# Copyright 2014 Spanish National Research Council
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#

import ldap
import logging
import re
from urllib2 import urlopen
from xml.dom.minidom import parse


# nagios exit codes
NAGIOS_OK = 0
NAGIOS_WARN = 1
NAGIOS_CRIT = 2
NAGIOS_UNK = 3

# Some LONG Strings
GOCDB_METHOD = ("/public/?method=get_site_list&certification_status"
                "=Certified&production_status=Production")
# GlueSchema fields
GLUE_CEID = 'GlueCEUniqueID'
GLUE_RTE = 'GlueHostApplicationSoftwareRunTimeEnvironment'
GLUE_MAX_CPUT = 'GlueCEPolicyMaxCPUTime'
GLUE_MAX_SLOTS = 'GlueCEPolicyMaxSlotsPerJob'
GLUE_MAX_WALLT = 'GlueCEPolicyMaxWallClockTime'
GLUE_MAX_RUNJOBS = 'GlueCEPolicyMaxRunningJobs'
GLUE_MAX_TOTALJOBS = 'GlueCEPolicyMaxTotalJobs'

BDII_ERROR = 999999999


class MpiMetricsException(Exception):
    """
    Base exception for errors during the execution of the probe.
    """
    pass


class GocDBGetter:
    def __init__(self, config):
        self.config = config

    def get_sites(self):
        logging.debug('Connecting to %s to fetch site list',
                      ''.join((self.config['gocdb_url'], GOCDB_METHOD)))
        f = urlopen(self.config['gocdb_url'] + GOCDB_METHOD)   # , timeout=15)
        d = parse(f)
        return [s.getAttribute('NAME') for s in d.getElementsByTagName('SITE')]


class BDIIFetcher:
    def __init__(self, config):
        self.config = config

    def ldap_init(self):
        try:
            l = ldap.initialize(self.config['bdii_url'])
            l.set_option(ldap.OPT_NETWORK_TIMEOUT,
                         self.config.get('timeout', -1))
            return l
        except ldap.LDAPError, e:
            raise MpiMetricsException("Error when trying to connect to %s: %s"
                                      % (self.config['bdii_url'], e))

    def get_srte_ce(self, ce):
        l = self.ldap_init()
        str_args = {'ce': ce, 'vo': self.config['vo']}
        f = ('(&(&(objectClass=GlueCE)(GlueCEInfoHostName=%(ce)s))'
             '(|(GlueCEAccessControlBaseRule=VO:%(vo)s)'
             '(GlueCEAccessControlBaseRule=VOMS:/%(vo)s/*)))') % str_args
        entries = l.search_s(self.config['bdii_base'], ldap.SCOPE_SUBTREE, f,
                             ['GlueForeignKey'])
        if not entries:
            raise MpiMetricsException('Unable to get site name for %s' % ce)
        # assume the first entry is good if we have more than one CE
        site = [e for e in entries[0][1]['GlueForeignKey']
                if e.find('GlueClusterUniqueID') == 0][0]
        if not site:
            raise MpiMetricsException('Unable to get site name for %s' % ce)
        # search
        entries = l.search_s(self.config['bdii_base'], ldap.SCOPE_SUBTREE,
                             '(&(objectClass=GlueSubCluster)'
                             '(GlueChunkKey=%s))' % site, [GLUE_RTE])
        if not entries:
            raise MpiMetricsException('Unable to get cluster info for site %s'
                                      % site)
        return entries[0][1][GLUE_RTE]

    def get_pcy_ce(self, ce):
        l = self.ldap_init()
        str_args = {'ce': ce, 'vo': self.config['vo']}
        f = ('(&(&(objectClass=GlueCE)(GlueCEInfoHostName=%(ce)s))'
             '(|(GlueCEAccessControlBaseRule=VO:%(vo)s)'
             '(GlueCEAccessControlBaseRule=VOMS:/%(vo)s/*)))') % str_args
        r = l.search_s(self.config['bdii_base'], ldap.SCOPE_SUBTREE, f,
                       [GLUE_MAX_RUNJOBS, GLUE_MAX_TOTALJOBS, GLUE_MAX_SLOTS,
                        GLUE_MAX_WALLT, GLUE_MAX_CPUT])
        if not r:
            raise MpiMetricsException('Unable to get policy info for %s' % ce)
        return r[0][1]

    def get_srte_site(self, site):
        l = self.ldap_init()
        entries = l.search_s(self.config['bdii_base'], ldap.SCOPE_SUBTREE,
                             ('(&(objectclass=GlueCluster)'
                              '(GlueForeignKey=GlueSiteUniqueID=%s))') % site,
                             ['GlueClusterUniqueID'])
        if not entries:
            raise MpiMetricsException('Unable to get Cluster IDs for site %s'
                                      % site)
        for e in entries:
            cluster_id = e[1]['GlueClusterUniqueID'][0]
        r = l.search_s(self.config['bdii_base'], ldap.SCOPE_SUBTREE,
                       ('(&(objectclass=GlueSubCluster)'
                        '(GlueChunkKey=GlueClusterUniqueID=%s))') % cluster_id,
                       [GLUE_RTE])
        if not r:
            raise MpiMetricsException('Unable to get RTE info for site %s'
                                      % site)
        return r[0][1][GLUE_RTE], cluster_id

    def get_pcy_cluster(self, cluster):
        l = self.ldap_init()
        str_args = {'cluster': cluster, 'vo': self.config['vo']}
        f = ('(&(&(objectClass=GlueCE)'
             '(GlueForeignKey=GlueClusterUniqueID=%(cluster)s))'
             '(|(GlueCEAccessControlBaseRule=VO:%(vo)s)'
             '(GlueCEAccessControlBaseRule=VOMS:/%(vo)s/*)))') % str_args
        r = l.search_s(self.config['bdii_base'], ldap.SCOPE_SUBTREE, f,
                       [GLUE_MAX_RUNJOBS, GLUE_MAX_TOTALJOBS, GLUE_MAX_SLOTS,
                        GLUE_MAX_WALLT, GLUE_MAX_CPUT, GLUE_CEID])
        if not r:
            raise MpiMetricsException('Unable to get policy info for %s'
                                      % cluster)
        return r


