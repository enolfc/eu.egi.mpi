import unittest

import mpimetrics.core as core
import mpimetrics.tests.fixtures as fixtures

from mockldap import MockLdap
import ldap


class TestBdiiQuery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_ldap = MockLdap(fixtures.directory)

    def setUp(self):
        self.config = {
            'bdii_base': fixtures.bdii_base,
            'bdii_url': 'ldap://localhost/',
            'vo': fixtures.vo,
        }
        self.mock_ldap.start()
        ldapobj = self.mock_ldap['ldap://localhost/']
        # fix return value for the VO searches
        f = '(GlueCEInfoHostName=%s)' % fixtures.ce_hostname
        foreign_key = ldapobj.search_s(fixtures.bdii_base, ldap.SCOPE_SUBTREE,
                                       f, ['GlueForeignKey'])
        pcy = ldapobj.search_s(fixtures.bdii_base, ldap.SCOPE_SUBTREE, f,
                               [core.GLUE_MAX_RUNJOBS, core.GLUE_MAX_TOTALJOBS,
                                core.GLUE_MAX_SLOTS, core.GLUE_MAX_WALLT,
                                core.GLUE_MAX_CPUT])
        f = '(&(&(objectClass=GlueCE)'
        f += '(GlueCEInfoHostName=%s))' % fixtures.ce_hostname
        f += '(|(GlueCEAccessControlBaseRule=VO:%s)' % fixtures.vo
        f += '(GlueCEAccessControlBaseRule=VOMS:/%s/*)))' % fixtures.vo
        ldapobj.search_s.seed(fixtures.bdii_base, ldap.SCOPE_SUBTREE, f,
                              ['GlueForeignKey'])(foreign_key)
        ldapobj.search_s.seed(fixtures.bdii_base, ldap.SCOPE_SUBTREE, f,
                              [core.GLUE_MAX_RUNJOBS, core.GLUE_MAX_TOTALJOBS,
                               core.GLUE_MAX_SLOTS, core.GLUE_MAX_WALLT,
                               core.GLUE_MAX_CPUT])(pcy)

    def tearDown(self):
        self.mock_ldap.stop()

    def test_get_ce_srte(self):
        bdii_querier = core.BDIIFetcher(self.config)
        srte = bdii_querier.get_srte_ce(fixtures.ce_hostname)
        self.assertItemsEqual(srte, fixtures.cluster_rte)

    def test_get_ce_pcy(self):
        bdii_querier = core.BDIIFetcher(self.config)
        policies = bdii_querier.get_pcy_ce(fixtures.ce_hostname)
        self.assertEqual(policies, fixtures.policies)
