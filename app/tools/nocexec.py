""" Stub module simulating the connection and configuration of the device """
import logging
import time
import random
from exceptions import DeviceConnectionError, ExecutionCommandError
from abc import abstractmethod
from unittest.mock import MagicMock
from ncclient import manager


LOGIN = "admin"
PASS = "password"
CONN_SUCCESS_CHANCE = 0.9
EXEC_SUCCESS_CHANCE = 0.9

logger = logging.getLogger("CApi")


class NetExec:  # pylint: disable=too-few-public-methods
    """Class of the execution on the net devices"""

    def __init__(self, name: str, ip: str, login: str = LOGIN, password: str = PASS):
        self.name = name
        self.ip = ip
        self.login = login
        self.password = password
        self.con = self._connect()

    @abstractmethod
    def _connect(self):
        pass

    def send_cmd(self, vendor, command: str = 'show version') -> bool | None:
        """
         Sends command to execution
        """
        if self.con:
            logger.info(f"Starting to execute {command} on the {self.name}")
            time.sleep(2)
            if vendor == "juniper":
                self.con.lock(self)
                if self.con.load_configuration(self, action="set", config=command):
                    self.con.commit(self)
                    self.con.unlock(self)
                    self.con.close_session(self)
                    return True
                return False
            elif vendor == "cisco":
                if self.con.configure_nexus(self, command):
                    return True
                return False


class JuniperExec(NetExec):  # pylint: disable=too-few-public-methods
    """For juniper devices"""

    def _connect(self, port=22):
        try:
            manager.connect = MagicMock(return_value=StubConnection)
            return manager.connect(host=self.ip,
                                   port=port,
                                   username=self.login,
                                   password=self.password,
                                   timeout=5,
                                   device_params={'name': 'junos'},
                                   hostkey_verify=False)
        except Exception as e:
            logger.error(f'SSHSession error {e}')
            raise DeviceConnectionError


class CiscoExec(NetExec):  # pylint: disable=too-few-public-methods
    """For Cisco devices"""

    def _connect(self, port=22):
        try:
            manager.connect = MagicMock(return_value=StubConnection)
            return manager.connect(host=self.ip,
                                   port=port,
                                   username=self.login,
                                   password=self.password,
                                   timeout=5,
                                   device_params={'name': 'nexus'},
                                   hostkey_verify=False)
        except Exception as e:
            logger.error(f'SSHSession error {e}')
            raise DeviceConnectionError


class StubConnection:
    """ Stub class """
    def __init__(self,  ip: str, port: str, login: str = LOGIN, password: str = PASS,
                 timeout: int = 30, device_params: dict = {}, hostkey_verify: bool = True):
        self.ip = ip
        self.login = login
        self.password = password
        self.timeout = timeout
        self.device_params = device_params
        self.hostkey_verify = hostkey_verify

    def close_session(self):
        """ Close connection """
        pass

    def lock(self) -> None:
        """ Lock the configuration"""
        pass

    def commit(self) -> None:
        """ Committing the configuration"""
        pass

    def unlock(self) -> None:
        """ Unlocking the configuration"""
        pass

    def load_configuration(self, action: str = "set", config: str = "show interfaces") -> bool:
        """ Simulate execution """
        time.sleep(2)
        _, _ = action, config
        if random.random() < EXEC_SUCCESS_CHANCE:
            return True
        raise ExecutionCommandError

    def configure_nexus(self, command: str):
        """ Fictional function to configure nexus """
        time.sleep(2)
        _ = command
        if random.random() < EXEC_SUCCESS_CHANCE:
            return True
        raise ExecutionCommandError