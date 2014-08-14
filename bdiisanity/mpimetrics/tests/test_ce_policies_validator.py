import mock
import string
import random
import unittest

import mpimetrics.core as core
import mpimetrics.tests.fixtures as fixtures


class MockBDIIFetcher():
    def __init__(self, config):
        pass

    def get_srte_site(self, site):
        return fixtures.subcluster_rte, 'mock-site'

    def get_srte_ce(self, ce):
        return fixtures.subcluster_rte

    def get_pcy_ce(self, ce):
        return fixtures.policies

    def get_pcy_cluster(self, cluster):
        pcy_dict = {core.GLUE_CEID: 'ceid'}
        pcy_dict.update(fixtures.policies)
        return [
            ['ce1', pcy_dict],
            ['ce2', pcy_dict] 
        ] 

class TestPolicyValidator(unittest.TestCase):
    def test_policy_value_getter(self):
        validator = core.MpiPolicyValidator({})
        policies = {'a': [0]}
        self.assertEquals(validator.get_policy_value(policies, 'a'), 0)
        self.assertEquals(validator.code, core.NAGIOS_OK)

    def test_policy_value_non_existant(self):
        validator = core.MpiPolicyValidator({})
        policies = {'a': [0]}
        self.assertEquals(validator.get_policy_value(policies, 'b'), None)
        self.assertEquals(validator.code, core.NAGIOS_CRIT)

    def test_policy_value_non_integer(self):
        validator = core.MpiPolicyValidator({})
        policies = {'a': ['foo']}
        self.assertEquals(validator.get_policy_value(policies, 'a'), None)
        self.assertEquals(validator.code, core.NAGIOS_CRIT)

    def test_correct_time_policies(self):
        validator = core.MpiPolicyValidator({})
        validator.validate_time_policies(1, 1)
        self.assertEquals(validator.code, core.NAGIOS_OK)

    def test_invalid_wc_time(self):
        validator = core.MpiPolicyValidator({})
        validator.validate_time_policies(0, 1)
        self.assertEquals(validator.code, core.NAGIOS_WARN)

    def test_invalid_cpu_time(self):
        validator = core.MpiPolicyValidator({})
        validator.validate_time_policies(1, 0)
        self.assertEquals(validator.code, core.NAGIOS_WARN)

    def test_invalid_cpu_and_wc_time(self):
        validator = core.MpiPolicyValidator({})
        validator.validate_time_policies(0, 0)
        self.assertEquals(validator.code, core.NAGIOS_WARN)

    def test_validate_slot_policies(self):
        validator = core.MpiPolicyValidator({})
        validator.validate_slots_policies(1234)
        self.assertEquals(validator.code, core.NAGIOS_OK)

    def test_validate_zero_slots(self):
        validator = core.MpiPolicyValidator({})
        validator.validate_slots_policies(0)
        self.assertEquals(validator.code, core.NAGIOS_WARN)

    def test_validate_one_slot(self):
        validator = core.MpiPolicyValidator({})
        validator.validate_slots_policies(1)
        self.assertEquals(validator.code, core.NAGIOS_WARN)

    def test_validate_error_slot(self):
        validator = core.MpiPolicyValidator({})
        validator.validate_slots_policies(core.BDII_ERROR)
        self.assertEquals(validator.code, core.NAGIOS_WARN)

    def test_validate_policies(self):
        validator = core.MpiPolicyValidator({})
        validator.validate_policies("fake", fixtures.policies)
        self.assertEquals(validator.code, core.NAGIOS_OK)

    def test_validate_flavor(self):
        validator = core.MpiPolicyValidator({})
        env = ['OPENMPI', 'OPENMPI-1.4']
        self.assertTrue(validator.validate_flavor_tags('OPENMPI', env))
        self.assertEquals(validator.code, core.NAGIOS_OK)

    def test_validate_flavor_no_version(self):
        validator = core.MpiPolicyValidator({})
        env = ['OPENMPI']
        self.assertTrue(validator.validate_flavor_tags('OPENMPI', env))
        self.assertEquals(validator.code, core.NAGIOS_WARN)

    def test_validate_flavor_only_version(self):
        validator = core.MpiPolicyValidator({})
        env = ['OPENMPI-1.4']
        self.assertFalse(validator.validate_flavor_tags('OPENMPI', env))
        self.assertEquals(validator.code, core.NAGIOS_OK)

    def test_validate_correct_mpi_env(self):
        validator = core.MpiPolicyValidator({'flavors': ['OPENMPI']})
        validator.validate_mpi_env(['OPENMPI', 'OPENMPI-1.4', 'MPI-START'])
        self.assertEquals(validator.code, core.NAGIOS_OK)

    def test_missing_mpi_start(self):
        validator = core.MpiPolicyValidator({'flavors': ['OPENMPI']})
        validator.validate_mpi_env(['OPENMPI', 'OPENMPI-1.4'])
        self.assertEquals(validator.code, core.NAGIOS_CRIT)

    def test_missing_flavor(self):
        validator = core.MpiPolicyValidator({'flavors': ['OPENMPI']})
        validator.validate_mpi_env(['MPI-START-1.4'])
        self.assertEquals(validator.code, core.NAGIOS_CRIT)

    def test_set_error(self):
        validator = core.MpiPolicyValidator({})
        msg = "".join([random.choice(string.letters) for i in xrange(15)])
        validator.set_error(msg)
        self.assertEquals(validator.code, core.NAGIOS_CRIT)
        self.assertIn(msg, validator.messages['error'])
        self.assertIn(msg, validator.messages['info'])

    def test_set_warning(self):
        validator = core.MpiPolicyValidator({})
        msg = "".join([random.choice(string.letters) for i in xrange(15)])
        validator.set_warning(msg)
        self.assertEquals(validator.code, core.NAGIOS_WARN)
        self.assertIn(msg, validator.messages['warning'])
        self.assertIn(msg, validator.messages['info'])

    def test_add_output(self):
        validator = core.MpiPolicyValidator({})
        msg = "".join([random.choice(string.letters) for i in xrange(15)])
        validator.add_output(msg)
        self.assertIn(msg, validator.messages['info'])

    @mock.patch('mpimetrics.core.BDIIFetcher', MockBDIIFetcher)
    def test_validate_site_ces(self):
        validator = core.MpiPolicyValidator({'flavors': ['OPENMPI']})
        code, msgs = validator.validate_site_ces('fake')  
        self.assertEqual(core.NAGIOS_OK, code)

    @mock.patch('mpimetrics.core.BDIIFetcher', MockBDIIFetcher)
    def test_validate_ce(self):
        validator = core.MpiPolicyValidator({'flavors': ['OPENMPI']})
        code, msgs = validator.validate_ce('fake')  
        self.assertEqual(core.NAGIOS_OK, code)
         
