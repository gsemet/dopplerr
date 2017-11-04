# coding: utf-8

import re

# tells flake8 to ignore complexity check for this file
# flake8: noqa


def get_node_by_xpath(mapping, xpath, default=None, ignore_errors=False,
                      handle_list_selector=False):
    '''Return the node pointed to by xpath from mapping.

    Args:
        mapping: nested dictionary.
        xpath: string-like selector.
        default: default value if the attribute doesn't exist.
        ignore_errors: if True, pass silently if the xpath is invalid.
        handle_list_selector: allow to support list element selector

    Example:

    >>> tree = {'level1': {'level2': {'level3': 'bottom'}}}
    >>> get_node_by_xpath(tree, 'level1.level2.level3') == 'bottom'
    True

    '''
    if not isinstance(mapping, dict):
        if not ignore_errors:
            raise KeyError("Mapping is not dictionary: {!r}".format(mapping))
        return default
    for segment in xpath.split('.'):
        if not mapping:
            if not ignore_errors:
                raise KeyError("Empty mapping, but need to access to '{}'".format(xpath))
            return default
        if segment not in mapping:
            if handle_list_selector and '[' in segment:
                re_subselector = re.compile(r"(.*)\[(\d+)\]$")
                m = re_subselector.match(segment)
                if m:
                    key = m.group(1)
                    index = int(m.group(2))
                    if key not in mapping:
                        if not ignore_errors:
                            raise KeyError("Invalid '{}' index selector: '{}' does not match "
                                           "anything. Available keys: {!r}".format(
                                               xpath, key, list(mapping.keys())))
                        return default
                    items = mapping[key]
                    if not isinstance(items, list):
                        if not ignore_errors:
                            raise KeyError("Invalid '{}' selector: '{}' is not a list, is: {}"
                                           .format(xpath, key, type(items)))
                        return default
                    if len(items) <= index:
                        if not ignore_errors:
                            raise KeyError("Invalid '{}' selector: item index '{}' of '{}' is "
                                           "outside of the list boundaries. Length is: {}".format(
                                               xpath, index, key, len(items)))
                        return default
                    mapping = items[index]
                    continue
            elif not ignore_errors:
                raise KeyError("Invalid '{}' selector: '{}' doesn't match "
                               "anything. Available keys: {!r}".format(
                                   xpath, segment, list(mapping.keys())))
            return default
        mapping = mapping[segment]
    return mapping


def set_node_by_xpath(mapping, xpath, value, extend=False, setter_attr=None):
    '''Set the node pointed to by xpath from mapping.

    Args:
        mapping: nested dictionary.
        xpath: string-like selector.
        value: value to set.
        extend: if True, create the nested structure if it doesn't exist,
            otherwise, raise an exception.
        setter_attr: use a special setter method attribute in mapping, instead of replacing
                     the node by the new value (note: do not use a property setter attribute)

    Example:

    >>> tree = {'level1': {'level2': {'level3': 'bottom'}}}
    >>> set_node_by_xpath(tree, 'level1.level2.level3', 'bottom')

    '''
    segments = xpath.split('.')
    attrname = segments.pop()
    for segment in segments:
        if segment not in mapping:
            if not extend:
                raise KeyError("Invalid '{}' selector: '{}' doesn't match "
                               "anything.".format(xpath, segment))
            mapping[segment] = {}
        mapping = mapping[segment]
    if setter_attr:
        # setter attribute defined, calling this setter
        setter = getattr(mapping[attrname], setter_attr)
        setter(value)
    else:
        mapping[attrname] = value


def delete_node_by_xpath(mapping, xpath, ignore_errors=False):
    '''Delete the node pointed to by xpath from mapping.

    Args:
        mapping: nested dictionary.
        xpath: string-like selector.
        ignore_errors: if True, pass silently if the node doesn't exist,
            otherwise, raise an exception.

    Example:

    >>> tree = {'level1': {'level2': {'level3': 'bottom'}}}
    >>> delete_node_by_xpath(tree, 'level1.level2')
    >>> tree
    {'level1': {}}

    '''
    segments = xpath.split('.')
    attrname = segments.pop()
    for segment in segments:
        if segment not in mapping:
            if ignore_errors:
                return
            raise KeyError("Invalid '{}' selector: '{}' doesn't match "
                           "anything.".format(xpath, segment))
        mapping = mapping[segment]
    return mapping.pop(attrname, None)
