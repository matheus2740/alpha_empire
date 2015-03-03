from SocketServer import TCPServer, StreamRequestHandler, ThreadingMixIn
from _socket import SHUT_RDWR
from socket import error
from multiprocessing import Process, Value
import os
import select
import errno
import traceback
from protocol import BaseIPCProtocol
from command import Command, Goodbye

__author__ = 'salvia'


class BaseIPCHandler(StreamRequestHandler):

    def handle(self):
        while True:
            self.data = self.server.protocol.recover_message(self.request)

            if self.data is None:
                return

            if isinstance(self.data, Command):
                try:
                    self.data.execute_as_server(self)
                except Goodbye:
                    return
            else:

                fname = self.data['f']
                args = self.data['a']
                kwargs = self.data['kw']

                if fname in self.server._quiver:
                    try:
                        # good path. Funtion exists and returns an object.
                        result = self.server._quiver[fname](*args, **kwargs)
                    except:
                        # function execution throws exception
                        result = Command.Traceback(traceback.format_exc())
                else:
                    # no such funtion
                    result = Command.Raise('no_such_function', self.data)

                BaseIPCProtocol.send_message(self.request, result)


class IPCAvailable(object):
    def __init__(self, ipc_server):
        self.server = ipc_server

    def __call__(self, func):

        self.server.register_functor(func)

        def wrapped(*args):
            result = func(*args)
            return result

        return wrapped


class BaseIPCServer(ThreadingMixIn, TCPServer):
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
    daemon_threads = True
    request_queue_size = 128
    allow_reuse_address = True
    handler = BaseIPCHandler
    protocol = BaseIPCProtocol
    _quiver = {}

    def __init__(self, address=('127.0.0.1', 8998), start=True):
        """
        Initializes the server.
        :param address: (str) The unix socket file path
        :param start: (bool) Flag indicating if the server should startup rightaway.
        """
        self.address = address
        self.deleted_socket_file = False
        self.process = None
        self.shuttingdown = Value('i', 0)
        TCPServer.__init__(self, self.address, self.handler)
        self._started = False
        if start:
            self.startup()

    @staticmethod
    def register_functor(functor, name=None):
        """
        Makes an functor available to client requests.
        If name is provided, the client will the functor through this else,
        functor.__name__ is used.
        Note: if you're registering a lambda expression make sure to pass the name argument, as lambdas are anonymous.
        :param functor: The functor to be registered.
        :param name: (optional) name which will be available to client calls.
        """
        BaseIPCServer._quiver[functor.__name__ if not name else name] = functor

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
        if self.process:
            self.process.terminate()

    def harakiri(self):
        """
        Shuts down the server from the server process itself.
        """
        with self.shuttingdown.get_lock():
            self.shuttingdown.value = 1
        TCPServer.server_close(self)

        os.remove(self.address)
        self.deleted_socket_file = True

        exit(0)

    def __del__(self):
        """
        Delets the lock if shutdown wasn't called.
        """
        self.shutdown()

    def startup(self):
        if self._started:
            return
        self.process = Process(target=self.serve_forever_)
        self.process.daemon = True
        self.process.start()
        self._started = True

    def serve_forever_(self):
        while self.shuttingdown.value == 0:
            self.handle_request()

    # for use in context managers
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
