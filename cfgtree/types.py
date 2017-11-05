# coding: utf-8

import argparse
import os

_UNDEFINED = object()


class _CfgBase(object):

    default = None
    name = None
    xpath = None
    arg_type = None
    environ_var_prefix = None
    ignore_in_cfg = False

    def __init__(self, l=None, s=None, h=None, r=False, d=_UNDEFINED):
        # Note: self.name should come later by EnvironmentConfig._inject_names()
        self.short_param = s
        self.help_str = h
        self.required = r
        self.forced_long_param = l
        if d != _UNDEFINED:
            self.default = d
        self._value = self.default

    def set_value(self, value):
        """
        Setter method used in set_node_by_xpath
        """
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self.set_value(value)

    @property
    def environ_var_name(self):
        return self.environ_var_prefix + self.cmd_line_name.upper()

    def get_cmd_line_params(self):
        a = []
        if self.short_param:
            a.append(self.short_param)
        if self.name:
            a.append(self.long_param)
        return a

    @property
    def _environ_var_value(self):
        return os.environ.get(self.environ_var_name, _UNDEFINED)

    def read_environ_var(self):
        return str(self._environ_var_value)

    @property
    def long_param(self):
        if self.forced_long_param:
            return self.forced_long_param
        if not self.xpath:
            return "--" + self.name.lower().replace("_", "-")
        return "--" + self.xpath.replace('.', '-').replace('_', '-')

    @property
    def cmd_line_name(self):
        return self.xpath.lower().replace("-", "_").replace(".", "_")

    @property
    def action(self):
        return 'store'

    @property
    def n_args(self):
        return None

    @property
    def safe_value(self):
        """
        string that can be outputed to logs
        """
        return self.value

    @property
    def cfgfile_value(self):
        """
        value as it should be saved in config file
        """
        return self.value if self.value is not None else ""

    @property
    def metavar(self):
        return self.name.upper()


class StringCfg(_CfgBase):
    default = ""

    def read_environ_var(self):
        return str(self._environ_var_value)


class ListOfStringCfg(_CfgBase):
    """
    Comma separated list of string (1 argument)
    """

    def __init__(self, *args, **kwargs):
        self.default = []
        super(ListOfStringCfg, self).__init__(*args, **kwargs)

    def read_environ_var(self):
        ls = self._environ_var_value
        return ls.split(",")

    @property
    def cfgfile_value(self):
        """
        value as it should be saved in config file
        """
        return ",".join(self.value)

    @staticmethod
    def arg_type(string):
        return string.split(",")


class IntCfg(_CfgBase):
    default = 0

    def read_environ_var(self):
        return int(self._environ_var_value)


class UserCfg(StringCfg):
    @property
    def user(self):
        return self.value


class PasswordCfg(StringCfg):
    @property
    def password(self):
        return self.value

    @property
    def safe_value(self):
        """
        Hide password in logs
        """
        return "*" * len(self.value)


class DirNameCfg(StringCfg):
    default = None

    def set_value(self, value):
        self._value = os.path.abspath(value)


class ConfigFileCfg(StringCfg):
    default = None
    ignore_in_cfg = True


class BoolCfg(_CfgBase):
    default = False

    def read_environ_var(self):
        e = os.environ.get(self.environ_var_name)
        return bool(e)

    @property
    def action(self):
        return 'store_true'

    @property
    def metavar(self):
        return None


class MultiChoiceCfg(ListOfStringCfg):
    def __init__(self, choices=None, *args, **kwargs):
        super(MultiChoiceCfg, self).__init__(*args, **kwargs)
        self.choices = choices

    def arg_type(self, string):
        items = string.split(",")
        for item in items:
            if item not in self.choices:
                raise argparse.ArgumentTypeError("{!r} not in available choise: {}".format(
                    item, ", ".join(self.choices)))
        return items


class SingleChoiceCfg(StringCfg):
    def __init__(self, choices=None, *args, **kwargs):
        super(SingleChoiceCfg, self).__init__(*args, **kwargs)
        self.choices = choices

    def arg_type(self, string):
        if string not in self.choices:
            raise argparse.ArgumentTypeError("{!r} not in available choise: {}".format(
                string, ", ".join(self.choices)))
        return string
