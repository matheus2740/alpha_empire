import sys

__author__ = 'salvia'


class Goodbye(Exception):
    pass


class IPCServerException(Exception):
    pass


def cmd_goodbye(server, info):
    raise Goodbye


def cmd_shutdown(server, info):
    server.server.harakiri()
    raise Goodbye


def cmd_traceback(client, info):
    print >> sys.stderr, info['traceback']
    raise IPCServerException('IPC Server threw an exception')


def cmd_raise(client, info):
    raise IPCServerException('IPC Server returned an exception: ' + info['exc'])


class Commands(object):
    """
        command = (id, client execution, server execution, execute function)
    """
    GOODBYE      = (1, False, True, cmd_goodbye)
    SHUTDOWN     = (2, False, True, cmd_shutdown)
    TRACEBACK    = (3, True, False, cmd_traceback)
    RAISE        = (4, True, False, cmd_raise)


class Command(object):

    def __init__(self, command, info):
        self.command = command
        self.info = info

    def execute_as_server(self, server):
        if self.command[2]:
            self.command[3](server, self.info)

    def execute_as_client(self, client):
        if self.command[1]:
            self.command[3](client, self.info)

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
