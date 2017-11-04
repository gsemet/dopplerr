# coding: utf-8

from unittest import TestCase

from cfgtree.dictxpath import delete_node_by_xpath
from cfgtree.dictxpath import get_node_by_xpath
from cfgtree.dictxpath import set_node_by_xpath


class DictXpathTests(TestCase):
    def test_get_node_by_path(self):
        mapping = {'level1': {'level2': {'level3': 42}}}
        expected = 42
        actual = get_node_by_xpath(mapping, 'level1.level2.level3')
        self.assertEqual(expected, actual)
        self.assertRaisesRegex(
            KeyError, (r"Invalid 'level1.unknown' selector: 'unknown' doesn't match anything. "
                       r"Available keys: \['level2'\]"), get_node_by_xpath, mapping,
            'level1.unknown')
        actual = get_node_by_xpath(
            mapping, 'level1.unknown', default="default value", ignore_errors=True)
        self.assertEqual(actual, "default value")

    def test_get_node_by_path_empty_mapping(self):
        empty_map = {}
        self.assertRaises(KeyError, get_node_by_xpath, empty_map, 'level1')
        self.assertRaises(KeyError, get_node_by_xpath, empty_map, 'level1.other')
        self.assertEqual(
            get_node_by_xpath(empty_map, 'level1', default="default value", ignore_errors=True),
            "default value")
        self.assertEqual(
            get_node_by_xpath(empty_map, '', default="default value", ignore_errors=True),
            "default value")

    def test_get_node_by_path_invalid_first_level(self):
        mapping = {"level1": {}}
        self.assertRaises(KeyError, get_node_by_xpath, mapping, 'invalid_level1')
        self.assertEqual(
            get_node_by_xpath(
                mapping, 'invalid_level1', default="default value", ignore_errors=True),
            "default value")

    def test_get_node_by_path_mapping_not_dict(self):
        mapping_no_a_dict = "simple string!"
        self.assertEqual(
            get_node_by_xpath(mapping_no_a_dict, '', default="default value", ignore_errors=True),
            "default value")
        self.assertRaises(
            KeyError,
            get_node_by_xpath,
            mapping_no_a_dict,
            'level1.unknown',
            ignore_errors=False,
        )

    def test_get_node_by_path_incomplete_mapping(self):
        mapping = {'level1': {'level2': {}}}
        self.assertRaises(KeyError, get_node_by_xpath, mapping, 'level1.level2.level3')
        self.assertRaises(KeyError, get_node_by_xpath, mapping, 'level1.unknown')
        # test with tailing "." at the end of path
        self.assertRaises(KeyError, get_node_by_xpath, mapping, 'level1.')
        self.assertEqual(
            get_node_by_xpath(
                mapping, 'level1.level2', default="default value", ignore_errors=True), {})
        self.assertEqual(
            get_node_by_xpath(
                mapping, 'level1.unknown', default="default value", ignore_errors=True),
            "default value")
        # test with tailing "." at the end of path
        self.assertEqual(
            get_node_by_xpath(mapping, 'level1.', default="default value", ignore_errors=True),
            "default value")

    def test_set_node_by_path(self):
        mapping = {'level1': {'level2': {'level3': None}}}
        expected = 42
        set_node_by_xpath(mapping, 'level1.level2.level3', expected)
        actual = get_node_by_xpath(mapping, 'level1.level2.level3')
        self.assertEqual(expected, actual)
        set_node_by_xpath(mapping, 'level1.unknown', expected)
        actual = get_node_by_xpath(mapping, 'level1.unknown')
        self.assertEqual(expected, actual)
        self.assertRaises(KeyError, set_node_by_xpath, mapping, 'level1.invalid.level3', '')
        expected = 'extended'
        set_node_by_xpath(mapping, 'level1.missing.level3', expected, extend=True)
        actual = get_node_by_xpath(mapping, 'level1.missing.level3')
        self.assertEqual(expected, actual)

    def test_delete_node_by_path(self):
        mapping = {'level1': {'level2': {'level3': 42}}}
        expected = 42
        actual = delete_node_by_xpath(mapping, 'level1.level2.level3')
        self.assertEqual(expected, actual)
        self.assertFalse('level3' in mapping['level1']['level2'])
        self.assertRaises(KeyError, delete_node_by_xpath, mapping, 'level1.invalid.level3')
        self.assertIsNone(
            delete_node_by_xpath(mapping, 'level1.invalid.level3', ignore_errors=True))

    def test_get_node_by_path_with_list_selector(self):
        mapping = {'level1': {'level_2_is_a_list': ['item1', 'item2']}}
        actual = get_node_by_xpath(
            mapping, 'level1.level_2_is_a_list[1]', handle_list_selector=True)
        self.assertEqual('item2', actual)

    def test_get_node_w_lst_selctr_sub_list(self):
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
        actual = get_node_by_xpath(
            mapping, 'level1.level_2_is_a_list[1].item2.k2', handle_list_selector=True)
        self.assertEqual('v2', actual)

    def test_get_w_bad_lst_selctr_n_default_val(self):
        mapping = {'level1': {'level_2_is_a_list': ['item1', 'item2']}}
        actual = get_node_by_xpath(
            mapping, 'level1.level_2_is_a_list[1]', handle_list_selector=True, default="N/A")
        self.assertEqual('item2', actual)
        self.assertRaisesRegex(
            KeyError,
            (r"Invalid \'level1.level_2_is_a_list\[99\]\' selector: "
             r"item index \'99\' of \'level_2_is_a_list\' is outside of the list boundaries. "
             r"Length is: 2"),
            get_node_by_xpath,
            mapping,
            'level1.level_2_is_a_list[99]',
            handle_list_selector=True,
            default="N/A")
