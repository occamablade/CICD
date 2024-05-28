from time import sleep
import logging
import re
import os
import xml.etree.ElementTree as ElT
from typing import Union
import urllib.request
import urllib.parse
from functools import reduce

import requests
from fnmatch import fnmatch, filter
import xmltodict

from Utilities.all import (
    TX_ST_LN, TX_ST_CL, PORT_ST_LN, PORT_ST_CL, LB_ST,
    ADMN, SUP_USER,
    UPLOAD, FW_POSTFIX
)
from Utilities.decorators.timer import execution_time
from base.Exception import InvalidNumberArguments

logger = logging.getLogger(__name__)


class SessionAPI:

    def __init__(self, role: str, url: str) -> None:
        self.role = role
        self.url = f'http://{url}'
        self._auth = self._init_auth()
        self.heading = b'<?xml version="1.0" encoding="utf-8"?>'

    def _user_role(self) -> str:
        return ADMN if self.role == 'admn' else SUP_USER

    def _payload(self, xml_str: Union[bytes, str]) -> dict:
        payload = urllib.parse.urlencode({'xml': xml_str}).encode('ascii')
        connect = {
            'url': self.url,
            'data': payload,
            'unverifiable': False,
            'method': 'POST'
        }
        return connect

    def _read_response(self, resp: dict) -> str:
        """
        Отправка POST запроса на шасси и получение ответа
        """
        try:
            request = urllib.request.Request(**resp)
            response = urllib.request.urlopen(request, timeout=5)
            return response.read().decode('utf-8')
        except Exception as err:
            print(err)
            logger.exception(f'С подключением к шасси [ {self.url} ] произошла проблема')

    def _init_auth(self) -> str:
        logger.info(f'Подключение к шасси [ {self.url} ]')
        user = self._user_role()
        connect = self._payload(user)
        r = self._read_response(connect)
        session_id = xmltodict.parse(r)
        return session_id['RACK']['SESSION_ID']

    def check_response(self, request_: str, val: str) -> None:
        counter = 30
        while counter:
            if self.get_param(request_) == val:
                break
            sleep(5)
            counter -= 1
            logger.info(f'Ожидание ответа. Обратный отсчёт [ {counter} ]')
            self.set_param(request_, val)
        else:
            logger.exception(f'Значение параметра [ {request_.split("_")[-1]} {self.get_param(request_)} ]')
            raise TimeoutError

    @staticmethod
    def parse_set_req(req: str) -> list:
        return req.split(':')

    def _create_logout_xml(self) -> bytes:
        """
        Метод, который составляет XML на выход с шасси.
        """
        xml = ElT.Element('QUERY', dict(Action='Logout'))
        ElT.SubElement(xml, 'SESSION_ID').text = self._auth
        return self.heading + ElT.tostring(xml)

    def _create_get_param_xml(self, parameter: str) -> bytes:
        """
        Метод, который составляет XML на получение
        текущего значения параметра.
        """
        xml = ElT.Element('QUERY', dict(Action='GetParams'))
        ElT.SubElement(xml, 'SESSION_ID').text = self._auth
        ElT.SubElement(xml, 'UID').text = parameter
        return self.heading + ElT.tostring(xml)

    def _create_set_param_xml(self, args: tuple) -> bytes:
        """
        Метод, который составляет XML на установку
        нового значения параметра.
        """
        xml = ElT.Element('QUERY', dict(Action='SetParam'))
        ElT.SubElement(xml, 'SESSION_ID').text = self._auth
        param = ElT.SubElement(xml, 'PARAM', dict(UID=f'{args[0]}'))
        ElT.SubElement(param, 'VALUE').text = args[1]
        return self.heading + ElT.tostring(xml)

    def _create_backup_xml(self, slot: str, devcls: str) -> bytes:
        """
        Метод, который составляет XML на создание
        резервной копии устройства.
        """
        xml = ElT.Element('QUERY', dict(Action='BackupParams'))
        ElT.SubElement(xml, 'SESSION_ID').text = self._auth
        device = ElT.SubElement(xml, 'DEVICE')
        ElT.SubElement(device, 'SLOT').text = slot
        ElT.SubElement(device, 'DEVICE_CLASS').text = devcls
        return self.heading + ElT.tostring(xml)

    def _create_get_param_backup_data(self, slot: str, devcls: str) -> bytes:
        """
        Метод, который составляет XML на получение
        набора параметров и их значений из резервной копии.
        """
        xml = ElT.Element('QUERY', dict(Action='GetParamBackupData'))
        ElT.SubElement(xml, 'SESSION_ID').text = self._auth
        device = ElT.SubElement(xml, 'DEVICE')
        ElT.SubElement(device, 'SLOT').text = slot
        ElT.SubElement(device, 'DEVICE_CLASS').text = devcls
        return self.heading + ElT.tostring(xml)

    def logout(self) -> str:
        """
        Метод выхода с шасси.
        """
        logger.info(f'Выход с шасси [ {self.url} ]')
        connect = self._payload(self._create_logout_xml())
        return self._read_response(connect)

    def get_param(self, param: str) -> str:
        """
        Метод получения значения параметра.
        """
        connect = self._payload(self._create_get_param_xml(parameter=param))
        r = self._read_response(connect)
        value = xmltodict.parse(r)
        return value['RACK']['DEVICE']['PARAM'].get('VALUE', 'Ключ не найден')

    def set_param(self, *args: str) -> dict:
        """
        :param args: принимает две строки. Первая параметр, который нужно изменить, вторая, значение.
        Пример ('rmstc6_4_WSSModule.TempWMax', '50')
        """
        if 1 >= len(args) or len(args) > 2:
            raise InvalidNumberArguments('Неверное число параметров. Должно быть 2. Пример '
                                         '[ rmstc6_4_WSSModule.TempWMax, 50 ]')
        connect = self._payload(self._create_set_param_xml(args))
        r = self._read_response(connect)
        value = xmltodict.parse(r)
        return value

    def get_param_backup_data(self, slot: str, dev_c: str) -> dict:
        """
        Метод, возвращающий словарь с резервной копией слотового устройства
        :param slot: номер слота
        :param dev_c: девайс класс слотового устройства (mjs2, mjm3, mit14)
        """
        connect = self._payload(self._create_get_param_backup_data(slot=slot, devcls=dev_c))
        r = self._read_response(connect)
        value = xmltodict.parse(r)
        only_param_list = list(
            reduce(lambda k, j: k + j, map(lambda x: x['PARAM'], value['RACK']['DEVICE']['SECTION'])))
        only_param_dict = dict(
            zip(map(lambda x: x['NAME'], only_param_list), map(lambda x: x['VALUE'], only_param_list)))
        return only_param_dict

    def backup(self, slot: str, dev_c: str) -> dict:
        """
        Метод, создающий резервную копию слотового устройства
        :param slot: номер слота
        :param dev_c: девайс класс слотового устройства (mjs2, mjm3, mit14)
        :return:
        """
        connect = self._payload(self._create_backup_xml(slot=slot, devcls=dev_c))
        r = self._read_response(connect)
        value = xmltodict.parse(r)
        return value

    def get_param_backup_data_unparse(self, slot: str, dev_c: str):
        """
        Метод, восстанавливающий резервную копию бэкапа устройства
        :param slot: номер слота
        :param dev_c: девайс класс слотового устройства (mjs2, mjm3, mit14)
        """
        connect = self._payload(self._create_get_param_backup_data(slot=slot, devcls=dev_c))
        r = self._read_response(connect)
        r = r.replace('"GetParamBackupData" Result="OK" ErrorCode="0" Msg=""><DEVICE Result="OK" ErrorCode="0">',
                      f'"RestoreParams"><SESSION_ID>{self._auth}</SESSION_ID><DEVICE>')
        root = ElT.fromstring(r)
        tree = ElT.tostring(root, encoding='utf-8')
        con = self._payload(tree)
        q = self._read_response(con)
        return q


