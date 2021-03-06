""" Stub module simulating the connection and configuration of the device """
import logging
import time
import random
from abc import abstractmethod
from unittest.mock import MagicMock
from exceptions import DeviceConnectionError, ExecutionCommandError
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
    def _connect(self, port: int = 22):
        pass

    def send_cmd(self, vendor, command: str = 'show version') -> bool | None:
        """
         Sends command to execution
        """
        if self.con:
            logger.info(f"Starting to execute {command} on the {self.name}")
            time.sleep(2)
            if vendor == "juniper":  # pylint: disable=R1705
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
        return None


class JuniperExec(NetExec):  # pylint: disable=too-few-public-methods
    """For juniper devices"""

    def _connect(self, port: int = 22):
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
            raise DeviceConnectionError from e


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
            raise DeviceConnectionError from e


class StubConnection:
    """ Stub class """
    def __init__(self,  ip: str, port: str, device_params: dict,  # pylint: disable=R0913
                 login: str = LOGIN, password: str = PASS,
                 timeout: int = 30, hostkey_verify: bool = True):
        self.ip = ip
        self.login = login
        self.password = password
        self.timeout = timeout
        self.device_params = device_params
        self.hostkey_verify = hostkey_verify
        self.port = port

    def close_session(self):
        """ Close connection """

    def lock(self) -> None:
        """ Lock the configuration"""

    def commit(self) -> None:
        """ Committing the configuration"""

    def unlock(self) -> None:
        """ Unlocking the configuration"""

    def load_configuration(self, action: str = "set", config: str = "show interfaces") -> bool:  # pylint: disable=R0201
        """ Simulate execution """
        time.sleep(2)
        _, _ = action, config
        if random.random() < EXEC_SUCCESS_CHANCE:
            return True
        raise ExecutionCommandError

    def configure_nexus(self, command: str):  # pylint: disable=R0201
        """ Fictional function to configure nexus """
        time.sleep(2)
        _ = command
        if random.random() < EXEC_SUCCESS_CHANCE:
            return True
        raise ExecutionCommandError
