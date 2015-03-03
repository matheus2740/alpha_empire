__author__ = 'salvia'


class DatamodelMeta(type):

    def __init__(cls, name, bases, dct):
        super(DatamodelMeta, cls).__init__(name, bases, dct)
        vmattrs = {}
        for key, atr in dct.items():
            if isinstance(atr, VMAttribute):
                atr.set_name('_' + name, key)
                vmattrs['name'] = atr
        cls._vmattrs = vmattrs


class VMAttribute(object):

    def __init__(self):
        self.set_name(self.__class__.__name__, id(self))

    def set_name(self, prefix, key):
        self.attr_name = '%s__%s' % (prefix, key)

    def get_name(self):
        return self.attr_name

    def __get__(self, instance, owner):
        return getattr(instance, self.attr_name)

    def __set__(self, instance, value):
        AttributeError('Cannot set attribute after creation. Use model constructor instead.')


class IntegerVMAttribute(VMAttribute):
    pass


class StringVMAttribute(VMAttribute):
    pass


class FloatVMAttribute(VMAttribute):
    pass


class BooleanVMAttribute(VMAttribute):
    pass


class ListVMAttribute(VMAttribute):
    pass


class PairVMAttribute(VMAttribute):
    pass


class TrioVMAttribute(VMAttribute):
    pass


class QuartetVMAttribute(VMAttribute):
    pass


class business_rule(object):

    def __init__(self, on_change=None, ):
        for target in on_change:
            if not isinstance(target, VMAttribute):
                raise Exception('Target for business rule must be of type VMAttribute, not ' + str(type(target)))
        pass

    def __call__(self, *args, **kwargs):
        pass

    def validate(self):
        pass