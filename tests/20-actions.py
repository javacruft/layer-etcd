#!/usr/bin/env python3

import amulet
import unittest
import re


class TestActions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = amulet.Deployment(series='xenial')
        cls.d.add('etcd')
        cls.d.add('easyrsa', 'cs:~containers/easyrsa')
        cls.d.configure('etcd', {'channel': '3.0/stable'})
        cls.d.relate('easyrsa:client', 'etcd:certificates')
        cls.d.setup(timeout=1200)
        cls.d.sentry.wait_for_messages({'etcd':
                                        re.compile('Healthy*|Unhealthy*')})
        # cls.d.sentry.wait()
        cls.etcd = cls.d.sentry['etcd']

    def test_snapshot_restore(self):
        """
        Trigger snapshot and restore actions
        """
        action_id = self.etcd[0].run_action('snapshot')
        outcome = self.d.action_fetch(action_id,
                                      timeout=7200,
                                      raise_on_timeout=True,
                                      full_output=True)
        self.assertEqual(outcome['status'], 'completed')
        action_id = self.etcd[0].run_action('restore')
        outcome = self.d.action_fetch(action_id,
                                      timeout=7200,
                                      raise_on_timeout=True,
                                      full_output=True)
        self.assertEqual(outcome['status'], 'completed')


if __name__ == '__main__':
    unittest.main()