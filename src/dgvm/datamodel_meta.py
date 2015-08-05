from collections import deque
from src.dgvm.utils import Proxy, iterable

__author__ = 'salvia'


class DatamodelStates(object):
    NORMAL = 0
    USER_CHANGING = 1
    ENGINE_CHANGING = 2
    DESTROYED = 3


class DatamodelMeta(type):

    def __init__(cls, name, bases, dct):
        super(DatamodelMeta, cls).__init__(name, bases, dct)
        vmattrs = {}
        for key, atr in dct.items():
            if isinstance(atr, VMAttribute):
                atr.set_name('_' + name, key)
                vmattrs[key] = atr
        cls._vmattrs = vmattrs


class VMAttributeView(Proxy):

    def __init__(self, val, type, model_instance):
        super(VMAttributeView, self).__init__(val)
        self.__dict__['type'] = type
        self.__dict__['model_instance'] = model_instance

    def reinit(self, obj):
        return type(self)(obj, self.__dict__['type'], self.__dict__['model_instance'])

    def _set(self, val):
        self.__dict__['_obj'] = val


class ModelDestroyedError(Exception):
    pass


class VMAttribute(object):

    attr_type = None
    coerce_val = False

    def __init__(self, default=None, **kwargs):
        self.attr_name = ""
        self.name = ""
        self.on_change = ConstraintCollection()
        self.default = default
        self.set_name(self.__class__.__name__, id(self))

    def val_init(self):
        if self.default:
            return self.default
        if self.attr_type:
            return self.attr_type()
        return None

    def set_name(self, prefix, key):
        self.name = key
        self.attr_name = '%s__%s' % (prefix, key)

    def _get_wrapped_value(self, instance):
        return getattr(instance, self.attr_name, VMAttributeView(None, None, None))

    def _set_wrapped_value(self, instance, value):
        if not getattr(instance, self.attr_name, None):
            setattr(instance, self.attr_name, VMAttributeView(value, self, instance))
        else:
            getattr(instance, self.attr_name)._set(value)

    def __get__(self, instance, owner):

        if instance._state == DatamodelStates.DESTROYED:
            raise ModelDestroyedError()

        return self._get_wrapped_value(instance)

    def __set__(self, instance, value):

        if self.coerce_val:
            value = self.attr_type(value)

        def normal():
            raise AttributeError('Cannot set attribute after object creation, build a new object or use Instructions.')

        def user_changing():
            for constraint in self.on_change:
                validates = constraint.validate(instance, value)
                if not validates:
                    raise ConstraintViolation(str(constraint))
            self._set_wrapped_value(instance, value)

        def engine_changing():
            self._set_wrapped_value(instance, value)

        def destroyed():
            raise ModelDestroyedError()

        actions = {
            DatamodelStates.NORMAL: normal,
            DatamodelStates.USER_CHANGING: user_changing,
            DatamodelStates.ENGINE_CHANGING: engine_changing,
            DatamodelStates.DESTROYED: destroyed
        }

        actions[instance._state]()


class TypedVMAttribute(VMAttribute):

    def __init__(self, subtype, default=None, **kwargs):
        super(TypedVMAttribute, self).__init__(**kwargs)
        if not subtype:
            raise ValueError('subtype cannot be None')
        if default and not isinstance(default, self.attr_type):
            raise ValueError('default value must be of type %s, not %s' % (str(self.attr_type), str(type(default))))
        self.subtype = subtype

    def val_init(self):
        if self.default:
            return self.default
        if self.attr_type:
            return self.attr_type(self.subtype)
        return None


def listof(type):
    return []


class tuple2(object):

    def __init__(self, x, y=None):
        if iterable(x):
            self.x = x[0]
            self.y = x[1]
        else:
            self.x = x
            self.y = y

    def __getitem__(self, item):
        if item == 0:
            return self.x
        if item == 1:
            return self.y

        raise KeyError(str(item))

    def __len__(self):
        return 2

    def __eq__(self, other):
        if iterable(other):
            return len(self) == len(other) and self.x == other[0] and self.y == other[1]

        return NotImplemented

    def __str__(self):
        return '(%s, %s)' % (str(self.x), str(self.y))

    def __repr__(self):
        return str(self)


