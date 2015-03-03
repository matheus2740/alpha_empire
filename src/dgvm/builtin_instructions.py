from src.dgvm.instruction import Instruction

__author__ = 'salvia'


class BeginTransaction(Instruction):
    # BEGINTRANS
    opcode = 1
    mnemonic = 'BEGINTRANS'
    n_args = 0
    arg_types = tuple()

    @classmethod
    def execute(cls, *args):
        pass


class EndTransaction(Instruction):
    # ENDTRANS
    opcode = 2
    mnemonic = 'ENDTRANS'
    n_args = 0
    arg_types = tuple()

    @classmethod
    def execute(cls, *args):
        pass


class InstantiateModel(Instruction):
    # INST model_instance [attributes]
    opcode = 3
    mnemonic = 'INST'
    n_args = 2
    arg_types = (object, dict)

    def __init__(self, *args):
        super(InstantiateModel, self).__init__(*args)
        from src.dgvm.datamodel import Datamodel
        InstantiateModel.arg_types = (Datamodel, dict)

    @classmethod
    def execute(cls, vm, model_instance, attrs):
        vm.heap.data[id(model_instance)] = model_instance


class DestroyInstance(Instruction):
    # DESTROY model_instance
    opcode = 4
    mnemonic = 'DESTROY'
    n_args = 1
    arg_types = (object,)

    def __init__(self, *args):
        super(DestroyInstance, self).__init__(*args)
        from src.dgvm.datamodel import Datamodel
        InstantiateModel.arg_types = (Datamodel,)

    @classmethod
    def execute(cls, vm, model_instance):
        vm.heap.data[id(model_instance)] = model_instance