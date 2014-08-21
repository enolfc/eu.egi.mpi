from mock import patch
import os
import unittest

import mpimetrics.shell as shell


class TestShell(unittest.TestCase):
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

    @patch('sys.argv', ['mock', '-a'])
    def test_default_values(self):
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

    @patch('sys.argv', ['mock'])
    @patch('optparse.OptionParser')
    def test_missing_check_type(self, mock_parser):
        self.assertRaises(SystemExit, shell.opt_parse())
