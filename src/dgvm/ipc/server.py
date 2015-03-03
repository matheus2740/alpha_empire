from SocketServer import TCPServer, StreamRequestHandler, ThreadingMixIn
from _socket import SHUT_RDWR
import socket
from socket import error
from multiprocessing import Process, Value
import sys
import select
import errno
from threading import Thread
import traceback
from protocol import BaseIPCProtocol
from command import Command, Goodbye

__author__ = 'salvia'


class IPCAvailable(object):
    def __init__(self, ipc_server):
        self.server = ipc_server

    def __call__(self, func):

        self.server.register_functor(func)

        def wrapped(*args):
            result = func(*args)
            return result

        return wrapped


def f_startup(instance):
    instance.startup(should_fork=False)


class TCPIPCServer(object):
    daemon_threads = True
    request_queue_size = 128
    allow_reuse_address = True

    def __init__(self, ipc_server):
        self.shuttingdown = Value('i', 0)
        self.ipc_server = ipc_server
        self.timeout = 100
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(ipc_server.address)
        self.server_address = self.socket.getsockname()
        self.socket.listen(self.request_queue_size)

    def shutdown(self):
        """
        Shuts down the server.
        """
        with self.shuttingdown.get_lock():
            self.shuttingdown.value = 1

        try:
            self.socket.shutdown(SHUT_RDWR)
        except error:
            pass
        self.socket.close()

    def serve_forever_(self):
        while self.shuttingdown.value == 0:
            fd_sets = _eintr_retry(select.select, [self.socket], [], [], self.timeout)
            if not fd_sets[0]:
                continue
            try:
                request_socket, client_address = self.socket.accept()
            except socket.error:
                return

            t = Thread(target=self.handle, args=(request_socket,))
            t.daemon = True
            t.start()

    def handle(self, request_socket):
        sv = self.ipc_server
        while True:
            data = sv.protocol.recover_message(request_socket)

            if data is None:
                return

            if isinstance(data, Command):
                try:
                    data.execute_as_server(self)
                except Goodbye:
                    sv.protocol.send_message(request_socket, Command.Ack())
                    return
            else:

                fname = data['f']
                args = data['a']
                kwargs = data['kw']

                if fname in sv._quiver:
                    try:
                        # good path. Funtion exists and returns an object.
                        result = sv._quiver[fname](*args, **kwargs)
                    except:
                        # function execution throws exception
                        result = Command.Traceback(traceback.format_exc())
                else:
                    # no such funtion
                    result = Command.Raise('no_such_function', data)

                sv.protocol.send_message(request_socket, result)


class BaseIPCServer(object):
    """
    Threaded inter-process communication server. This server itself WON'T run in the process
    which initializes this class, it will run in a separate child process, so the initializer
    process (the one that instantiates this class) may do non related work.
    The child process opened, which is the server itself, will open a new thread for every client connected
    to it, and close the thread as soon as the client disconnects.

    To inherit from this, the following properties are noteworthy:
    :class attribute handler: The requisition handler class, defaults to BaseIPCHandler
     which is adequate for most scenarios.
    :class attribute protocol: The class in charge of serializing, deserializing, sending and
     retrieving information to and from the socket, defaults to BaseIPCProtocol which uses pickling.
    """

    protocol = BaseIPCProtocol
    _quiver = {}

    def __init__(self, address=('127.0.0.1', 8998), start=True):
        """
        Initializes the server.
        :param address: (str) The unix socket file path
        :param start: (bool) Flag indicating if the server should startup rightaway.
        """
        self.address = address
        self.process = None
        self._started = False
        self.tcp_server = None
        if start:
            self.startup()

    @classmethod
    def register_functor(cls, functor, name=None):
        """
        Makes an functor available to client requests.
        If name is provided, the client will the functor through this else,
        functor.__name__ is used.
        Note: if you're registering a lambda expression make sure to pass the name argument, as lambdas are anonymous.
        :param functor: The functor to be registered.
        :param name: (optional) name which will be available to client calls.
        """
        cls._quiver[functor.__name__ if not name else name] = functor

    def startup(self, should_fork=True):

        if should_fork:
            if sys.platform == 'win32':
                self.process = Thread(target=f_startup, args=(self,))
            else:
                self.process = Process(target=f_startup, args=(self,))
            self.process.daemon = True
            self.process.start()
        else:
            if self._started:
                return
            self.tcp_server = TCPIPCServer(self)
            self.tcp_server.serve_forever_()
            self._started = True

    def shutdown(self):
        from client import BaseIPCClient
        c = BaseIPCClient(address=self.address)
        c.shutdown()

    def __enter__(self):
        self.startup()
        return self

    # for use in context managers
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()


# This function is present on cpython but not pypy stdlib. I've added it here for pypy compatibility.
def _eintr_retry(func, *args):
    """restart a system call interrupted by EINTR"""
    while True:
        try:
            return func(*args)
        except (OSError, select.error) as e:
            if e.args[0] != errno.EINTR:
                raise
