__author__ = 'salvia'

from threading import Lock

from meta import DatamodelMeta, DatamodelStates
from ..builtin_instructions import InstantiateModel, DestroyInstance


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

        # set the model state to ENGINE_CHANGING, which permits attribute setting without checks and constraints
        self._state = DatamodelStates.ENGINE_CHANGING

        # id is a special snowflake and need separate attention.
        id = self._next_id(vm)
        self._vmattrs['_id']._set_wrapped_value(self, id, id)
        self.id = id

        # for each attribute of this model
        for k, v in self._vmattrs.iteritems():

            # id is a special snowflake and need separate attention. which he got. above.
            if k == '_id':
                continue

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

        # set the model state to NORMAL, which forbids attribute changes.
        self._state = DatamodelStates.NORMAL

        # emit an InstantiateModel instruction to the vm
        self.vm.execute([self.__instantiate_instruction()])

    def is_destroyed(self):
        return self._state == DatamodelStates.DESTROYED

    def destroy(self):
        self.vm.execute([self.__destroy_instruction()])
        self._state = DatamodelStates.DESTROYED

    def __destroy_instruction(self):
        return DestroyInstance(self)

    def __instantiate_instruction(self):
        return InstantiateModel(self, self._vmattrs)

    def _to_user_changing_state(self):
        self._state = DatamodelStates.USER_CHANGING

    def _to_normal_state(self):
        self._state = DatamodelStates.NORMAL

    def data_dict(self, unwrap=False):

        d = {
            'class': type(self).__name__,
            'attributes': []
        }

        for name, attr in self._vmattrs.items():
            val = attr._get_wrapped_data(self)
            if unwrap:
                d['attributes'].append({
                    'class': type(attr).__name__,
                    'name': attr.name,
                    'value': val.data_dict(True) if isinstance(val, Datamodel) else val
                })
            else:
                d['attributes'].append({
                    'class': type(val).__name__ if isinstance(val, Datamodel) else type(attr).__name__,
                    'name': attr.name,
                    'value': val.id if isinstance(val, Datamodel) else val
                })
        return d

    @classmethod
    def _next_id(cls, vm):
        key = cls.__name__ + '/IDCOUNTER'
        val = None

        with Lock() as lock:
            current_id = vm.heap.get(key) or 0
            val = current_id + 1
            vm.heap.set(key, val)

        return val


