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
        for k, v in self._vmattrs.iteritems():
            # value is passed in ctor, just go ahead
            if k in kwargs and kwargs[k] is not None:
                setattr(self, k, kwargs[k])
            # no value provided in ctor, do we require it?
            else:
                # nope, we don't require it, just leave it as None
                if v.null:
                    setattr(self, k, None)
                # yes we require it, do we have a default value?
                else:
                    # yes we have a default value, use it
                    if v.default:
                        setattr(self, k, v.default)
                    # no we don't have a default value and something is required, so raise and let user fix it.
                    else:
                        self._state = DatamodelStates.NORMAL
                        raise ValueError('Cannot instantiate %s: value for %s is required.' % (type(self).__name__, k,))

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