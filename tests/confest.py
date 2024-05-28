import json
import logging
from datetime import datetime, timedelta
from time import perf_counter, sleep
from operator import itemgetter as ig
import csv
import os
from typing import Literal, Union
from dataclasses import dataclass

import pytest
import pytz
from py.xml import html
from fnmatch import fnmatch
from playwright.sync_api import sync_playwright
from deepdiff import DeepDiff

from EXFO.exfo import Exfo
from EXFO.VIAVI import MTS5800
from base.Atlas.atlas import Facade
from base.SSHConnect.sshconnect import SshConn
from Utilities.all import (
    DELAY, DURATION, PERIOD,
    WAIT, TITLE, FW_POSTFIX, LINE_PORT, LINE_OPT,
    URL_LOGIN_NMS,
    IP, NODE_ID, NODE_NAME, TEST_NODE, ADM_ST, USER_FOR_NE,
    PASSWD_FOR_NE, PORT, TEST_PASSWD_NMS, TEST_LOGIN_NMS,
    CHANGE_IP, CHANGE_PORT, REBOOT_VAL, WAIT_REBOOT,
    CHANGE_IP, CHANGE_PORT,
    PING_DATA, TRACEROUTE_DATA, TESTING_SLOT_NAME, NODE_NAME1,
    IP_TUNNEL_DATA1, IP_TUNNEL_DATA2, USER, PASSW
)
from base.config.cfg import Cfg23Chs
from base.NMS.nms import NetconfCli
from base.NMS.xmlbody import XmlData
from base.Update.swm import SWM
from base.NMS.nms_api import Backup

logger = logging.getLogger(__name__)

@dataclass
class Command:
    section_5: str = 'cat /tmp/atlas/data/{}/t5'

# ---------------------------------
# Pytest
# ---------------------------------
def pytest_addoption(parser):
    parser.addoption('--reboot_slot', action='append', default=[],
                     help='Полная запись команды для перезагрузки слотового устройства. Пример "dnepr3_10_Slot6Restart"'
                          'для Атлас или aid слота для NMS')
    parser.addoption('--backup_slot', action='store', default='', help='Номер слота для которого нужно сделать backup')
    parser.addoption('--module', action='store', default=int, help='Модуль на EXFO тестере')
    parser.addoption('--bert', action='append', default=[], help='IP адрес тестера')
    parser.addoption('--dev_cls', action='store', default='', help='Девайс класс устройства. Пример "mjstc3"')
    parser.addoption('--reboot_mode', action='append', default=[], help='Либо "cold", либо "warm"')
    parser.addoption('--node_id', action='append', default=[], help='Имя узла')
    parser.addoption('--slot', action='store', default='', help='Номер слота где установлено устройство')
    parser.addoption('--cnt', action='store', default='1', help='Число перезагрузок слотового устройства')
    parser.addoption('--upd_slot', action='store', default='', help='Номер слота для обновления')
    parser.addoption('--line_port', action='store', default='1', help='Номер слота для обновления')
    parser.addoption('--chs', action='append', default=[], help='IP адрес шасси')
    parser.addoption('--tr_type', action='store', default='0', help='Тип клиентского трафика для настройки AZOV2S.'
                                                                    '0 - это 10GE(7.3)'
                                                                    '1 - это STM64 '
                                                                    '2 - это OTU2'
                                                                    '3 - это OTU2E'
                                                                    '4 - это 8FC'
                                                                    '5 - это 10FC'
                                                                    '6 - это 10GE(6.2)')
    parser.addoption('--half', action='store', default='',
                     help='Для настройки клиентского трафика 2-х типов (пополам) для настройки AZOV2S.'
                          '0 - это 10GE(7.3)'
                          '4 - это 8FC')
    parser.addoption('--mask', action='store', default='0',
                     help='Выбор трибутарного порта через параметр ATPMux1OPUTpSelect или ATPMux1OPUTsMaskSet'
                          '0 - По умолчанию настраивается через ATPMux[*]OPUTpSelect'
                          '1 - Настраивается через ATPMux[*]OPUTsMaskSet')
    parser.addoption('--slots', action='store', default='',
                     help='Номера слотов. Если в одном шасси используется 2 и более слотовых устройств')


