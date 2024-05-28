import logging
from typing import Literal


import pytest
from time import sleep
from datetime import datetime

from Utilities.all import (
    NODE_NAME1,
    TESTING_SLOT_NAME,           # sensor wil be tested on this slot
    EXCLUDED_DEVICES,            # These slots will not be expanded
)
from tests.conftest import table1_id, if_el_belongs_to_slot, read_modal_dialog_table, ne_unwrap_unlock, \
    to_archive_log, modify_device_config, notice_message_blue, to_backup_restore, notice_message_green, \
    backup_upload_from_nms_to_ne, backup_nms_delete, table_data_text, backup_manual_download_from_ne_to_nms


logger = logging.getLogger(__name__)


@pytest.fixture()
def setup_perf_mngmnt(login_via_playwright):
    logger.info('Setup started')
    page = login_via_playwright
    backup_manual_download_from_ne_to_nms(page, node_name=NODE_NAME1,
                                               backup_name=f'{NODE_NAME1}_backup_TC1021')
    sleep(1)
    logger.info(f'NOW TEST RUNS ')


@pytest.fixture()
def teardown_perf_mngmnt(login_via_playwright):
    logger.info('Teardown started')
    page = login_via_playwright
    to_archive_log(page)

    backup_info = table_data_text(page)
    backup_names = []
    for el in backup_info:
        if el[1] == NODE_NAME1 and el[3] == f'{NODE_NAME1}_backup_TC1021':
            backup_nms_delete(page=page, node_name=f'{NODE_NAME1}',
                              nms_archive_name=f'{NODE_NAME1}_backup_TC1021')


# ---------------------------- TEST FIXTURES STARTS HERE -----------------
@pytest.fixture
def all_sensors_on_board_t1021(login_via_playwright):
    logger.info('T1021 started')
    page = login_via_playwright

    node_info = ne_unwrap_unlock(page=page, node_name=NODE_NAME1)

    logger.info('Writing port list')
    all_ports: list = []
    for k, el in node_info.items():
        port_info: dict = {}
        if 'Line port LINE' in el["el_name"]:
            port_info['port_type'] = 'L'
            port_info['port_name'] = el['el_name']
            port_info['table_row_num'] = int(k)
            all_ports.append(port_info)
        elif 'Client port C' in el['el_name']:
            port_info['port_type'] = 'C'
            port_info['port_name'] = el['el_name']
            port_info['table_row_num'] = int(k)
            all_ports.append(port_info)
        else:
            continue

    logger.info('Now testing all ports')
    test_data = []
    for the_port in all_ports:
        if any([if_el_belongs_to_slot(node_info, the_port['table_row_num'], dev) for dev in TESTING_SLOT_NAME]):
            test_port_data = {'port_name': the_port['port_name']}
            # logger.info(f'Testing_port: {the_port["port_name"]}')

            test_port_data['pump_current1'] = 'N/A'

            table_data_1 = read_modal_dialog_table(page, device_name=the_port['port_name'], table_name="Sensors")
            for el in table_data_1:
                if el[0] == 'input-power':
                    test_port_data['input_power1'] = float(el[1])
                if el[0] == 'output-power':
                    test_port_data['output_power1'] = float(el[1])
                if el[0] == 'pump-current':
                    test_port_data['pump_current1'] = int(el[1])
            sleep(0.5)

            table_data_2 = read_modal_dialog_table(page, device_name=the_port['port_name'], table_name="Configuration")
            for el in table_data_2:
                if el[0] == 'administrative-state':
                    test_port_data['port_administrative_state1'] = el[2]
                if el[0] == 'tx-enable':
                    test_port_data['port_tx_enable1'] = el[2]

            port_txt = f'{the_port["port_name"]}'
            state_txt = f'{test_port_data["port_administrative_state1"]}'
            tx_txt = f'{test_port_data["port_tx_enable1"]}'
            pow_txt = f'{test_port_data["output_power1"]}'
            curr_txt = f'{test_port_data["pump_current1"]}'
            logger.info\
                (f'Port: {port_txt}; state1: {state_txt}; tx1: {tx_txt};  output_power1: {pow_txt};  pump_current1: {curr_txt}')

            sleep(0.5)
            if test_port_data['port_tx_enable1'] == 'false':
                modify_device_config(page, device_name=f'{the_port["port_name"]}', param='tx-enable', value='true')
            else:
                modify_device_config(page, device_name=f'{the_port["port_name"]}', param='tx-enable', value='false')


            test_port_data['pump_current2'] = 'N/A'

            table_data_2 = read_modal_dialog_table(page, device_name=the_port['port_name'], table_name="Configuration")
            for el in table_data_2:
                if el[0] == 'administrative-state':
                    test_port_data['port_administrative_state2'] = el[2]
                if el[0] == 'tx-enable':
                    test_port_data['port_tx_enable2'] = el[2]

            table_data_3 = read_modal_dialog_table(page, device_name=f'{the_port["port_name"]}', table_name="Sensors")
            for el in table_data_3:
                if el[0] == 'input-power':
                    test_port_data['input_power2'] = float(el[1])
                if el[0] == 'output-power':
                    test_port_data['output_power2'] = float(el[1])
                if el[0] == 'pump-current':
                    test_port_data['pump_current2'] = int(el[1])

            port_txt = f'{the_port["port_name"]}'
            state_txt = f'{test_port_data["port_administrative_state2"]}'
            tx_txt = f'{test_port_data["port_tx_enable2"]}'
            pow_txt = f'{test_port_data["output_power2"]}'
            curr_txt = f'{test_port_data["pump_current2"]}'
            logger.info\
                (f'Port: {port_txt}; state2: {state_txt}; tx2: {tx_txt};  output_power2: {pow_txt};  pump_current2: {curr_txt}')

            test_data.append(test_port_data)
    yield test_data

    backup_upload_from_nms_to_ne(
        page,
        node_name=f'{NODE_NAME1}',
        backup_name=f'{NODE_NAME1}_backup_TC1021')


# @pytest.fixture
# def tmp1(login_via_playwright):
    # logger.info('tmp1 started')
    # start_time = datetime.now()
    # logger.info('hi')
    # total_time = datetime.now() - start_time
    # print(f'Function took {str(total_time).split(".")[0]} seconds')



