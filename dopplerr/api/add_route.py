# coding: utf-8

# Third Party Libraries
from sanic_transmute import add_route
from transmute_core.compat import string_type
from transmute_core.function import TransmuteAttributes


def describe_add_route(blueprint, **kwargs):

    # if we have a single method, make it a list.
    if isinstance(kwargs.get("paths"), string_type):
        kwargs["paths"] = [kwargs["paths"]]
    if isinstance(kwargs.get("methods"), string_type):
        kwargs["methods"] = [kwargs["methods"]]
    attrs = TransmuteAttributes(**kwargs)

    def decorator(fnc):
        if hasattr(fnc, "transmute"):
            fnc.transmute = fnc.transmute | attrs
        else:
            fnc.transmute = attrs
        add_route(blueprint, fnc)
        return fnc

    return decorator