@pytest.fixture
def option_args(request) -> dict[str, any]:
    option_dict = {
        'chs': request.config.getoption('chs'),
        'upd_slot': request.config.getoption('upd_slot'),
        'dev_cls': request.config.getoption('dev_cls'),
        'backup_slot': request.config.getoption('backup_slot'),
        'reboot_slot': request.config.getoption('reboot_slot'),
        'tr_type': request.config.getoption('tr_type'),
        'half': request.config.getoption('half').split(','),
        'slot': request.config.getoption('slot'),
        'mask': request.config.getoption('mask'),
        'slots': request.config.getoption('slots').split(','),
        'reboot_mode': request.config.getoption('reboot_mode'),
        'node_id': request.config.getoption('node_id'),
        'module': request.config.getoption('module'),
        'bert': request.config.getoption('bert'),
        'cnt': request.config.getoption('cnt'),
        'line_port': request.config.getoption('line_port'),
    }
    return option_dict


# ---------------------------------
# BERT
# ---------------------------------
@pytest.fixture(scope='class')
def exfoftb(option_args):
    exfoftb = Exfo(exfo_ip=''.join(option_args.get('bert')), module=option_args.get('module'))
    yield exfoftb
    exfoftb.close()


@pytest.fixture
def ppm(exfoftb, request):
    exfoftb.stop_test_for_module()
    exfoftb.set_ppm(request.param)
    exfoftb.manage_offset('ON')
    exfoftb.start_test_for_module()
    sleep(5)
    exfoftb.reset_test_for_module()
    logger.info(f'Ждём [ {WAIT} сек ]')
    sleep(WAIT)
    yield exfoftb
    exfoftb.manage_offset('OFF')


@pytest.fixture
def mts5800(option_args):
    ber = MTS5800(ip=''.join(option_args.get('bert')), port=8006)
    yield ber
    ber.close()


# ---------------------------------
# SSH
# ---------------------------------
@pytest.fixture
def ssh_connect(option_args):
    ssh = SshConn(*option_args['chs'], user=USER, password=PASSW)
    logger.info(f'SSH сессия с {option_args.get("chs")} открыта')
    yield ssh
    logger.info(f'Закрытие SSH сессии с {option_args.get("chs")}')
    ssh.logout()


@pytest.fixture
def get_5_section(ssh_connect, option_args):
    section_5 = ssh_connect.command(Command.section_5.format(option_args.get('slot')))
    return list(map(int, section_5.split(';')))


# ---------------------------------
# ATLAS
# ---------------------------------
@pytest.fixture
def atlas_session(option_args):
    facade = Facade('s_admn', *option_args['chs'])
    yield facade
    facade.logout()


@pytest.fixture
def freq(atlas_session, request):
    sleep(20)
    atlas_session.set_param(*request.param[1::])
    sleep(20)
    response = float(atlas_session.get_param(request.param[0]))
    yield [request.param[-1], response, abs(response - float(request.param[-1]))]


@pytest.fixture
def backup_before_test(atlas_session, request):
    bs = request.config.getoption('--backup_slot')
    dc = request.config.getoption('--dev_cls')
    atlas_session.backup(bs, dc)
    logger.info('Backup до теста создан')
    before_test = atlas_session.get_param_backup_data(bs, dc)
    logger.info(f'Backup до теста сохранён {before_test}')
    yield before_test


@pytest.fixture
def choice_mask_or_select_for_mux1(atlas_session, option_args, request):
    if option_args['mask'] == '1':
        logger.info('Добавление ТР через MaskSet')
        atlas_session.set_param(f'{option_args.get("dev_cls")}_{option_args.get("slot")}_ATPMux1OPUTsMaskSet',
                                maskDict.get(str(request.param[0])))
        assert atlas_session.check_response(
            f'{option_args.get("dev_cls")}_{option_args.get("slot")}_ATPMux1OPUTsMaskSet',
            f'{maskDict.get(str(request.param[0]))}') is None
        logger.info(f'Выбран трибутарный порт OPU [ OPUkTp{request.param[1]} ]')
    else:
        logger.info('Добавление ТР через Select')
        atlas_session.set_param(f'{option_args.get("dev_cls")}_{option_args.get("slot")}_ATPMux1OPUTpSelect',
                                f'{request.param[0]}')
        assert atlas_session.check_response(
            f'{option_args.get("dev_cls")}_{option_args.get("slot")}_ATPMux1OPUTpSelect',
            f'{request.param[0]}') is None
        logger.info(f'Выбран трибутарный порт OPU [ OPUkTp{request.param[1]} ]')


