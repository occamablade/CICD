import time
from dataclasses import dataclass, asdict
from typing import Any
import logging

import xmltodict
from ncclient import manager
# from ncclient.manager import OPERATIONS
from ncclient.transport import SSHError, SessionCloseError
from ncclient.transport.errors import AuthenticationError, SessionError

from base.NMS.data import (
    OduState,
    OtuState,
    OpticsState,
    SlotState,
    PortState,
    Info, RoadmConnections
)
# from xmlbody import XmlData
from base.NMS.xmlbody import XmlData

logger = logging.getLogger(__name__)


@dataclass
class Xpath:
    sens: str = '/sen/sensors/sensor[object-class="{}"][object="{}"][sensor-name="{}"]/value'


class NetconfCli(Xpath):

    def __init__(self, url: str, login: str, password: str, port: int = 830):
        self.url = url
        self.login = login
        self.password = password
        self.port = port
        self.conn = self.connect()
        self.odu_st = OduState()
        self.otu_st = OtuState()
        self.opt_st = OpticsState()
        self.slot_st = SlotState()
        self.port_st = PortState()
        self.info = Info()
        self.nmc = RoadmConnections()
        # self.cp = CP()

    # @staticmethod
    # def _check_response(reply):
    #     assert reply.ok, ' List of RPCError \n\t\t {}'.format(reply.errors)
    #     parse_data = xmltodict.parse(reply.xml)['rpc-reply']['data']
    #     return parse_data if parse_data else dict()

    def connect(self):
        """
        Function to connect to a node
        :return:
        """

        start = time.time()
        elapsed = 0
        while elapsed < 300:
            try:
                mg = manager.connect(host=self.url, port=self.port,
                                     username=self.login, password=self.password,
                                     hostkey_verify=False, timeout=120)
                break
            except (SSHError, AuthenticationError, SessionCloseError, SessionError) as e:
                logging.error(f'Exception was caught: "{e}". Reconnect to {self.url}')
                elapsed = time.time() - start
                time.sleep(20)
        else:
            raise SSHError("Could not open socket to %s:%s" % (self.url, self.port))

        return mg

    def _separator(self, aid: str) -> dict[str, Any]:

        prefix = aid.split('-')[0]
        match prefix:
            case 'PPM' | 'MPDR' | 'FU' | 'CU' | 'EA' | 'OAMP' | 'PS' | 'ROADM' | 'SLOT':
                xpath = self.slot_st
            case 'OPT':
                xpath = self.opt_st
            case 'OTU':
                xpath = self.otu_st
            case 'ODU':
                xpath = self.odu_st
            case 'OAIN' | 'OAOUT' | 'OSC' | 'XPC' | 'XPL' | 'OSC' | 'OMC' | 'ODC' | 'OML' | 'ODL' | 'OADMG' | 'GE':
                xpath = self.port_st
            case 'NMC' | 'NMCC' | 'ROADMG' | 'DEGR':
                xpath = self.nmc
            case _:
                raise ValueError('Unknown prefix')

        return asdict(xpath)

    def check_nms_response(self, aid: str, name_state: str, val: str):
        # TODO ещё не сделано
        counter = 300
        while counter:
            if self.get_state(aid=aid, name_state=name_state) == val:
                break
            time.sleep(3)
            counter -= 1
            logger.info(f'Ожидание ответа. Обратный отсчёт [ {counter} ]')
            print(f'Ожидание ответа. Обратный отсчёт [ {counter} ]')
        else:
            raise TimeoutError

    def get_sensor(self, aid: str, sens_name: str) -> str:
        """

        :param aid: aid interface for which you need to get the sensor value, e.g. XPL-1-1-8-0-LINE1
        :param sens_name: sensor name, e.g. input-power, input-current, case-temperature
        :return:
        """
        prefix = aid.split('-')[0]
        match prefix:
            case 'PPM' | 'MPDR' | 'FU' | 'CU' | 'EA' | 'OAMP' | 'PS' | 'ROADM':
                obj_cls = 'EmCpk'
            case 'OPT' | 'OTU' | 'ODU':
                obj_cls = 'EmIf'
            case 'OAIN' | 'OAOUT' | 'OSC' | 'XPC' | 'XPL':
                obj_cls = 'EmPort'
            case _:
                raise ValueError('Unknown prefix')

        replay = self.conn.get(filter=('xpath', self.sens.format(obj_cls, aid, sens_name)))
        parse_value = xmltodict.parse(replay.xml)['rpc-reply']['data']['sen']['sensors']['sensor']['value']

        return parse_value

    def get_state(self, aid: str, name_state: str):
        """

        :param aid: Аид объекта
        :param name_state: это ключ, который нужно смотреть в модуле data.py
        :return:
        """

        state_xpath = self._separator(aid=aid)
        r = state_xpath.get(name_state).format(aid)
        _, _, intrfcs, intrfc, *_ = r.split('/')
        replay = self.conn.get(filter=('xpath', r))
        parse_value = xmltodict.parse(replay.xml)['rpc-reply']['data']['em'][f'{intrfcs}'][f'{intrfc.split("[")[0]}']

        if 'optics' in parse_value:
            return parse_value['optics']
        elif 'otu' in parse_value:
            return parse_value['otu']
        elif 'odu' in parse_value:
            return parse_value['odu']

        return parse_value

    def __select_info(self, val: str):

        selection_dict: dict = {
            'model': (self.info.module_prt_number, 'model'),
            'serial': (self.info.serial_number, 'serial-number'),
            'vendor': (self.info.vendor, 'vendor'),
            'rev': (self.info.software_rev, 'software-revision')
        }

        return selection_dict[val] if val in selection_dict.keys() else None

    def get_info(self, aid: str, type_: str) -> str:
        """

        :param aid: AID по которому ты хочешь получить инфо
        :param type_: какую инфо ты хочешь получить (
                                                    model - модель уст-ва или парт номер,
                                                    serial - серийный номер,
                                                    vendor - вендор устройства,
                                                    rev - software revision)
        :return:
        """

        r, t = self.__select_info(val=type_)
        replay = self.conn.get(filter=('xpath', r))
        parse_value = xmltodict.parse(replay.xml)['rpc-reply']['data']['em']['circuit-packs']['circuit-pack']

        if parse_value:
            for item in parse_value:
                if item['aid'] == aid:
                    return item['info']['common'][t]
                else:
                    continue
        else:
            return f'Список [ {parse_value} ] пуст'

    def edit_conf_and_commit(self, xml):

        reply = self.conn.edit_config(target='candidate', config=xml)
        assert reply.ok, ' List of RPCError \n\t\t {}'.format(reply.errors)
        parse_data = xmltodict.parse(reply.xml)
        assert 'ok' in parse_data['rpc-reply']
        self.conn.commit()

    def disconnect(self):
        self.conn.close_session()
