from datamodel_meta import DatamodelMeta, DatamodelStates
from collections import deque
from builtin_instructions import InstantiateModel, DestroyInstance

__author__ = 'salvia'


required_methods = {}


class InvalidModel(Exception):
    pass


# TODO: implement .objects(.all/.filter)
class Datamodel(object):
    """
        Base class for all models.

    """
    __metaclass__ = DatamodelMeta

    _state = DatamodelStates.NORMAL

    def __init__(self, vm, **kwargs):
        self.vm = vm

        self._state = DatamodelStates.ENGINE_CHANGING
        # TODO: correctly validate default and null
        for k, v in self._vmattrs.iteritems():
            if k in kwargs:
                setattr(self, k, kwargs[k])
            else:
                setattr(self, k, v.val_init())

        self._state = DatamodelStates.NORMAL

        self.vm.emit([self.__instantiate_instruction()])

    def is_destroyed(self):
        return self._state == DatamodelStates.DESTROYED

    def destroy(self):
        self.vm.emit([self.__destroy_instruction()])
        self._state = DatamodelStates.DESTROYED

    def __destroy_instruction(self):
        return DestroyInstance(self)

    def __instantiate_instruction(self):
        return InstantiateModel(self, self._vmattrs)

    def _to_user_changing_state(self):
        self._state = DatamodelStates.USER_CHANGING

    def _to_normal_state(self):
        self._state = DatamodelStates.NORMAL