@pytest.fixture
def choice_mask_or_select_for_mux2(atlas_session, option_args, request):
    if option_args['mask'] == '1':
        logger.info('Добавление ТР через MaskSet')
        atlas_session.set_param(f'{option_args.get("dev_cls")}_{option_args.get("slot")}_ATPMux2OPUTsMaskSet',
                                maskDict.get(str(request.param[0])))
        assert atlas_session.check_response(
            f'{option_args.get("dev_cls")}_{option_args.get("slot")}_ATPMux2OPUTsMaskSet',
            f'{maskDict.get(str(request.param[0]))}') is None
        logger.info(f'Выбран трибутарный порт OPU [ OPUkTp{request.param[1]} ]')
    else:
        logger.info('Добавление ТР через Select')
        atlas_session.set_param(f'{option_args.get("dev_cls")}_{option_args.get("slot")}_ATPMux2OPUTpSelect',
                                f'{request.param[0]}')
        assert atlas_session.check_response(
            f'{option_args.get("dev_cls")}_{option_args.get("slot")}_ATPMux2OPUTpSelect',
            f'{request.param[0]}') is None
        logger.info(f'Выбран трибутарный порт OPU [ OPUkTp{request.param[1]} ]')


@pytest.fixture
def backup_diff(atlas_session, option_args):
    atlas_session.backup(option_args.get('backup_slot'), option_args.get('dev_cls'))
    logger.info('Backup до перезагрузки слота сделан')
    sleep(5)
    backup_before_reboot = atlas_session.get_param_backup_data(option_args.get('backup_slot'),
                                                               option_args.get('dev_cls'))
    logger.info('Backup до перезагрузки слота сохранён')
    sleep(3)
    atlas_session.set_param(*option_args.get('reboot_slot'), REBOOT_VAL)
    sleep(WAIT_REBOOT)
    atlas_session.backup(option_args.get('backup_slot'), option_args.get('dev_cls'))
    logger.info('Backup после перезагрузки слота создан')
    backup_after_reboot = atlas_session.get_param_backup_data(option_args.get('backup_slot'),
                                                              option_args.get('dev_cls'))
    logger.info(f'Backup после теста сохранён {backup_after_reboot}')
    diff = DeepDiff(backup_before_reboot, backup_after_reboot, verbose_level=2)

    yield diff

    # assert not diff, f'После перезагрузки слотового устройства параметры не совпадают: [ {diff} ]'


@pytest.fixture
def oos_is_adm_st(atlas_session, option_args):
    atlas_session.set_param(f'{option_args.get("dev_cls")}_{option_args.get("slot")}_ATP1Ln1PortState', '1')
    atlas_session.check_response(f'{option_args.get("dev_cls")}_{option_args.get("slot")}_ATP1Ln1PortState', '1')
    logger.info(
        f'ATP1Ln1PortState на устройстве [ {option_args.get("dev_cls")} ] в слоту '
        f'[ {option_args.get("slot")} ] переведён в [ OOS-MT ]')
    yield
    atlas_session.set_param(f'{option_args.get("dev_cls")}_{option_args.get("slot")}_ATP1Ln1PortState', '2')
    atlas_session.check_response(f'{option_args.get("dev_cls")}_{option_args.get("slot")}_ATP1Ln1PortState', '2')
    logger.info(
        f'ATP1Ln1PortState на устройстве [ {option_args.get("dev_cls")} ] в слоту '
        f'[ {option_args.get("slot")} ] переведён в [ IS ]')


