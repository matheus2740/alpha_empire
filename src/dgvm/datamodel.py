from datamodel_meta import DatamodelMeta, DatamodelStates
from collections import deque
from builtin_instructions import InstantiateModel

__author__ = 'salvia'


required_methods = {}


class InvalidModel(Exception):
    pass


class Events(object):
    INSTANCED = 0


class Datamodel(object):
    """
        Base class for all models.

        NOTE:
            self.log is a sequence that builds up instructions over the object lifetime, until .save is called,
            at which point these instructions are going to be passed on the the VM.
    """
    __metaclass__ = DatamodelMeta

    _state = DatamodelStates.NORMAL

    def __init__(self, vm, **kwargs):
        self.vm = vm
        self.log = deque()

        self._state = DatamodelStates.ENGINE_CHANGING

        for k, v in self._vmattrs.iteritems():
            if k in kwargs:
                setattr(self, k, kwargs[k])
            else:
                setattr(self, k, v.val_init())

        self._state = DatamodelStates.NORMAL

        self.vm.emit([self.instantiate()])

    def __del__(self):
        pass

    def instantiate(self):
        return InstantiateModel(self, self._vmattrs)

    def clear_log(self):
        self.log = deque()

    def _to_user_changing_state(self):
        self._state = DatamodelStates.USER_CHANGING

    def _to_normal_state(self):
        self._state = DatamodelStates.NORMAL