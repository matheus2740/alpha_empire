__author__ = 'salvia'


class InvalidInstruction(Exception):
    pass


class BadInstructionCall(Exception):
    pass


def str_instruction(self):
    return (
        '<%s at %i: opcode=%i, n_arg=%i, mnemonic=%s>' %
        (self.get_name(), id(self), self.opcode, self.n_args, self.mnemonic)
    )


_required_parameters = [
    ('opcode', int),
    ('mnemonic', str),
    ('n_args', int),
    ('arg_types', tuple)
]


def raise_invalid(ins, arg):
    raise InvalidInstruction('Invalid ' + arg + ' for instruction ' + str(ins))


class InstructionMeta(type):

    def __str__(self):
        return '<%s at %i: opcode=%i, n_arg=%i, mnemonic=%s>' % (self.__name__, id(self), self.opcode, self.n_args, self.mnemonic)

    def __init__(cls, name, bases, dct):
        super(InstructionMeta, cls).__init__(name, bases, dct)
        cls.__str__ = str_instruction
        if name != 'Instruction' and name != 'MemberInstruction':
            for par in _required_parameters:
                if dct.get(par[0]) is None or not isinstance(dct.get(par[0]), par[1]):
                    raise_invalid(cls, par[0])
            if len(dct.get('arg_types')) != dct.get('n_args'):
                raise_invalid(cls, 'arg_types')


class Instruction(object):

    __metaclass__ = InstructionMeta

    # code of instruction
    opcode = None
    # mnemonic
    mnemonic = None
    # number of arguments
    n_args = None
    # types of the arguments
    arg_types = None

    def __init__(self, *args):
        from datamodel import Datamodel

        if len(self.arg_types) != self.n_args:
            raise InvalidInstruction('Instruction %s has mismatching .n_args and .arg_types' % (type(self).__name__, ))

        if len(args) != self.n_args:
            raise BadInstructionCall('Wrong number of arguments to ' + str(self))
        for i, arg in enumerate(args):
            if not isinstance(arg, self.arg_types[i]):
                raise BadInstructionCall('Wrong type of arguments to ' + str(self))
        self.args = args
        self.model_args = [arg for arg in args if isinstance(arg, Datamodel)]

    def __call__(self, vm):
        map(lambda model: model._to_user_changing_state(), self.model_args)
        self.execute(vm, *self.args)
        map(lambda model: model._to_normal_state(), self.model_args)

    def mnemonize(self):
        return str(self.mnemonic) + ''.join(' %s' % self.args[n] for n in xrange(self.n_args))

    @staticmethod
    def execute(cls, vm, *args):

        raise ValueError('Cannot execute base class instruction.')

    @classmethod
    def get_name(cls):
        return cls.__name__


class MemberInstruction(Instruction):

    owner = None
    onself = False
    instances = {}

    def __init__(self, *args):
        super(MemberInstruction, self).__init__(*args)

    @classmethod
    def get_name(cls):
        return cls.owner.__name__ + '.' + cls.__name__


class MemberInstructionView(object):

    def __init__(self, instr, instance):
        self.__dict__['instr'] = instr
        self.__dict__['instance'] = instance

    def __getattr__(self, item):
        return getattr(self.__dict__['instr'], item)

    def __setattr__(self, key, value):
        return setattr(self.__dict__['instr'], key, value)

    def __call__(self, *args, **kwargs):
        instruction_class = self.__dict__['instr']
        model_instance = self.__dict__['instance']
        instruction = instruction_class(model_instance, *args, **kwargs)
        model_instance.vm.emit([instruction])
        return None


class MemberInstructionWrapper(object):

    def __init__(self, func, opcode, mnemonic, args, onself):
        self.attr_name = ""
        self.name = ""
        self.func = func
        self.opcode = opcode
        self.mnemonic = mnemonic
        self.args = args
        self.onself = onself
        self.i = None

    def __get__(self, instance, owner):
        if instance:
            if instance.is_destroyed():
                from datamodel_meta import ModelDestroyedError
                raise ModelDestroyedError()
            return MemberInstructionView(self.i, instance)
        else:
            return self.i

    def __set__(self, instance, value):
        raise ValueError('Cannot set MemberInstruction after its creation')

    def register(self, vm, owner):
        self.i = InstructionMeta(self.func.__name__, (MemberInstruction,), {
            'opcode': self.opcode,
            'mnemonic': self.mnemonic,
            'n_args': len(self.args),
            'arg_types': self.args,
            'owner': owner,
            'onself': self.onself
        })
        self.i.execute = staticmethod(self.func)
        vm.add_instruction(self.i)


class instruction(object):
    """
        Decorator for inline instructions
    """

    def __init__(self, opcode, mnemonic, args, onself=True):
        self.opcode = opcode
        self.mnemonic = mnemonic
        self.args = args
        self.onself = onself

    def __call__(self, func):
        return MemberInstructionWrapper(func, self.opcode, self.mnemonic, self.args, self.onself)