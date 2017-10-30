# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re


def getNodeByPath(mapping, xpath, default=None, ignoreErrors=False, handleListSelector=False):
    '''Return the node pointed to by xpath from mapping.

    Args:
        mapping: nested dictionary.
        xpath: string-like selector.
        default: default value if the attribute doesn't exist.
        ignoreErrors: if True, pass silently if the xpath is invalid.
        handleListSelector: allow to support list element selector

    Example:

    >>> tree = {'level1': {'level2': {'level3': 'bottom'}}}
    >>> getNodeByPath(tree, 'level1.level2.level3') == 'bottom'
    True

    '''
    if not isinstance(mapping, dict):
        if not ignoreErrors:
            raise KeyError("Mapping is not dictionary: {!r}".format(mapping))
        return default
    for segment in xpath.split('.'):
        if not mapping:
            if not ignoreErrors:
                raise KeyError("Empty mapping, but need to access to '{}'".format(xpath))
            return default
        if segment not in mapping:
            if handleListSelector and '[' in segment:
                re_subselector = re.compile(r"(.*)\[(\d+)\]$")
                m = re_subselector.match(segment)
                if m:
                    key = m.group(1)
                    index = int(m.group(2))
                    if key not in mapping:
                        if not ignoreErrors:
                            raise KeyError("Invalid '{}' index selector: '{}' does not match "
                                           "anything. Available keys: {!r}".format(
                                               xpath, key, list(mapping.keys())))
                        return default
                    items = mapping[key]
                    if not isinstance(items, list):
                        if not ignoreErrors:
                            raise KeyError("Invalid '{}' selector: '{}' is not a list, is: {}"
                                           .format(xpath, key, type(items)))
                        return default
                    if len(items) <= index:
                        if not ignoreErrors:
                            raise KeyError("Invalid '{}' selector: item index '{}' of '{}' is "
                                           "outside of the list boundaries. Length is: {}".format(
                                               xpath, index, key, len(items)))
                        return default
                    mapping = items[index]
                    continue
            elif not ignoreErrors:
                raise KeyError("Invalid '{}' selector: '{}' doesn't match "
                               "anything. Available keys: {!r}".format(
                                   xpath, segment, list(mapping.keys())))
            return default
        mapping = mapping[segment]
    return mapping


def setNodeByPath(mapping, xpath, value, extend=False):
    '''Set the node pointed to by xpath from mapping.

    Args:
        mapping: nested dictionary.
        xpath: string-like selector.
        value: value to set.
        extend: if True, create the nested structure if it doesn't exist,
            otherwise, raise an exception.

    Example:

    >>> tree = {'level1': {'level2': {'level3': 'bottom'}}}
    >>> setNodeByPath(tree, 'level1.level2.level3', 'bottom')

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
    mapping[attrname] = value


def deleteNodeByPath(mapping, xpath, ignoreErrors=False):
    '''Delete the node pointed to by xpath from mapping.

    Args:
        mapping: nested dictionary.
        xpath: string-like selector.
        ignoreErrors: if True, pass silently if the node doesn't exist,
            otherwise, raise an exception.

    Example:

    >>> tree = {'level1': {'level2': {'level3': 'bottom'}}}
    >>> deleteNodeByPath(tree, 'level1.level2')
    >>> tree
    {'level1': {}}

    '''
    segments = xpath.split('.')
    attrname = segments.pop()
    for segment in segments:
        if segment not in mapping:
            if ignoreErrors:
                return
            raise KeyError("Invalid '{}' selector: '{}' doesn't match "
                           "anything.".format(xpath, segment))
        mapping = mapping[segment]
    return mapping.pop(attrname, None)
