import sys

__author__ = 'salvia'


class Goodbye(Exception):
    pass


class IPCServerException(Exception):
    pass


def cmd_goodbye(server, info):
    raise Goodbye


def cmd_shutdown(server, info):
    server.harakiri()
    raise Goodbye


def cmd_traceback(client, info):
    print >> sys.stderr, info['traceback']
    raise IPCServerException('IPC Server threw an exception')


def cmd_raise(client, info):
    raise IPCServerException('IPC Server returned an exception: %s, with data: %s' % (info['exc'], info['data']))


def do_nothing(*args, **kwargs):
    pass


def fn_call(server, info):
    return server.fn_call(info[0], info[1], info[2])


def return_arg(client, arg):
    return arg


class Commands(object):
    """
        command = (id, client execution, server execution, execute function)
    """
    GOODBYE      = (1, False, True,  cmd_goodbye)
    SHUTDOWN     = (2, False, True,  cmd_shutdown)
    TRACEBACK    = (3, True,  False, cmd_traceback)
    RAISE        = (4, True,  False, cmd_raise)
    ACK          = (5, True,  True,  do_nothing)
    FN_CALL      = (6, False, True,  fn_call)
    FN_CALL_RES  = (7, True,  False, return_arg)


class Command(object):

    def __init__(self, command, info):
        self.command = command
        self.info = info

    def execute_as_server(self, server):
        if self.command[2]:
            return self.command[3](server, self.info)

    def execute_as_client(self, client):
        if self.command[1]:
            return self.command[3](client, self.info)

    @staticmethod
    def Goodbye():
        return Command(Commands.GOODBYE, {})

    @staticmethod
    def Shutdown():
        return Command(Commands.SHUTDOWN, {})

    @staticmethod
    def Traceback(tb):
        return Command(Commands.TRACEBACK, {
            'traceback': tb
        })

    @staticmethod
    def Raise(exc, data):
        return Command(Commands.RAISE, {
            'exc': exc,
            'data': data
        })

    @staticmethod
    def Ack(message=''):
        return Command(Commands.ACK, {'message': message})

    @staticmethod
    def FunctionCall(name, args, kwargs):
        return Command(Commands.FN_CALL, (name, args, kwargs))

    @staticmethod
    def FunctionCallResponse(result):
        return Command(Commands.FN_CALL_RES, result)