class MpiPolicyValidator:
    def __init__(self, config):
        self.config = config
        self.messages = {'error': '', 'warning': '', 'info': []}
        self.code = NAGIOS_OK
        self.bdii_fetcher = BDIIFetcher(config)

    def set_error(self, error_msg):
        logging.debug("NAGIOS ERROR: %s", error_msg)
        self.messages['error'] = error_msg
        self.code = NAGIOS_CRIT
        self.add_output(error_msg)

    def set_warning(self, warn_msg):
        logging.debug("NAGIOS WARNING: %s", warn_msg)
        self.messages['warning'] = warn_msg
        self.code = NAGIOS_WARN
        self.add_output(warn_msg)

    def add_output(self, msg):
        self.messages['info'].append(msg)

    def validate_flavor_tags(self, flv, env):
        flavor_name = False
        flavor_version = False
        r = re.compile('^%s(-\S+)?$' % flv)
        tags = []
        for e in env:
            res = r.match(e)
            if res:
                if res.groups()[0]:
                    flavor_version = True
                    tags.append(e)
                else:
                    flavor_name = True
                    tags.append(e)
        if tags:
            self.add_output('Found tags %s for flavor %s'
                            % (', '.join(tags), flv))
        if flavor_name and not flavor_version:
            self.set_warning('Does not publish %s version' % flv)
        return flavor_name

    def get_policy_value(self, policies, pcy):
        logging.debug("Checking policy %s", pcy)
        try:
            v = int(policies[pcy][0])
            logging.debug("Found value %d", v)
            self.add_output('Found value %d for policy %s' % (v, pcy))
            return v
        except KeyError:
            self.set_error('does not publish %s' % pcy)
        except ValueError:
            self.set_error('publishes non integer value for %s (%s)'
                           % (pcy, policies[pcy][0]))
        return None

    def validate_time_policies(self, max_wc_time, max_cpu_time):
        if max_wc_time == 0:
            self.set_warning('Publishes an incorrect value for %s (%d)'
                             % (GLUE_MAX_WALLT, max_wc_time))
        if max_cpu_time == 0:
            self.set_warning('Publishes an incorrect value for %s (%d)'
                             % (GLUE_MAX_CPUT, max_cpu_time))

    def validate_slots_policies(self, max_slots):
        if max_slots == 0 or max_slots == 1 or max_slots == BDII_ERROR:
            self.set_warning('Publishes an incorrect value for %s (%d)' %
                             (GLUE_MAX_SLOTS, max_slots))

    def validate_policies(self, ce, policies):
        logging.debug("Checking policies for %s", ce)
        max_wc_time = self.get_policy_value(policies, GLUE_MAX_WALLT)
        max_cpu_time = self.get_policy_value(policies, GLUE_MAX_CPUT)
        max_slots = self.get_policy_value(policies, GLUE_MAX_SLOTS)
        self.validate_time_policies(max_wc_time, max_cpu_time)
        self.validate_slots_policies(max_slots)

    def validate_mpi_env(self, env):
        has_flavors = False
        for flv in self.config.get('flavors', []):
            has_flavors |= self.validate_flavor_tags(flv, env)
        mpi_start_tags = [m for m in env if m.find('MPI-START') == 0]
        if not mpi_start_tags:
            self.set_error('Does not publish MPI-START tag!')
        else:
            self.add_output('Found tag %s for MPI-START'
                            % ', '.join(mpi_start_tags))
        if not has_flavors:
            self.set_error('Does not publish any MPI flavors!')

    def validate_ce(self, ce):
        logging.debug("Checking CE %s", ce)
        self.validate_mpi_env(self.bdii_fetcher.get_srte_ce(ce))
        self.validate_policies(ce, self.bdii_fetcher.get_pcy_ce(ce))
        return self.code, self.messages

    def validate_site_ces(self, site):
        logging.debug("Checking SITE %s", site)
        srte, cluster = self.bdii_fetcher.get_srte_site(site)
        self.validate_mpi_env(srte)
        cluster_pcy = self.bdii_fetcher.get_pcy_cluster(cluster)
        for ce in cluster_pcy:
            self.validate_policies(ce, ce[1])
        return self.code, self.messages
