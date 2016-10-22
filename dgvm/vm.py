from collections import deque
import os
import hashlib
from datamodel.meta import DatamodelMeta
from dgvm.data_structures import Heap
from instruction import InvalidInstruction, MemberInstructionWrapper
from ipc.server import BaseIPCServer
from builtin_instructions import *
from datamodel import InvalidModel, Datamodel
from utils import iterable
import datamodel

__author__ = 'salvia'


def file_here(file):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), file)


class VMMeta(type):

    def __init__(cls, name, bases, dct):
        super(VMMeta, cls).__init__(name, bases, dct)


class Commit(object):

    def __init__(self):
        self.__has_valid_hash = False
        self.__hash = None
        self.__diff = deque()

    def calc_hash(self):
        if not self.__has_valid_hash:
            pre_str = deque()
            for instruction in self.__diff:
                pre_str.append(instruction.mnemonize())

            pre_str = '\n'.join(pre_str)
            self.__hash = int(hashlib.sha256(pre_str).hexdigest(), 16)
            self.__has_valid_hash = True
        return self.__hash

    def append(self, item):
        if not isinstance(item, Instruction):
            raise ValueError('Commit item must be of type Instruction, not ' + type(item).__name__)
        self.__has_valid_hash = False
        self.__hash = None
        self.__diff.append(item)

    def extend(self, items):
        if not iterable(items):
            raise ValueError('items must be iterable')

        for item in items:
            self.append(item)

    def dumps(self):
        raise NotImplementedError()

    @classmethod
    def loads(cls):
        raise NotImplementedError()

    def __len__(self):
        return len(self.__diff)

    def __getitem__(self, item):
        return self.__diff[item]

    def __setitem__(self, key, value):
        raise ValueError('Cannot set a commit item.')

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return self.calc_hash()

    def __str__(self):
        s = []
        for i in range(min(len(self.__diff), 10)):
            s += [str(self.__diff[i])]
        return '<Commit object at %s with instructions: [%s]>' % (id(self), ', '.join(s))


class VM(BaseIPCServer):
    __metaclass__ = VMMeta

    def __init__(self, definitions_package):

        BaseIPCServer.__init__(self, start=False)
        self.instructions_pack = __import__(definitions_package + '.instructions')
        self.datamodels_pack = __import__(definitions_package + '.datamodels')

        self.datamodels = {}
        self.instructions = {'opcodes': {}, 'mnemonics': {}}

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
                for member_instruction in [inst for (name, inst) in v.__dict__.iteritems() if isinstance(inst, MemberInstructionWrapper)]:
                    member_instruction.register(self, v)

        self.datamodels = list(models)

    def validate_model(self, model):
        for m in datamodel.model.required_methods:
            if m not in model.__dict__ or model.__dict__[m] is getattr(Datamodel, m):
                raise InvalidModel('%s does not define %s' % (model.__name__, m))

    def load_instructions(self):
        self.instructions = {
            'opcodes': {
                BeginTransaction.opcode: BeginTransaction,
                EndTransaction.opcode: EndTransaction,
                InstantiateModel.opcode: InstantiateModel,
                DestroyInstance.opcode: DestroyInstance
            },
            'mnemonics': {
                BeginTransaction.mnemonic: BeginTransaction,
                EndTransaction.mnemonic: EndTransaction,
                InstantiateModel.mnemonic: InstantiateModel,
                DestroyInstance.mnemonic: DestroyInstance
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

        def fmt(desc):
            return False, '%s: %s' % (desc, str(instruction))

        if instruction.opcode <= 100:
            return fmt('Invalid opcode')
        if not instruction.mnemonic:
            return fmt('Invalid mnemonic')
        if instruction.opcode in self.instructions['opcodes']:
            return fmt('Duplicate opcode')
        if instruction.mnemonic in self.instructions['mnemonics']:
            return fmt('Duplicate mnemonic')

        return True, 'OK'

    # -----

    def begin_transaction(self):
        """
            Start a new commit and adds VM_BEGINTRANS to it (every commit start with an VM_BEGINTRANS instruction)
        """
        if self.workspace:
            raise Exception('Cannot begin transaction with an uncomitted transaction (dirty workspace).')
        self.workspace = Commit()
        self.workspace.append(BeginTransaction())

    def end_transaction(self):
        """
            Ends the current commit and adds VM_ENDTRANS to it (every commit ends with a VM_ENDTRANS instruction)
        """
        self.workspace.append(EndTransaction())
        self.workspace = None

    def execute(self, instructions):
        if not iterable(instructions):
            raise ValueError('Argument must be a list of instructions, not ' + type(instructions).__name__)
        if not self.workspace:
            self.begin_transaction()

        for instruction in instructions:
            instruction(self)
        self.workspace.extend(instructions)

    def commit(self):
        if self.workspace:
            self.workspace.calc_hash()
            self.commits.append(self.workspace)
            self.end_transaction()

    def rollback(self):
        # TODO: implement rollback
        pass

    def get_last_commit(self):
        return self.commits[-1]


#TODO: implement commit log/history
#TODO: implement serialization of heap and commit logs
#TODO: implement VM compilation