@pytest.fixture
def get_cl_sfp_thr(atlas_session, option_args, request):
    module_vendor = atlas_session.get_param(
        f'{option_args.get("dev_cls")}_{option_args.get("slot")}_QSFP{request.param}Vendor')
    pt_number = atlas_session.get_param(
        f'{option_args.get("dev_cls")}_{option_args.get("slot")}_QSFP{request.param}PtNumber')
    logger.info(f'Производитель модуля - {module_vendor}')
    logger.info(f'Код модуля {pt_number}')
    atlas_session.set_param(f'{option_args.get("dev_cls")}_{option_args.get("slot")}_QSFP{request.param}ThrReset', '0')
    sleep(7)

    thr_names = [
        'PinCMin', 'PinWMin', 'PinWMax', 'PinCMax',
        'PoutCMin', 'PoutWMin', 'PoutWMax', 'PoutCMax'
    ]
    values_before = [
        'pin_cmin_before', 'pin_wmin_before', 'pin_wmax_before', 'pin_cmax_before',
        'pout_cmin_before', 'pout_wmin_before', 'pout_wmax_before', 'pout_cmax_before'
    ]

    thr_set_value = [
        ('PinWMin', '-8'), ('PinWMax', '3'), ('PinCMin', '-10'), ('PinCMax', '4'),
        ('PoutWMin', '-3'), ('PoutWMax', '2'), ('PoutCMin', '-5'), ('PoutCMax', '5')
    ]
    values_after = [
        'in_wmin_after', 'in_wmax_after', 'in_cmin_after', 'in_cmax_after',
        'out_wmin_after', 'out_wmax_after', 'out_cmin_after', 'out_cmax_after'
    ]

    thr_values_before = dict(zip(values_before, map(lambda n: atlas_session.get_param(
        f'{option_args.get("dev_cls")}_{option_args.get("slot")}_ATP1Cl{request.param}{n}'), thr_names)))

    sleep(3)
    logger.warning('Значения порогов на клиентских портах, считанных с модуля')
    logger.warning(
        f'Cl{request.param}PinCMin = {thr_values_before["pin_cmin_before"]}\n\t\t\t\t\t\t\tCl{request.param}'
        f'PinWMin = {thr_values_before["pin_wmin_before"]}\n\t\t\t\t\t\t\t'
        f'Cl{request.param}PinWMax = {thr_values_before["pin_wmax_before"]}\n\t\t\t\t\t\t\tCl{request.param}'
        f'PinCMax = {thr_values_before["pin_cmax_before"]}\n\t\t\t\t\t\t\t'
        f'Cl{request.param}PoutCMin = {thr_values_before["pout_cmin_before"]}\n\t\t\t\t\t\t\tCl{request.param}'
        f'PoutWMin = {thr_values_before["pout_wmin_before"]}\n\t\t\t\t\t\t\t'
        f'Cl{request.param}PoutWMax = {thr_values_before["pout_wmax_before"]}\n\t\t\t\t\t\t\tCl{request.param}'
        f'PoutCMax = {thr_values_before["pout_cmax_before"]}\n\t\t\t\t\t\t\t')

    thr_values_after = dict(zip(values_after, map(lambda n: atlas_session.set_param(
        f'{option_args.get("dev_cls")}_{option_args.get("slot")}_ATP1Cl{request.param}{n[0]}', n[1]), thr_set_value)))

    sleep(15)
    logger.warning('Значения порогов установленных на клиентских портах')
    logger.warning(
        f'Cl{request.param}PinCMin = {thr_values_after["in_cmin_after"]["RACK"]["PARAM"]["VALUE"]}\n\t\t\t\t\t\t\t'
        f'Cl{request.param}PinWMin = {thr_values_after["in_wmin_after"]["RACK"]["PARAM"]["VALUE"]}\n\t\t\t\t\t\t\t'
        f'Cl{request.param}PinWMax = {thr_values_after["in_wmax_after"]["RACK"]["PARAM"]["VALUE"]}\n\t\t\t\t\t\t\t'
        f'Cl{request.param}PinCMax = {thr_values_after["in_cmax_after"]["RACK"]["PARAM"]["VALUE"]}\n\t\t\t\t\t\t\t'
        f'Cl{request.param}PoutCMin = {thr_values_after["out_cmin_after"]["RACK"]["PARAM"]["VALUE"]}\n\t\t\t\t\t\t\t'
        f'Cl{request.param}PoutWMin = {thr_values_after["out_wmin_after"]["RACK"]["PARAM"]["VALUE"]}\n\t\t\t\t\t\t\t'
        f'Cl{request.param}PoutWMax = {thr_values_after["out_wmax_after"]["RACK"]["PARAM"]["VALUE"]}\n\t\t\t\t\t\t\t'
        f'Cl{request.param}PoutCMax = {thr_values_after["out_cmax_after"]["RACK"]["PARAM"]["VALUE"]}\n\t\t\t\t\t\t\t')

    return thr_names, values_before, thr_values_before


@pytest.fixture
def drset(atlas_session, option_args, request):
    atlas_session.set_param(f'{option_args.get("dev_cls")}_{option_args.get("slot")}_ATP1Ln1DRSet', request.param)

    if atlas_session.check_response(f'{option_args.get("dev_cls")}_{option_args.get("slot")}_ATP1Ln1DRSet',
                                    request.param) is None:
        return True
    else:
        return False


# ---------------------------------
# Support
# ---------------------------------
@pytest.fixture
def csv_writer():
    with open('table.csv', 'a', encoding='utf-8') as csv_v:
        writer = csv.writer(csv_v, delimiter=';')
        yield writer


@pytest.fixture(scope='class')
def create_csv_file():
    logger.info('Создание файла')
    with open('table.csv', 'a', encoding='utf-8') as csv_v:
        writer = csv.writer(csv_v, delimiter=';')
        writer.writerows([TITLE])


@pytest.fixture
def get_fw_file():
    fws = []
    for root, dirs, files in os.walk(os.getcwd()):
        for name in files:
            if fnmatch(name, FW_POSTFIX):
                fws.append(name)
    yield fws
