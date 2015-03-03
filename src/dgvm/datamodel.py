from datamodel_meta import DatamodelMeta, VMAttribute
from collections import deque
from src.dgvm.instantiate_model import Instantiate

__author__ = 'salvia'


required_methods = {}


class InvalidModel(Exception):
    pass


class Events(object):
    INSTANCED = 0


class Datamodel(object):
    __metaclass__ = DatamodelMeta

    def __init__(self, **kwargs):
        self.log = deque([self.instantiate()])
        pass

    def __del__(self):
        pass

    def instantiate(self):
        return Instantiate(self, self._vmattrs)

    def parse_log(self):
        pass

    def clear_log(self):
        self.log = deque()

    def save(self, vm):
        self.parse_log()
        vm.emit(self.log)
        self.clear_log()