from itertools import chain, combinations
from mock import patch
import optparse
import os
import sys
import unittest

import mpimetrics.shell as shell
import mpimetrics.core as core


class MockValidator:
    def __init__(self, config):
        self.code = 0
        self.messages = {}
        pass

    def validate_site_ces(self, site):
        return self.code, self.messages

    def validate_ce(self, ce):
        return self.code, self.messages


class FailingMockValidator(MockValidator):
    def validate_site_ces(self, site):
        raise core.MpiMetricsException('boom')

    def validate_ce(self, ce):
        raise core.MpiMetricsException('boom')


class TestShell(unittest.TestCase):
    def setUp(self):
        self.argv = sys.argv

    def tearDown(self):
        sys.argv = self.argv

    def system_exit(self, code, f, *args):
        try:
            f(*args)
        except SystemExit, e:
            self.assertEquals(type(e), type(SystemExit()))
            self.assertEquals(e.code, code)
        else:
            self.fail('SystemExit was expected...')

    def test_default_bdii_url(self):
        if 'LCG_GFAL_INFOSYS' in os.environ:
            del os.environ['LCG_GFAL_INFOSYS']
        self.assertEquals(shell.default_bdii_url, shell.get_bdii_url(None))

    def test_passed_bdii_url(self):
        self.assertEquals('ldap://foo', shell.get_bdii_url('foo'))

    def test_environ_single_bdii_url(self):
        os.environ['LCG_GFAL_INFOSYS'] = 'foo'
        self.assertEquals('ldap://foo', shell.get_bdii_url('foo'))

    def test_environ_multiple_bdii_url(self):
        os.environ['LCG_GFAL_INFOSYS'] = 'foo,bar'
        self.assertEquals('ldap://foo', shell.get_bdii_url('foo'))

    def test_default_values(self):
        sys.argv = ['foo', '-a']
        cfg = shell.opt_parse()
        self.assertTrue(cfg['all'])
        self.assertEquals('ops', cfg['vo'])
        self.assertEquals('ldap://topbdii.core.ibergrid.eu:2170',
                          cfg['bdii_url'])
        self.assertEquals('https://goc.egi.eu/gocdbpi', cfg['gocdb_url'])
        self.assertEquals('o=grid', cfg['bdii_base'])
        self.assertEquals(30.0, cfg['timeout'])
        self.assertItemsEqual(['MPICH', 'MPICH2', 'OPENMPI'], cfg['flavors'])
        self.assertIsNone(cfg['ce'])
        self.assertIsNone(cfg['site'])

    @patch.object(optparse.OptionParser, 'error')
    def test_missing_check_type(self, mock_method):
        sys.argv = ['foo']
        shell.opt_parse()
        self.assertTrue(mock_method.called)

    @patch.object(optparse.OptionParser, 'error')
    def test_multiple_check_type(self, mock_method):
        check_types = (('-a', ), ('-H', 'bar'), ('-S', 'baz'))
        for i in combinations(check_types, 2):
            sys.argv = list(chain(['foo'], *i))
            shell.opt_parse()
            self.assertTrue(mock_method.called)
        sys.argv = list(chain(['foo'], *check_types))
        shell.opt_parse()
        self.assertTrue(mock_method.called)

    @patch('mpimetrics.core.MpiPolicyValidator', MockValidator)
    def test_check_ce(self):
        self.assertEquals((0, {}), shell.check_ce({'ce': 'foo'}))

    @patch('mpimetrics.core.MpiPolicyValidator', FailingMockValidator)
    def test_failing_check_ce(self):
        self.system_exit(core.NAGIOS_UNK, shell.check_ce, {'ce': 'foo'})

    @patch('mpimetrics.core.MpiPolicyValidator', MockValidator)
    def test_check_site(self):
        self.assertEquals((0, {}), shell.check_site_ces({'site': 'foo'}))

    @patch('mpimetrics.core.MpiPolicyValidator', FailingMockValidator)
    def test_failing_check_site(self):
        try:
            shell.check_site_ces({'site': 'foo'})
        except SystemExit, e:
            self.assertEquals(type(e), type(SystemExit()))
            self.assertEquals(e.code, core.NAGIOS_UNK)
        else:
            self.fail('SystemExit was expected...')

    @patch.object(core.GocDBGetter, 'get_sites')
    @patch('mpimetrics.core.MpiPolicyValidator', MockValidator)
    def test_check_all_sites(self, mock_getter):
        mock_getter.return_value = ['site1', 'site2']
        self.assertEquals((0, {}), shell.check_all_sites({}))

    @patch.object(core.GocDBGetter, 'get_sites')
    @patch('mpimetrics.core.MpiPolicyValidator', FailingMockValidator)
    def test_failing_check_all_sites(self, mock_getter):
        mock_getter.return_value = ['site1', 'site2']
        self.assertEquals((0, {}), shell.check_all_sites({}))

    @patch('mpimetrics.shell.check_all_sites')
    @patch('mpimetrics.shell.opt_parse')
    def test_main_all(self, mock_parse, mock_check):
        mock_parse.return_value = {'all': True, 'flavors': [],
                                   'site': None, 'ce': None}
        mock_check.return_value = (core.NAGIOS_OK,  {'error': '',
                                                     'warning': '',
                                                     'info': ['']})
        self.system_exit(core.NAGIOS_OK, shell.main)

    @patch('mpimetrics.shell.check_site_ces')
    @patch('mpimetrics.shell.opt_parse')
    def test_main_site(self, mock_parse, mock_check):
        mock_parse.return_value = {'all': False, 'flavors': [],
                                   'site': 'foo', 'ce': None}
        mock_check.return_value = (core.NAGIOS_OK,  {'error': '',
                                                     'warning': '',
                                                     'info': ['']})
        self.system_exit(core.NAGIOS_OK, shell.main)

    @patch('mpimetrics.shell.check_ce')
    @patch('mpimetrics.shell.opt_parse')
    def test_main_ce(self, mock_parse, mock_check):
        mock_parse.return_value = {'all': False, 'flavors': [],
                                   'site': None, 'ce': 'foo'}
        mock_check.return_value = (core.NAGIOS_OK,  {'error': '',
                                                     'warning': '',
                                                     'info': ['']})
        self.system_exit(core.NAGIOS_OK, shell.main)

    @patch('mpimetrics.shell.check_ce')
    @patch('mpimetrics.shell.opt_parse')
    def test_main_ce_critical(self, mock_parse, mock_check):
        mock_parse.return_value = {'all': False, 'flavors': [],
                                   'site': None, 'ce': 'foo'}
        mock_check.return_value = (core.NAGIOS_CRIT, {'error': '',
                                                      'warning': '',
                                                      'info': ['']})
        self.system_exit(core.NAGIOS_CRIT, shell.main)

    @patch('mpimetrics.shell.check_ce')
    @patch('mpimetrics.shell.opt_parse')
    def test_main_ce_warning(self, mock_parse, mock_check):
        mock_parse.return_value = {'all': False, 'flavors': [],
                                   'site': None, 'ce': 'foo'}
        mock_check.return_value = (core.NAGIOS_WARN, {'error': '',
                                                      'warning': '',
                                                      'info': ['']})
        self.system_exit(core.NAGIOS_WARN, shell.main)
