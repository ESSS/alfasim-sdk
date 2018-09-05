import attr

from alfasim_sdk.data_types import BaseField


def container_model(*, model, CAPTION, ICON):

    def apply(class_):
        setattr(class_, 'model', attr.ib(default=model))
        return wrap_class(class_, CAPTION, ICON)

    return apply


def data_model(*, CAPTION, ICON=None):

    def apply(class_):
        setattr(class_, 'model', attr.ib(default=None))
        return wrap_class(class_, CAPTION, ICON)

    return apply


def wrap_class(class_, CAPTION, ICON):
    for name in dir(class_):
        value = getattr(class_, name)

        if isinstance(value, BaseField):
            if name.startswith('_'):
                continue
            new_value = attr.ib(default=value)
            setattr(class_, name, new_value)

    setattr(class_, 'CAPTION', attr.ib(default=CAPTION))
    setattr(class_, 'ICON', attr.ib(default=ICON))

    return attr.s(class_)