class tuple3(object):

    def __init__(self, x, y=None, z=None):
        if iterable(x):
            self.x = x[0]
            self.y = x[1]
            self.z = x[2]
        else:
            self.x = x
            self.y = y
            self.z = z

    def __getitem__(self, item):
        if item == 0:
            return self.x
        if item == 1:
            return self.y
        if item == 2:
            return self.z

        raise KeyError(str(item))

    def __len__(self):
        return 3

    def __eq__(self, other):
        if iterable(other):
            return len(self) == len(other) and self.x == other[0] and self.y == other[1] and self.z == other[2]

        return NotImplemented

    def __str__(self):
        return '(%s, %s, %s)' % (str(self.x), str(self.y), str(self.z))

    def __repr__(self):
        return str(self)


class tuple4(object):

    def __init__(self, x, y=None, z=None, w=None):
        if iterable(x):
            self.x = x[0]
            self.y = x[1]
            self.z = x[2]
            self.w = x[4]
        else:
            self.x = x
            self.y = y
            self.z = z
            self.w = w

    def __getitem__(self, item):
        if item == 0:
            return self.x
        if item == 1:
            return self.y
        if item == 2:
            return self.z
        if item == 3:
            return self.w

        raise KeyError(str(item))

    def __len__(self):
        return 4

    def __eq__(self, other):
        if iterable(other):
            return len(self) == len(other) and self.x == other[0] and self.y == other[1] and self.z == other[2] and self.w == other[3]

        return NotImplemented

    def __str__(self):
        return '(%s, %s, %s, %s)' % (str(self.x), str(self.y), str(self.z), str(self.w))

    def __repr__(self):
        return str(self)


class IntegerVMAttribute(VMAttribute):
    attr_type = int


class StringVMAttribute(VMAttribute):
    attr_type = str


class FloatVMAttribute(VMAttribute):
    attr_type = float


class BooleanVMAttribute(VMAttribute):
    attr_type = bool


class ListVMAttribute(TypedVMAttribute):
    attr_type = staticmethod(listof)


class PairVMAttribute(TypedVMAttribute):
    attr_type = staticmethod(tuple2)
    coerce_val = True


class TrioVMAttribute(TypedVMAttribute):
    attr_type = staticmethod(tuple3)
    coerce_val = True


class QuartetVMAttribute(TypedVMAttribute):
    attr_type = staticmethod(tuple4)
    coerce_val = True


class ForeignModelVMAttribute(TypedVMAttribute):
    pass

class ConstraintViolation(Exception):
    pass


class Constraint(object):

    def __init__(self, name, func, target, related):
        related = related or tuple()
        if not isinstance(target, VMAttribute):
            raise Exception('Target for business rule must be of type VMAttribute, not ' + str(type(target)))

        for target in related:
            if not isinstance(target, VMAttribute):
                raise Exception('Related objects for business rule must be of type VMAttribute, not ' + str(type(target)))

        self.name = name
        self.func = func
        self._target = target
        self._related = related

    def related(self, model_instance):
        return {r.name: r._get_wrapped_value(model_instance) for r in self._related}

    def target(self, model_instance):
        return self._target._get_wrapped_value(model_instance)

    def validate(self, model_instance):
        return False

    def __str__(self):
        return '<%s: %s on %s>' % (type(self).__name__, self.name, self._target.name)


class AttributeChangedConstraint(Constraint):

    def __init__(self, name, func, target, related):
        super(AttributeChangedConstraint, self).__init__(name, func, target, related)

    def validate(self, model_instance, new):
        return self.func(self, self.target(model_instance), new, self.related(model_instance))


class ConstraintCollection(object):

    def __init__(self, constraints=None):
        self.constraints = constraints or deque()

    def add_constraint(self, cons):
        self.constraints.append(cons)

    def __iter__(self):
        return iter(self.constraints)


class constraint(object):
    """
        Decorators
    """
    class on_change(object):
        def __init__(self, target, related=tuple()):
            self.func = None
            self.target = target
            self.related = related

        def __call__(self, func):
            self.func = func
            c = AttributeChangedConstraint(func.__name__, func, self.target, self.related)
            self.target.on_change.add_constraint(c)
            return c





