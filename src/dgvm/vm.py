from collections import deque
import os
import hashlib
from src.dgvm.datamodel_meta import DatamodelMeta
from src.dgvm.instruction import Instruction, InvalidInstruction
from src.dgvm.ipc.server import BaseIPCServer
from src.dgvm.transaction import EndTransaction, BeginTransaction
from datamodel import InvalidModel, Datamodel
import datamodel

__author__ = 'salvia'


def file_here(file):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), file)


class Heap(object):

    def __init__(self, size):
        super(Heap, self).__init__()
        self.size = size
        self.data = {}


class VMMeta(type):

    def __init__(cls, name, bases, dct):
        super(VMMeta, cls).__init__(name, bases, dct)


class Commit(object):

    def __init__(self,):
        self.hash = None
        self.diff = deque()

    def calc_hash(self):
        pre_str = deque()
        for instruction in self.diff:
            pre_str.append(instruction.mnemonize())

        pre_str = '\n'.join(pre_str)
        self.hash = hashlib.sha256(pre_str).hexdigest()


# BaseIPCServer is old-styled (Python ServerSocker is old-style, sadly),
# so we need to inherit from object also, if we want metaclasses to work.
class VM(BaseIPCServer, object):
    __metaclass__ = VMMeta

    def __init__(self, definitions_package):

        BaseIPCServer.__init__(self, start=False)
        self.instructions_pack = __import__(definitions_package + '.instructions')
        self.datamodels_pack = __import__(definitions_package + '.datamodels')

        self.datamodels = {}
        self.instructions = []

        self.load_datamodels()
        self.load_instructions()

        # initialize heap (16k starting size)
        self.heap = Heap(16384)

        # are we currently in a transaction?
        self.in_transaction = False
        # temporary state of the commit. may be reversed or permanently commited
        self.workspace = None
        # commit history
        self.commits = deque()

        # debugging
        self.verbose = False

    def load_datamodels(self):
        models = deque()
        for k, v in self.datamodels_pack.datamodels.__dict__.iteritems():
            if isinstance(v, DatamodelMeta):
                self.validate_model(v)
                models.append(v)

        self.datamodels = list(models)

    def validate_model(self, model):
        for m in datamodel.required_methods:
            if m not in model.__dict__ or model.__dict__[m] is getattr(Datamodel, m):
                raise InvalidModel('%s does not define %s' % (model.__name__, m))

    def load_instructions(self):
        self.instructions = {
            'opcodes': {
                BeginTransaction.opcode: BeginTransaction,
                EndTransaction.opcode: EndTransaction
            },
            'mnemonics': {
                BeginTransaction.mnemonic: BeginTransaction,
                EndTransaction.mnemonic: EndTransaction
            }
        }
        for k, v in self.instructions_pack.instructions.__dict__.iteritems():
            if isinstance(v, type) and issubclass(v, Instruction):
                self.add_instruction(v)

    def add_instruction(self, instruction):
        validation = self.validate_instruction(instruction)

        if not validation[0]:
            raise InvalidInstruction(validation[1])

        self.instructions['opcodes'][instruction.opcode] = instruction
        self.instructions['mnemonics'][instruction.mnemonic] = instruction

    def validate_instruction(self, instruction):

        def invalid(desc):
            return False, '%s: %s' % (desc, str(instruction))

        if instruction.opcode <= 100:
            return invalid('Invalid opcode')
        if not instruction.mnemonic:
            return invalid('Invalid mnemonic')
        if instruction.opcode in self.instructions['opcodes']:
            return invalid('Duplicate opcode')
        if instruction.mnemonic in self.instructions['mnemonics']:
            return invalid('Duplicate mnemonic')

        return True, 'OK'

    def startup(self):
        BaseIPCServer.startup(self)

    # -----

    def begin_transaction(self):
        self.workspace = Commit()
        self.workspace.diff.append(BeginTransaction())

    def end_transaction(self):
        self.workspace.diff.append(EndTransaction())
        self.workspace = None

    def emit(self, log):
        if not self.workspace:
            self.begin_transaction()
        self.raw_emit(log)

    def raw_emit(self, log):
        self.workspace.diff.extend(log)
        for instruction in log:
            instruction(self)

    def commit(self):
        self.workspace.calc_hash()
        self.commits.append(self.workspace)
        self.end_transaction()

    def get_last_commit(self):
        return self.commits[-1]

