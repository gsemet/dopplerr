# coding: utf-8
"""
Singleton class definition

Usage:

    @singleton
    class MySingletonClass(object):
        def __init__(self):
            pass
        ...
        def a_function(self):
            pass

Later in the code:

    from module.of.MySingleton import MySingletonClass
    def anyFunction(...):
        ...
        MySingletonClass().a_function(...)


"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import types


# pylint: disable=invalid-name
class __Singleton(object):
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.
    The decorated class can define one `__init__` function that
    takes only the `self` argument. Other than that, there are
    no restrictions that apply to the decorated class.
    To get the singleton instance, use the `instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.
    Limitations: The decorated class cannot be inherited from.
    """

    def __init__(self, decorated):
        self._decorated = decorated

    def instance(self, *args, **kwargs):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.
        """
        # Do not use a test here for performance sake. The first call has the exception penalty
        try:
            return self._instance
        except AttributeError:
            # pylint: disable=attribute-defined-outside-init
            self._instance = self._decorated(*args, **kwargs)

            # pylint: enable=attribute-defined-outside-init

            def unload(inst):
                # pylint: disable=protected-access
                inst.__singleton.unload()
                # pylint: enable=protected-access

            # Magically bind "unload" as a method
            self._instance.unload = types.MethodType(unload, self._instance)
            # pylint: disable=protected-access
            self._instance.__singleton = self
            # pylint: enable=protected-access
            return self._instance

    def __call__(self, *args, **kwargs):
        return self.instance(*args, **kwargs)

    def unload(self):
        if hasattr(self, "_instance"):
            delattr(self, "_instance")


singleton = __Singleton
# pylint: enable=invalid-name