class Loopback(SessionAPI):

    def cl_lpbk(self, set_req: str, direction: str) -> None:
        dev, slot, port = self.parse_set_req(set_req)
        logger.info(f'Переход административного состояния в OOS-MT для клиентского порта [ {port} ] на [ {self.url} ] шасси')
        self.set_param(PORT_ST_LN.format(dev, slot, port), '1')
        sleep(3)
        if direction == 'cl':
            self.set_param(LB_ST.format(dev, slot, port), '1')
            self.check_response(LB_ST.format(dev, slot, port), '1')
            logger.info(f'На клиентском порту [ {port} ] [ {self.url} ] шасси установлен loopback "На клиента"')
        elif direction == 'ln':
            self.set_param(LB_ST.format(dev, slot, port), '2')
            self.check_response(LB_ST.format(dev, slot, port), '2')
            logger.info(f'На клиентском порту [ {port} ] [ {self.url} ] шасси установлен loopback "В линию"')
        else:
            print('Либо "cl", либо "ln".')

    def ln_lpbk(self, dev: str, slot: str, direction: str, port: str) -> None:
        logger.info(f'Переход административного состояния в OOS-MT для линейного порта [ {port} ] на [ {self.url} ] шасси')
        self.set_param(PORT_ST_LN.format(dev, slot, port), '1')
        sleep(3)
        if direction == 'cl':
            self.set_param(LB_ST.format(dev, slot, port), '2')
            self.check_response(LB_ST.format(dev, slot, port), '2')
            logger.info(f'На линейном порту [ {port} ] [ {self.url} ] шасси установлен loopback "На клиента"')
        elif direction == 'ln':
            self.set_param(LB_ST.format(dev, slot, port), '1')
            self.check_response(LB_ST.format(dev, slot, port), '1')
            logger.info(f'На линейном порту [ {port} ] [ {self.url} ] шасси установлен loopback "В линию"')
        else:
            print('Либо "cl", либо "ln".')

    def del_lpbk(self, dev: str, slot: str, port: str) -> None:
        logger.info(f'Снятие loopback с [ {port} ] на [ {self.url} ] шасси')
        self.set_param(LB_ST.format(dev, slot, port), '0')
        self.check_response(LB_ST.format(dev, slot, port), '0')
        logger.info(f'Loopback с [ {port} ] на [ {self.url} ] шасси снят')
        self.set_param(PORT_ST_LN.format(dev, slot, port), '2')
        self.check_response(PORT_ST_LN.format(dev, slot, port), '2')


