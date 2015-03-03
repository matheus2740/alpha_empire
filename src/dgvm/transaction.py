from src.dgvm.instruction import Instruction

__author__ = 'salvia'


class BeginTransaction(Instruction):
    # BEGINTRANS
    opcode = 1
    mnemonic = 'BEGINTRANS'
    n_arg = 0

    @classmethod
    def execute(cls, *args):
        pass


class EndTransaction(Instruction):
    # ENDTRANS
    opcode = 2
    mnemonic = 'ENDTRANS'
    n_arg = 0

    @classmethod
    def execute(cls, *args):
        pass