from instruction import Instruction

__author__ = 'salvia'


class BeginTransaction(Instruction):
    # BEGINTRANS
    opcode = 1
    mnemonic = 'VM_BEGINTRANS'
    n_args = 0
    arg_types = tuple()

    @classmethod
    def execute(cls, *args):
        pass


class EndTransaction(Instruction):
    # ENDTRANS
    opcode = 2
    mnemonic = 'VM_ENDTRANS'
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
        from dgvm.datamodel import Datamodel
        type(self).arg_types = (Datamodel, dict)
        super(InstantiateModel, self).__init__(*args)

    @classmethod
    def execute(cls, vm, model_instance, attrs):
        pass


class DestroyInstance(Instruction):
    # DESTROY model_instance
    opcode = 4
    mnemonic = 'DESTROY'
    n_args = 1
    arg_types = (object,)

    def __init__(self, *args):
        from dgvm.datamodel import Datamodel
        type(self).arg_types = (Datamodel,)
        super(DestroyInstance, self).__init__(*args)

    @classmethod
    def execute(cls, vm, model_instance):

        for name, attr in model_instance._vmattrs.items():
            attr._destroy(model_instance)


#TODO: implement CollapseHeap, an instruction which collapses all treects in the Heap, saving memory and access time,
#TODO: but making commit undo impossible.