class ManagePort(SessionAPI):

    def lock(self, set_req: str) -> None:
        dev, slot, port = self.parse_set_req(set_req)
        logger.info(f'Выключение порта [ {port} ] на [ {self.url} ] шасси')
        self.set_param(PORT_ST_LN.format(dev, slot, port), '1')
        self.check_response(PORT_ST_LN.format(dev, slot, port), '1')
        self.set_param(PORT_ST_LN.format(dev, slot, port), '0')
        self.check_response(PORT_ST_LN.format(dev, slot, port), '0')
        logger.info(f'Порт [ {port} ] на [ {self.url} ] шасси выключен')

    def maintenance_ln_port(self, dev: str, slot: str, port: str) -> None:
        logger.info(f'Переход в OOS-MT линейного порта [ {port} ] на [ {self.url} ] шасси')
        self.set_param(PORT_ST_LN.format(dev, slot, port), '1')
        self.check_response(PORT_ST_LN.format(dev, slot, port), '1')
        logger.info(f'Линейный порт [ {port} ] на [ {self.url} ] шасси переведен в OOS-MT')

    def maintenance_cl_port(self, dev: str, slot: str, port: str) -> None:
        logger.info(f'Переход в OOS-MT клиентского порта [ {port} ] на [ {self.url} ] шасси')
        self.set_param(PORT_ST_CL.format(dev, slot, port), '1')
        self.check_response(PORT_ST_CL.format(dev, slot, port), '1')
        logger.info(f'Клиентский порт [ {port} ] на [ {self.url} ] шасси переведен в OOS-MT')

    def unlock_ln_port(self, dev: str, slot: str, port: str) -> None:
        logger.info(f'Включение линейного порта [ {port} ] на [ {self.url} ] шасси')
        self.set_param(PORT_ST_LN.format(dev, slot, port), '1')
        self.check_response(PORT_ST_LN.format(dev, slot, port), '1')
        self.set_param(PORT_ST_LN.format(dev, slot, port), '2')
        self.check_response(PORT_ST_LN.format(dev, slot, port), '2')
        logger.info(f'Линейный порт [ {port} ] на [ {self.url} ] шасси включен')
        logger.info(f'Включение передатчика линейного порта [ {port} ] на [ {self.url} ] шасси')
        self.set_param(TX_ST_LN.format(dev, slot, port), '1')
        self.check_response(TX_ST_LN.format(dev, slot, port), '1')
        logger.info(f'Передатчик на линейном порту [ {port} ] на [ {self.url} ] шасси включен')

    def unlock_cl_port(self, dev: str, slot: str, port: str) -> None:
        logger.info(f'Включение клиентского порта [ {port} ] на [ {self.url} ] шасси')
        self.set_param(PORT_ST_CL.format(dev, slot, port), '1')
        self.check_response(PORT_ST_CL.format(dev, slot, port), '1')
        self.set_param(PORT_ST_CL.format(dev, slot, port), '2')
        self.check_response(PORT_ST_CL.format(dev, slot, port), '2')
        logger.info(f'Клиентский порт [ {port} ] на [ {self.url} ] шасси включен')
        logger.info(f'Включение передатчика клиентского порта [ {port} ] на [ {self.url} ] шасси')
        self.set_param(TX_ST_CL.format(dev, slot, port), '1')
        self.check_response(TX_ST_CL.format(dev, slot, port), '1')
        logger.info(f'Передатчик на клиентском порту [ {port} ] на [ {self.url} ] шасси включен')

    def tx_on_ln(self, dev: str, slot: str, port: str) -> None:
        logger.info(f'Включение передатчика линейного порта [ {port} ] на [ {self.url} ] шасси')
        self.set_param(TX_ST_LN.format(dev, slot, port), '1')
        self.check_response(TX_ST_LN.format(dev, slot, port), '1')
        logger.info(f'Передатчик на линейном порту [ {port} ] на [ {self.url} ] шасси включен')

    def tx_on_cl(self, dev: str, slot: str, port: str) -> None:
        logger.info(f'Включение передатчика клиентского порта [ {port} ] на [ {self.url} ] шасси')
        self.set_param(TX_ST_CL.format(dev, slot, port), '1')
        self.check_response(TX_ST_CL.format(dev, slot, port), '1')
        logger.info(f'Передатчик на клиентском порту [ {port} ] на [ {self.url} ] шасси включен')

    def tx_off_ln(self, dev: str, slot: str, port: str) -> None:
        logger.info(f'Выключение передатчика линейного порта [ {port} ] на [ {self.url} ] шасси')
        self.set_param(TX_ST_LN.format(dev, slot, port), '0')
        self.check_response(TX_ST_LN.format(dev, slot, port), '0')
        logger.info(f'Передатчик на линейном порту [ {port} ] на [ {self.url} ] шасси выключен')

    def tx_off_cl(self, dev: str, slot: str, port: str) -> None:
        logger.info(f'Выключение передатчика клиентского порта [ {port} ] на [ {self.url} ] шасси')
        self.set_param(TX_ST_CL.format(dev, slot, port), '0')
        self.check_response(TX_ST_CL.format(dev, slot, port), '0')
        logger.info(f'Передатчик на клиентском порту [ {port} ] на [ {self.url} ] шасси выключен')


