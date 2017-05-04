# --*-- coding:utf-8 --*--

import glob
import unittest

from ziyan.utils.util import get_conf


class TestConfig(unittest.TestCase):
    """
    unittest for configuration file
    """
    def setUp(self):
        self.all_conf = dict()
        for conf in glob.glob('conf/*.toml'):
            self.all_conf.update(get_conf(conf))

    def test_console_output(self):
        self.assertFalse(self.all_conf['log_configuration']['console'], 'Change the terminal to false, please')


if __name__ == '__main__':
    unittest.main()
