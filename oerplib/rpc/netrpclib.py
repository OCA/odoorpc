# -*- coding: UTF-8 -*-
##############################################################################
#
#    OERPLib
#    Copyright (C) 2011-2013 Sébastien Alix.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
"""This module contains the NetRPC class which implements
the NetRPC protocol.

"""

import socket
import pickle
import cStringIO


class NetRPCError(BaseException):
    """Exception raised by the NetRPC class when an error occured."""
    def __init__(self, faultCode, faultString):
        self.faultCode = faultCode
        self.faultString = faultString
        self.args = (faultCode, faultString)


class NetRPC(object):
    """Low level class for NetRPC protocol."""
    def __init__(self, sock=None, timeout=120):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock
        self.sock.settimeout(timeout)

    def connect(self, host, port=False):
        if not port:
            buf = host.split('//')[1]
            host, port = buf.split(':')
        self.sock.connect((host, int(port)))

    def disconnect(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

    def send(self, msg, exception=False, traceback=None):
        msg = pickle.dumps([msg, traceback])
        size = len(msg)
        self.sock.send('%8d' % size)
        self.sock.send(exception and "1" or "0")
        totalsent = 0
        while totalsent < size:
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise NetRPCError("RuntimeError", "Socket connection broken")
            totalsent = totalsent + sent

    def receive(self):
        buf = ''
        while len(buf) < 8:
            chunk = self.sock.recv(8 - len(buf))
            if chunk == '':
                raise NetRPCError("RuntimeError", "Socket connection broken")
            buf += chunk
        size = int(buf)
        buf = self.sock.recv(1)
        if buf != "0":
            exception = buf
        else:
            exception = False
        msg = ''
        while len(msg) < size:
            chunk = self.sock.recv(size - len(msg))
            if chunk == '':
                raise NetRPCError("RuntimeError", "Socket connection broken")
            msg = msg + chunk
        msgio = cStringIO.StringIO(msg)
        unpickler = pickle.Unpickler(msgio)
        unpickler.find_global = None
        res = unpickler.load()

        if isinstance(res[0], BaseException):
            if exception:
                raise NetRPCError(res[0], res[1])
            raise res[0]
        else:
            return res[0]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
