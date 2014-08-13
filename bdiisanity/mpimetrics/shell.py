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

#
# command line shell for the eu.egi.mpi bdii checks
#

import logging
import os
from optparse import OptionParser
import sys

import mpimetrics.core as core


def opt_parse():
    """
    Parses the command line options.
    """
    parser = OptionParser()
    parser.add_option('-v', '--verbose', dest='verbose',
                      help='be verbose', action='store_true', default=False)
    parser.add_option('-H', '--hostname', dest='hostname',
                      help='test host HOSTNAME', metavar='HOSTNAME')
    parser.add_option('-a', '--all', action='store_true', default=False,
                      help='Test all the sites in GOCDB', dest='all')
    parser.add_option('-V', '--vo', default='ops', dest='vo',
                      help='Test info for VO', metavar='VO')
    parser.add_option('-t', '--timeout', dest='timeout', default=30,
                      help='set timeout value to TIMEOUT', metavar='TIMEOUT')
    parser.add_option('-f', '--flavor', dest='flavors',
                      default=["MPICH", "MPICH2", "OPENMPI"],
                      help='test specific MPI flavor', metavar='FLAVOR',
                      action="append")
    parser.add_option('-b', '--bdii', dest='bdii_url',
                      help='use BDII_URL (<hostname>:<port>) for queries',
                      metavar='BDII_URL',)
    parser.add_option('-B', '--bdii-base', dest='bdii_base', default="o=grid",
                      help='use BDII_BASE for queries',
                      metavar='BDII_BASE',)
    parser.add_option('-g', '--gocdb', dest='gocdb_url',
                      default="https://goc.egi.eu/gocdbpi",
                      help='Use GOCDB_URL to query GOCDB (tests all CEs)',
                      metavar='GOCDB_URL',)
    (options, args) = parser.parse_args()
    if options.all and options.hostname:
        parser.error('-a and -H options cannot be used simultaneously')
    if not (options.all or options.hostname):
        parser.error('Specify -a or -H options')

    if options.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logging.basicConfig(datefmt="%c", level=log_level,
                        format="%(asctime)s %(levelname)s %(message)s")
    config = {
        'flavors': options.flavors,
        'gocdb_url': options.gocdb_url,
        'bdii_base': options.bdii_base,
        'timeout': options.timeout,
        'vo': options.vo,
        'ce': options.hostname,
        'all': options.all,
        # safe default for bdii_url
        'bdii_url': 'ldap://topbdii.core.ibergrid.eu:2170',
    }
    if options.bdii_url:
        config['bdii_url'] = 'ldap://%s' % options.bdii_url
    else:
        try:
            bdii = os.environ['LCG_GFAL_INFOSYS'].split(',')[0]
            config['bdii_url'] = 'ldap://%s' % (bdii)
        except KeyError:
            pass
    return config


def check_all_sites(config):
    """
    Queries GOCDB and goes through the list of sites.
    """
    validator = core.MpiPolicyValidator(config)
    logging.debug("Testing all sites in GOCDB")
    gocdb_getter = core.GocDBGetter(config)
    for site in gocdb_getter.get_sites():
        try:
            validator.validate_site_ces(site)
        except core.MpiMetricsException, e:
            logging.warning("Unknown error when checking site: %s ", e)
            logging.warning("Continuing execution")
    return validator.code, validator.messages


def check_ce(config):
    """
    Checks the configuration of a single CE.
    """
    logging.debug("Testing single CE")
    validator = core.MpiPolicyValidator(config)
    try:
        return validator.validate_ce(config['ce'])
    except core.MpiMetricsException, e:
        logging.error("Unknown error when checking site: %s", e)
        sys.exit(core.NAGIOS_UNK)


def main():
    config = opt_parse()
    logging.debug("Executing MPI BDII sanity check!")
    logging.debug("Will test %s flavors", ', '.join(config['flavors']))
    exit_code = core.NAGIOS_OK
    if config['all']:
        exit_code, msgs = check_all_sites(config)
    else:
        exit_code, msgs = check_ce(config)
    # make sure the order of the messages is the one expected
    # since only one line is shown in the nagios status
    if exit_code == core.NAGIOS_OK:
        print "MPI related BDII values OK!"
    elif exit_code == core.NAGIOS_CRIT:
        print msgs['error']
    elif exit_code == core.NAGIOS_WARN:
        print msgs['warning']
    for msg in msgs['info']:
        print msg
    sys.exit(exit_code)