class Upload(SessionAPI):

    @staticmethod
    def find_fw() -> list[str]:
        fws = []
        for root, dirs, files in os.walk(os.getcwd()):
            [fws.append(os.path.join(root, file)) for file in filter(files, FW_POSTFIX)]

        return fws

    @staticmethod
    def installable_fw_version(not_prepared_fw) -> str:
        # return [fw.split('_')[-1].rstrip('.s19') for fw in self.find_fw()]
        return not_prepared_fw.split('_')[-1].replace('.s19', '')

    @execution_time
    def update_slot(self, dc: str, slot: str, firmware: str) -> None:
        """
        Пример при помощи curl: curl -X POST -F 'session_id=id активной сессии' \
                                            -F 'type=firmware' \
                                            -F 'file=@сама ВПО' \
                                            -F 'slot=номер слота' \
                                            http://192.168.31.194/upload.php
        :return:
        """
        chs = '.'.join(self.url.split('.')[-2::])
        # sw_name = self.find_fw()[0]

        logger.info(f'Установка версии ВПО [ {firmware} ] на [ {slot} слот ] [ шасси 192.168.{chs} ]')
        with open(firmware, 'rb') as f:
            file = {'file': f}

            content = {
                'session_id': self._auth,
                'type': 'firmware',
                'slot': slot
            }
            try:
                response = requests.post(UPLOAD.format(chs), data=content, files=file)
            except requests.exceptions.HTTPError as er:
                logger.exception(er)

            parseAnswer = re.sub(r'[></?]', ' ', response.text).split()
            *_, msg, err, result = parseAnswer
            assert result == 'Result="OK"', (msg, err)
            logger.info(
                f'ВПО [ {firmware} ] успешно отправлено на [ {slot} слот ] [ шасси 192.168.{chs} ] [ {msg}; {err} ]')

            try:
                self.check_response(f'{dc}_{slot}_SwNumber', self.installable_fw_version(firmware))
            except TimeoutError as te:
                logger.exception(
                    f'{te}. За 10 минут ВПО [ {firmware} ] не установилось на [ {slot} слот ] [ шасси 192.168.{chs} ]')
            else:
                logger.info(
                    f'ВПО [ {firmware} ] успешно установлено на [ {slot} слот ] [ шасси 192.168.{chs} ] [ {msg}; {err} ]')


class Facade(Loopback, ManagePort, Upload):
    pass
