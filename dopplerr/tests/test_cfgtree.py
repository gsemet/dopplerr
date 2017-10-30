# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from txrwlock.txtestcase import TxTestCase

from dopplerr.cfgtree import deleteNodeByPath
from dopplerr.cfgtree import getNodeByPath
from dopplerr.cfgtree import setNodeByPath


class TreeTests(TxTestCase):
    def test_get_node_by_path(self):
        mapping = {'level1': {'level2': {'level3': 42}}}
        expected = 42
        actual = getNodeByPath(mapping, 'level1.level2.level3')
        self.assertEqual(expected, actual)
        self.assertRaisesWithMessage(
            KeyError, "Invalid 'level1.unknown' selector: 'unknown' doesn't match anything. "
            "Available keys: ['level2']", getNodeByPath, mapping, 'level1.unknown')
        actual = getNodeByPath(
            mapping, 'level1.unknown', default="default value", ignoreErrors=True)
        self.assertEqual(actual, "default value")

    def test_get_node_by_path_empty_mapping(self):
        empty_map = {}
        self.assertRaises(KeyError, getNodeByPath, empty_map, 'level1')
        self.assertRaises(KeyError, getNodeByPath, empty_map, 'level1.other')
        self.assertEqual(
            getNodeByPath(empty_map, 'level1', default="default value", ignoreErrors=True),
            "default value")
        self.assertEqual(
            getNodeByPath(empty_map, '', default="default value", ignoreErrors=True),
            "default value")

    def test_get_node_by_path_invalid_first_level(self):
        mapping = {"level1": {}}
        self.assertRaises(KeyError, getNodeByPath, mapping, 'invalid_level1')
        self.assertEqual(
            getNodeByPath(mapping, 'invalid_level1', default="default value", ignoreErrors=True),
            "default value")

    def test_get_node_by_path_mapping_not_dict(self):
        mapping_no_a_dict = "simple string!"
        self.assertEqual(
            getNodeByPath(mapping_no_a_dict, '', default="default value", ignoreErrors=True),
            "default value")
        self.assertRaises(
            KeyError,
            getNodeByPath,
            mapping_no_a_dict,
            'level1.unknown',
            ignoreErrors=False,
        )

    def test_get_node_by_path_incomplete_mapping(self):
        mapping = {'level1': {'level2': {}}}
        self.assertRaises(KeyError, getNodeByPath, mapping, 'level1.level2.level3')
        self.assertRaises(KeyError, getNodeByPath, mapping, 'level1.unknown')
        # test with tailing "." at the end of path
        self.assertRaises(KeyError, getNodeByPath, mapping, 'level1.')
        self.assertEqual(
            getNodeByPath(mapping, 'level1.level2', default="default value", ignoreErrors=True), {})
        self.assertEqual(
            getNodeByPath(mapping, 'level1.unknown', default="default value", ignoreErrors=True),
            "default value")
        # test with tailing "." at the end of path
        self.assertEqual(
            getNodeByPath(mapping, 'level1.', default="default value", ignoreErrors=True),
            "default value")

    def test_set_node_by_path(self):
        mapping = {'level1': {'level2': {'level3': None}}}
        expected = 42
        setNodeByPath(mapping, 'level1.level2.level3', expected)
        actual = getNodeByPath(mapping, 'level1.level2.level3')
        self.assertEqual(expected, actual)
        setNodeByPath(mapping, 'level1.unknown', expected)
        actual = getNodeByPath(mapping, 'level1.unknown')
        self.assertEqual(expected, actual)
        self.assertRaises(KeyError, setNodeByPath, mapping, 'level1.invalid.level3', '')
        expected = 'extended'
        setNodeByPath(mapping, 'level1.missing.level3', expected, extend=True)
        actual = getNodeByPath(mapping, 'level1.missing.level3')
        self.assertEqual(expected, actual)

    def test_delete_node_by_path(self):
        mapping = {'level1': {'level2': {'level3': 42}}}
        expected = 42
        actual = deleteNodeByPath(mapping, 'level1.level2.level3')
        self.assertEqual(expected, actual)
        self.assertFalse('level3' in mapping['level1']['level2'])
        self.assertRaises(KeyError, deleteNodeByPath, mapping, 'level1.invalid.level3')
        self.assertIsNone(deleteNodeByPath(mapping, 'level1.invalid.level3', ignoreErrors=True))

    def test_get_node_by_path_with_list_selector(self):
        mapping = {'level1': {'level_2_is_a_list': ['item1', 'item2']}}
        actual = getNodeByPath(mapping, 'level1.level_2_is_a_list[1]', handleListSelector=True)
        self.assertEqual('item2', actual)

    def test_get_node_by_path_with_list_selector_sub_list(self):
        mapping = {
            'level1': {
                'level_2_is_a_list': [
                    {
                        'item1': {
                            'k1': 'v1'
                        }
                    },
                    {
                        'item2': {
                            'k2': 'v2'
                        }
                    },
                ]
            }
        }
        actual = getNodeByPath(
            mapping, 'level1.level_2_is_a_list[1].item2.k2', handleListSelector=True)
        self.assertEqual('v2', actual)

    def test_get_node_by_path_with_bas_list_selector_and_default_value(self):
        mapping = {'level1': {'level_2_is_a_list': ['item1', 'item2']}}
        actual = getNodeByPath(
            mapping, 'level1.level_2_is_a_list[1]', handleListSelector=True, default="N/A")
        self.assertEqual('item2', actual)
        self.assertRaisesWithMessage(
            KeyError,
            "Invalid \'level1.level_2_is_a_list[99]\' selector: "
            "item index \'99\' of \'level_2_is_a_list\' is outside of the list boundaries. "
            "Length is: 2",
            getNodeByPath,
            mapping,
            'level1.level_2_is_a_list[99]',
            handleListSelector=True,
            default="N/A")
