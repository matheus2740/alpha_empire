__author__ = 'salvia'


class InvalidInstruction(Exception):
    pass


class BadInstructionCall(Exception):
    pass


def str_instruction(self):
    return '<%s at %i: opcode=%i, n_arg=%i, mnemonic=%s>' %\
           (type(self).__name__, id(self), self.opcode, self.n_arg, self.mnemonic)


class InstructionMeta(type):

    __str__ = str_instruction

    def __init__(cls, name, bases, dct):
        super(InstructionMeta, cls).__init__(name, bases, dct)
        cls.__str__ = str_instruction


class Instruction(object):

    __metaclass__ = InstructionMeta

    # code of instruction
    opcode = None
    # number of arguments
    n_arg = None
    # mnemonic
    mnemonic = None

    def __init__(self, *args):
        if len(args) != self.n_arg:
            raise BadInstructionCall('Wrong number of arguments to ' + self.mnemonic)
        self.args = args

    def __call__(self, vm):
        self.execute(vm, *self.args)

    def mnemonize(self):
        return str(self.opcode) + ''.join(' %s' % self.args[n] for n in xrange(self.n_arg))

    @classmethod
    def execute(cls, vm, *args):
        raise ValueError('Cannot execute base class instruction.')