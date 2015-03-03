import os
import unittest
from src.dgvm.instantiate_model import Instantiate
from src.dgvm.ipc.client import BaseIPCClient
from src.dgvm.tests.alpha_empire_test.datamodels import Infantry
from src.dgvm.transaction import BeginTransaction, EndTransaction

__author__ = 'salvia'


class VMTests(unittest.TestCase):

    def test_ipc(self):
        from src.dgvm.vm import VM
        # simple square function
        VM.square = staticmethod(lambda x: x ** 2)
        VM.register_functor(VM.square, 'square')

        # getpid function, we must make sure the VM is in another process
        VM.pid = staticmethod(lambda: os.getpid())
        VM.register_functor(VM.pid, 'pid')

        with VM('alpha_empire_test') as vm:
            client = BaseIPCClient()

            assert client.square(2) == 4
            assert client.square(3) == 9
            assert client.square(4) == 16

            assert os.getpid() != client.pid()

            client.disconnect()

    def test_commit(self):
        from src.dgvm.vm import VM

        with VM('alpha_empire_test') as vm:
            i = Infantry()
            i.n_units = 1
            i.attack_dmg = 1
            i.armor = 0
            i.health = 1
            i.action = 10
            i.position = (1, 1)
            i.save(vm)

            vm.commit()

            commit = vm.get_last_commit()

            assert commit.hash is not None
            assert isinstance(commit.diff[0], BeginTransaction)
            assert isinstance(commit.diff[1], Instantiate)
            assert isinstance(commit.diff[2], EndTransaction)
            assert vm.heap.data[id(i)] == i

            i.position = (2, 2)

            vm.commit()


if __name__ == '__main__':
    unittest.main()