from mock import patch
from StringIO import StringIO
import unittest

import mpimetrics.core as core
import mpimetrics.tests.fixtures as fixtures


class TestGocDBQuery(unittest.TestCase):
    def setUp(self):
        self.gocdb_url = 'https://goc.egi.eu/gocdbp'
        self.getter = core.GocDBGetter({'gocdb_url': self.gocdb_url})

    @patch('mpimetrics.core.urlopen')
    def test_gocdb_url(self, mock_urlopen):
        mock_urlopen.return_value = 1234
        self.assertEquals(1234, self.getter.query_gocdb())
        mock_urlopen.assert_called_with(self.gocdb_url + core.GOCDB_METHOD)

    @patch('mpimetrics.core.urlopen')
    def test_gocdb_parser(self, mock_urlopen):
        mock_urlopen.return_value = StringIO(fixtures.gocdb_query_output)
        self.assertItemsEqual(fixtures.gocdb_sites, self.getter.get_sites())
        mock_urlopen.assert_called_with(self.gocdb_url + core.GOCDB_METHOD)
