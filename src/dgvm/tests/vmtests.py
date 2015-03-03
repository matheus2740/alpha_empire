import os
import unittest
from src.dgvm.datamodel_meta import ConstraintViolation
from src.dgvm.ipc.client import BaseIPCClient
from src.dgvm.builtin_instructions import BeginTransaction, EndTransaction, InstantiateModel
from src.dgvm.vm import VM
from alpha_empire_test.datamodels import Infantry, Board
__author__ = 'salvia'


class VMTests(unittest.TestCase):

    def test_ipc(self):
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

            client.disconnect()
            pass

    def test_commit(self):

        with VM('alpha_empire_test') as vm:
            i = Infantry(
                vm,
                n_units=1,
                attack_dmg=1,
                armor=0,
                health=1,
                action=10,
                position=(1, 1),
                board=Board(vm, width=20, height=20)
            )

            vm.commit()

            commit = vm.get_last_commit()

            assert commit.hash is not None
            assert isinstance(commit.diff[0], BeginTransaction)
            assert isinstance(commit.diff[1], InstantiateModel)
            assert isinstance(commit.diff[2], InstantiateModel)
            assert isinstance(commit.diff[3], EndTransaction)
            assert vm.heap.data[id(i)] == i

    def test_move(self):

        with VM('alpha_empire_test') as vm:
            i = Infantry(
                vm,
                n_units=1,
                attack_dmg=1,
                armor=0,
                health=1,
                action=10,
                position=(1, 1),
                board=Board(vm, width=20, height=20)
            )

            vm.commit()

            commit = vm.get_last_commit()

            assert commit.hash is not None
            assert isinstance(commit.diff[0], BeginTransaction)
            assert isinstance(commit.diff[1], InstantiateModel)
            assert isinstance(commit.diff[2], InstantiateModel)
            assert isinstance(commit.diff[3], EndTransaction)
            assert vm.heap.data[id(i)] == i

            i.move(2, 2)

            vm.commit()

            commit = vm.get_last_commit()

            assert commit.hash is not None
            assert isinstance(commit.diff[1], Infantry.move)
            assert i.position == (2, 2)
            pass

    def test_constraints(self):

        with VM('alpha_empire_test') as vm:
            i = Infantry(
                vm,
                n_units=1,
                attack_dmg=1,
                armor=0,
                health=1,
                action=1000,
                position=(1, 1),
                board=Board(vm, width=20, height=20)
            )

            try:
                i.move(21, 21)
                assert False
            except ConstraintViolation as e:
                assert e.message == '<AttributeChangedConstraint: board_bounds on board>'

            vm.commit()

            commit = vm.get_last_commit()

            assert commit.hash is not None
            assert isinstance(commit.diff[0], BeginTransaction)
            assert isinstance(commit.diff[1], InstantiateModel)
            assert isinstance(commit.diff[2], InstantiateModel)
            assert isinstance(commit.diff[3], EndTransaction)
            assert vm.heap.data[id(i)] == i
            assert i.position == (1, 1)
            pass

        with VM('alpha_empire_test') as vm:
            i = Infantry(
                vm,
                n_units=1,
                attack_dmg=1,
                armor=0,
                health=1,
                action=10,
                position=(1, 1),
                board=Board(vm, width=200, height=200)
            )

            try:
                i.move(100, 100)
                assert False
            except ConstraintViolation as e:
                assert e.message == '<AttributeChangedConstraint: action_limit on action>'

            vm.commit()

            commit = vm.get_last_commit()

            assert commit.hash is not None
            assert isinstance(commit.diff[0], BeginTransaction)
            assert isinstance(commit.diff[1], InstantiateModel)
            assert isinstance(commit.diff[2], InstantiateModel)
            assert isinstance(commit.diff[3], EndTransaction)
            assert vm.heap.data[id(i)] == i
            assert i.position == (1, 1)
            pass


# TODO: test destroy model

if __name__ == '__main__':
    unittest.main()

