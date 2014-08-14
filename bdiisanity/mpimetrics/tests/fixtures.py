# minimal ldap information for testing
# took from real ldap queries

vo = 'mpi1'

bdii_base = 'o=grid'

ce_hostname = 'fakece.site.org'
ce_id = '%s:8443/cream-sge-mpi' % ce_hostname
ce_dn = 'GlueCEUniqueID=%s,Mds-Vo-name=SITE,Mds-Vo-name=local,o=grid' % ce_id

ce2_hostname = 'fakece2.site.org'
ce2_id = '%s:8443/cream-sge-mpi' % ce2_hostname
ce2_dn = 'GlueCEUniqueID=%s,Mds-Vo-name=SITE,Mds-Vo-name=local,o=grid' % ce2_id

cluster_id = 'CLUSTER-ID'
cluster_dn = ('GlueClusterUniqueID=%s,Mds-Vo-name=SITE,Mds-Vo-name=local,'
              'o=grid') % cluster_id
subcluster_id = 'SUBCLUSTER-ID'
subcluster_dn = 'GlueSubClusterUniqueID=%s,%s' % (subcluster_id, cluster_dn)
subcluster_rte = [
    'MPI-START',
    'OPENMPI',
    'OPENMPI-1.4',
    'OPENMPI-1.4.4',
    'OPENMPI-1.4.4-GCC',
]
site_id = 'SITE'


policies = {
    'GlueCEPolicyMaxCPUTime': ['41328'],
    'GlueCEPolicyMaxWallClockTime': ['10080'],
    'GlueCEPolicyMaxSlotsPerJob': ['500'],
    'GlueCEPolicyMaxTotalJobs': ['999999999'],
    'GlueCEPolicyMaxRunningJobs': ['0'],
}

directory = {
    bdii_base: {'o': 'grid'},
    ce_dn: {
        'objectClass': ['GlueCETop', 'GlueCE', 'GlueCEAccessControlBase',
                        'GlueCEInfo', 'GlueCEPolicy', 'GlueCEState',
                        'GlueInformationService', 'GlueKey',
                        'GlueSchemaVersion'],
        'GlueCEInfoHostName': [ce_hostname],
        'GlueCEUniqueID': [ce_id],
        'GlueCEAccessControlBaseRule': ['VO:%s' % vo,
                                        'VOMS:/%s/Role=other' % vo],
        'GlueForeignKey': ['GlueClusterUniqueID=%s' % cluster_id],
    },
    ce2_dn: {
        'objectClass': ['GlueCETop', 'GlueCE', 'GlueCEAccessControlBase',
                        'GlueCEInfo', 'GlueCEPolicy', 'GlueCEState',
                        'GlueInformationService', 'GlueKey',
                        'GlueSchemaVersion'],
        'GlueCEInfoHostName': [ce2_hostname],
        'GlueCEUniqueID': [ce2_id],
        'GlueCEAccessControlBaseRule': ['VO:%s' % vo,
                                        'VOMS:/%s/Role=other' % vo],
        'GlueForeignKey': ['GlueClusterUniqueID=%s' % cluster_id],
    },
    subcluster_dn: {
        'objectClass': ['GlueClusterTop', 'GlueSubCluster',
                        'GlueHostArchitecture', 'GlueHostApplicationSoftware',
                        'GlueHostBenchmark', 'GlueHostMainMemory',
                        'GlueHostNetworkAdapter', 'GlueHostOperatingSystem',
                        'GlueHostProcessor', 'GlueInformationService',
                        'GlueKey', 'GlueSchemaVersion'],
        'GlueChunkKey': ['GlueClusterUniqueID=%s' % cluster_id],
        'GlueHostApplicationSoftwareRunTimeEnvironment': subcluster_rte,
    },
    cluster_dn: {
        'objectClass': ['GlueClusterTop', 'GlueCluster',
                        'GlueInformationService', 'GlueKey',
                        'GlueSchemaVersion'],
        'GlueClusterUniqueID': [cluster_id],
        'GlueForeignKey': ['GlueSiteUniqueID=%s' % site_id],
    },
}

directory[ce_dn].update(policies)
directory[ce2_dn].update(policies)

gocdb_query_output = '''<?xml version="1.0" encoding="UTF-8"?>
<results>
<SITE ID="156" PRIMARY_KEY="247G0" NAME="IFCA-LCG2" COUNTRY="Spain"
 COUNTRY_CODE="ES" ROC="NGI_IBERGRID" SUBGRID=""
 GIIS_URL="ldap://gridiis01.ifca.es:2170/mds-vo-name=IFCA-LCG2,o=grid"/>

<SITE ID="41" PRIMARY_KEY="201G0" NAME="IISAS-Bratislava"
 COUNTRY="Slovakia" COUNTRY_CODE="SK" ROC="NGI_SK" SUBGRID=""
 GIIS_URL="ldap://sbdii.ui.savba.sk:2170/Mds-Vo-name=IISAS-Bratislava,o=grid"/>
</results>
'''

gocdb_sites = ['IISAS-Bratislava', 'IFCA-LCG2']
