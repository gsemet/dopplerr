==================
Configuration Tree
==================

This module provides an easy yet comprehensive way of defining a configuration tree
for any application.

It requires the following acknolegdment:

- Application settings are organize in a hierarchical structure, dependend of the application
  itself. This structure is called in cfgtree: "bare config".

- Settings can come from different inputs:

  - environment variables (12 factors approach)
  - command line argument
  - configuration storage area such as json or configuration server

Configuration Storage
---------------------

The trivial storage is a simple json file. The complete settings are placed inside it, such as:

    {
        'setting1': 'value1',
        'setting2': 'value2',
        'setting3': 'value3',
    }

But developer may want to organize in a more hierarchical structure.

Another typical file format for configuration is Yaml file, which is more human readable and allow
inserting comments and so.

But both are storing hierarchical configuration.

Instead of one file, we can imagine a set of files where each individual file is gathered at the
first level of the configuration hierarchy.

Current Support:

- single Json file

Future support:

- Yaml file (with inplace save keeping comments and overall organization)
- Set of Yaml files
- Configuration server

Configuration Tree Description
------------------------------

Configuration hierarchy is to be described in a `cfgtree.EnvironmentConfig` inherited instance,
inside the member `.cfgtree`, using helper classes such as `StringCfg`, 'IntCfg', 'UserCfg' or
'PasswordCfg'. Each setting can be set by environment variable, command line parameter or by
the storage file(s) itself.

Let's take an example of an item defined at the first level of the hierarchy. It is defined as a
'IntCfg' with name 'count'. It can be set by the following:

- environment variable `APPLICATIONNAME_COUNT` (`APPLICATIONNAME` is an optional developer-defined
  prefix added to every environment variable)
- command line argument `--count`
- item `count` at the first level of a json file

Hierarchical structure is reflected in these different ways, to avoid conflicts. Now, the 'count'
setting is set in a settings section called 'general':

- environment variable: `APPLICATIONNAME_GENERAL_COUNT`
- command line argument: `--general-count`
- Json has a first level named `general`, and inside one of the items is called `count`.

XPath syntax
------------

A xpath-like syntax allows to reach any item of the configuration: `<key1>.<key2>.<key3>.<item>`.
