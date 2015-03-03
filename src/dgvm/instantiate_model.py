from src.dgvm.instruction import Instruction

__author__ = 'salvia'


class Instantiate(Instruction):
    # INST model_instance [attributes]
    opcode = 3
    mnemonic = 'INST'
    n_arg = 2

    @classmethod
    def execute(cls, vm, model_instance, attrs):
        vm.heap.data[id(model_instance)] = model_instance