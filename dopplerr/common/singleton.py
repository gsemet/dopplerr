# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import types


class singleton:

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
            self._instance = self._decorated(*args, **kwargs)

            def unload(inst):
                inst.__singleton.unload()
            # Magically bind "unload" as a method
            self._instance.unload = types.MethodType(unload, self._instance)
            self._instance.__singleton = self
            return self._instance

    def __call__(self, *args, **kwargs):
        return self.instance(*args, **kwargs)

    def unload(self):
        if hasattr(self, "_instance"):
            delattr(self, "_instance")
