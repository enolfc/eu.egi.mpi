# minimal ldap information for testing
# took from real ldap queries

vo = 'mpi1'

bdii_base = 'o=grid'

ce_hostname = 'fakece.site.org'
ce_id = '%s:8443/cream-sge-mpi' % ce_hostname
ce_dn = 'GlueCEUniqueID=%s,Mds-Vo-name=SITE,Mds-Vo-name=local,o=grid' % ce_id

cluster_id = 'CLUSTER-ID'
cluster_dn = ('GlueSubClusterUniqueID=%s,GlueClusterUniqueID=%s,'
              'Mds-Vo-name=SITE,Mds-Vo-name=local,o=grid') % (cluster_id,
                                                              cluster_id)
cluster_rte = [
    'MPI-START',
    'OPENMPI',
    'OPENMPI-1.4',
    'OPENMPI-1.4.4',
    'OPENMPI-1.4.4-GCC',
]

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
    cluster_dn: {
        'objectClass': ['GlueClusterTop', 'GlueSubCluster',
                        'GlueHostArchitecture', 'GlueHostApplicationSoftware',
                        'GlueHostBenchmark', 'GlueHostMainMemory',
                        'GlueHostNetworkAdapter', 'GlueHostOperatingSystem',
                        'GlueHostProcessor', 'GlueInformationService',
                        'GlueKey', 'GlueSchemaVersion'],
        'GlueChunkKey': ['GlueClusterUniqueID=%s' % cluster_id],
        'GlueHostApplicationSoftwareRunTimeEnvironment': cluster_rte,
    }
}

directory[ce_dn].update(policies)
