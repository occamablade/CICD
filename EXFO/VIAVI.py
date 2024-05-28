import socket
import logging
from dataclasses import dataclass
from typing import Union
from time import sleep

from base.Exception import ErrorRemoteConnection


logger = logging.getLogger(__name__)


@dataclass
class ViaviSCPICommands:
    remoteOperation: bytes = b'*REM VISIBLE FULL'
    identifyingInfo: bytes = b'*IDN?'
    curApp: bytes = b':SYST:APPL:CAPP?'
    stopTest: bytes = b':ABOR'
    startTest: bytes = b':INIT'
    selectPortApp: bytes = b':SYST:APPL:SEL %b'
    createSessionApp: bytes = b':SESS:CRE'
    startSessionApp: bytes = b':SESS:STAR'
    selectApp: bytes = b':SYST:APPL:LAUN %b %b'
    systemErr: bytes = b':SYST:ERR?'
    statusTest: bytes = b':SENSE:DATA? TEST:SUMMARY'
    laserON: bytes = b':OUTP:OPT ON'
    laserOFF: bytes = b':OUTP:OPT OFF'
    laserState: bytes = b':OUTP:OPT?'
    exitapp: bytes = b':EXIT'


class MTS5800(ViaviSCPICommands):
    """
    Класс для подключения и управления тестером VIAVI MTS5800

    Само подключение происходит при помощи библиотеки socket.
    Указывается ip-адрес устройства и порт (8006)
    После подключения, необходимо отправить обязательную команду *REM VISIBLE FULL
    так же есть (*REM и *REM VISIBLE). Команда необходима для создания сессии.
    Различия: *REM - управление переходит только скрипту, т.е. UI тестера становится недоступным
              *REM VISIBLE - read-only для UI тестера
              *REM VISIBLE FULL - полное управление и для скрипта, и для UI

    Каждая новая команда должна заканчиваться переносом строки
    """

    def __init__(self, ip: str, port: int) -> None:
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect()

    def connect(self) -> None:
        logger.info('Подключение к тестеру')
        self.sock.settimeout(10)
        try:
            self.sock.connect((self.ip, self.port))
            self.sock.sendall(self.__end(self.remoteOperation))
            self.sock.sendall(self.__end(self.identifyingInfo))
            ans = self.sock.recv(1024).decode()
            if 'JDSU,BERT' not in ans:
                raise ErrorRemoteConnection(f'Нет удалённого управления с тестером [ {self.ip} ]')
        except socket.error as err:
            print(f'При попытке соединения c [ {self.ip}:{self.port} ] произошла ошибка - [ {err} ]')
            logger.exception(f'При попытке соединения c [ {self.ip}:{self.port} ] произошла ошибка - [ {err} ]')

    @staticmethod
    def __end(cmd: bytes) -> bytes:
        return cmd + b'\n'

    def close(self) -> None:
        logger.info('Отключение от тестера')
        self.sock.close()

    def _exit(self):
        logger.info('Закрытие приложения')
        self.sock.sendall(self.__end(self.exitapp))

    def _launch_app(self, traffic, port):
        logger.info('Запуск приложения')
        self.sock.sendall(self.__end(self.selectApp % (traffic, port)))

    def syst_error(self) -> Union[bool, str]:
        self.sock.sendall(self.__end(self.systemErr))
        ans = self.sock.recv(1024).decode()
        if ans.strip('\n') == '0, "No error"':
            return True
        print(ans)
        logger.error(f'Ошибка [ {ans} ]')
        return False

    def _current_app(self) -> list:
        self.sock.sendall(self.__end(self.curApp))
        cur_app = self.sock.recv(1024).decode()
        cur_app_list = cur_app.split(',')
        return cur_app_list

    def _select_app(self, num: int) -> str:
        data = self._current_app()
        app = list(filter(lambda i: int(i[-1]) == num, map(lambda s: s.strip('\n'), data)))
        if not app:
            return f'Запущенных приложений на тестере [ {self.ip} ] нет. Доступные приложения: [ {data} ]'
        self.sock.sendall(self.__end(self.selectPortApp % app[0].encode()))
        if self.syst_error():
            logger.info('Порт выбран успешно. Ошибок нет')

    def _app_session(self) -> None:
        self.sock.sendall(self.__end(self.createSessionApp))
        self.sock.sendall(self.__end(self.startSessionApp))
        if self.syst_error():
            logger.info('Сессия с приложением установлена. Ошибок нет')

    def restart_test(self, port: int) -> None:
        sleep(5)
        self._select_app(port)
        self._app_session()
        self.sock.sendall(self.__end(self.stopTest))
        sleep(5)
        self.sock.sendall(self.__end(self.startTest))

    def simple_restart_test(self, port: int) -> None:
        sleep(5)
        self.sock.sendall(self.__end(self.stopTest))
        sleep(5)
        self.sock.sendall(self.__end(self.startTest))

    def status_test(self, port: int) -> bool:
        sleep(5)
        self._select_app(port)
        self._app_session()
        self.sock.sendall(self.__end(self.statusTest))
        ans = self.sock.recv(1024).decode().strip('\n')
        logger.info(f'Статус теста для порта [ {port} ]: [ {ans} ]')
        print(ans)
        return True if ans == '"normal"' else False

    def simple_status_test(self, port: int) -> bool:
        sleep(5)
        self.sock.sendall(self.__end(self.statusTest))
        ans = self.sock.recv(1024).decode().strip('\n')
        logger.info(f'Статус теста для порта [ {port} ]: [ {ans} ]')
        return True if ans == '"normal"' else False

    def laser_ON(self, port):
        self._select_app(port)
        self._app_session()
        self.sock.sendall(self.__end(self.laserON))
        self.sock.sendall(self.__end(self.laserState))
        ans = self.sock.recv(1024).decode()
        logger.info(f'Лазер на порту [ {port} {ans} ]')

    def simple_laser_ON(self, port):
        self.sock.sendall(self.__end(self.laserON))
        self.sock.sendall(self.__end(self.laserState))
        ans = self.sock.recv(1024).decode()
        logger.info(f'Лазер на порту [ {port} {ans} ]')

    def laser_OFF(self, port):
        self._select_app(port)
        self._app_session()
        self.sock.sendall(self.__end(self.laserOFF))
        self.sock.sendall(self.__end(self.laserState))
        ans = self.sock.recv(1024).decode()
        logger.info(f'Лазер на порту [ {port} {ans} ]')

    def send_rc(self, command, port):
        self._select_app(port)
        self._app_session()
        self.sock.sendall(self.__end(command))
        ans = self.sock.recv(1024).decode()
        return ans

    def simple_send_rc(self, command):
        self.sock.sendall(self.__end(command))
        ans = self.sock.recv(1024).decode()
        return ans

    def send_command(self, command):
        self.sock.sendall(self.__end(command))

