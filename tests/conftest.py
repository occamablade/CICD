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

# ---------------------------------
# Vars
# ---------------------------------
maskDict = {
    '1': '000000FF 00000000 00000000',
    '2': '0000FF00 00000000 00000000',
    '3': '00FF0000 00000000 00000000',
    '4': 'FF000000 00000000 00000000',
    '5': '00000000 000000FF 00000000',
    '6': '00000000 0000FF00 00000000',
    '7': '00000000 00FF0000 00000000',
    '8': '00000000 FF000000 00000000',
    '9': '00000000 00000000 000000FF',
    '10': '00000000 00000000 0000FF00'
}


@dataclass
class Command:
    section_5: str = 'cat /tmp/atlas/data/{}/t5'


# ---------------------------------
# Report
# ---------------------------------
# def pytest_configure(config):
#     config._metadata = None


def pytest_html_results_table_header(cells):
    cells.insert(1, html.th("Time", class_="sortable time", col="time"))


# ----------------------------------------------------------------------
#                               NMS Playwright
# ----------------------------------------------------------------------
# ---------------------  NMS LOGIN --------------------------------------

@pytest.fixture
def login_via_playwright() -> object:
    """
    The fixture logins to NMS and returns page object for further processing

    """
    with sync_playwright() as syncP:
        browser = syncP.chromium.launch(headless=False, slow_mo=100)
        page = browser.new_page()
        page.goto(URL_LOGIN_NMS)
        page.get_by_placeholder("Enter your username").fill(TEST_LOGIN_NMS)
        page.get_by_placeholder("Enter user password").fill(TEST_PASSWD_NMS)
        page.click("button#submit_button")
        syst = page.get_by_role('link', name='Topology').text_content().strip()
        assert syst == "Topology", f'Ошибка входа на [ {URL_LOGIN_NMS} ]'
        logger.warning(f'Успешно вошли на [ {URL_LOGIN_NMS} ]')
        yield page
        browser.close()
        logger.warning(f'Браузер закрыт')


# ---------------------  NMS TABLE ID --------------------------------------
def table1_id(page):
    """
    The fixture returns text string which allows further processing of NMS main table.
    example of table1_id :
    "pid_sKoC"  "pid_mrQf"  etc
    :param page:
    :type page:
    :return: text string
    :rtype:
    """
    return page.locator('.page-container') \
               .locator('.content-layout') \
               .locator('.lm_goldenlayout') \
               .locator('.lm_item') \
               .locator('.lm_item_container') \
               .locator('.lm_content:visible').get_attribute('id')[:8]


# ---------------------  NMS TABLE ID --------------------------------------
def table11_id(page):
    """
        The function returns text string which allows further processing of NMS main table.
        example of table1_id :
        ""pid_wkMu_cne"  etc
        :param page:
        :type page:
        :return: text string
        :rtype:
        """
    return (page.locator
            ('#page-container > #content-layout > .lm_goldenlayout')
            .locator('.lm_item >> .lm_item_container:visible > .lm_content ')
            .locator('.golden-wrapper > .panel >> div.table-container').get_attribute('id'))


def table2_id(page):  # for Upload Backup Files into NMS Archive, TC-151
    """
     The function returns text string which allows further processing of Filter panel.
        example of table2_id : id="bs-select-336"

        Example of variables which are using in code are id="bs-select-336-0" , id="bs-select-336-3" etc
    :param page:
    :type page:
    :return: string
    :rtype:
    """
    result = page.locator(f'#{table1_id(page)}_modal-form-upload-backup') \
        .locator('button:has-text("Select and Begin Typing")').get_attribute('aria-owns')
    return result


def table3_id(page):
    """
         The function returns text string which allows further processing of Filter panel.
            example of table2_id : id="bs-select-336"

            Example of variables which are using in code are id="bs-select-336-0" , id="bs-select-336-3" etc
        :param page:
        :type page:
        :return: string
        :rtype:
    """
    el = page.get_by_role("combobox", name="Nothing selected").get_attribute('aria-owns')
    # logger.info(f'table3_id: {el}')
    return el


def table4_id(page):
    return page.locator(f"#{table1_id(page)}_modal-dialog-add-ad") \
        .locator(f'button:has-text("Select and Begin Typing")').get_attribute('aria-owns')


def react_id_domain(page):
    react_id = page.locator("div:nth-child(8):visible").locator(".react-select-container").locator(
        "span").first.get_attribute("id")
    logger.info(f'{react_id[:14]=}')
    return react_id[:14]


def table_data_text(page):
    """
    The function returns  data of displayed table as list of lists elements, in text format.
    Elements of inner list are cell_text  or cell_data-value
    example is :
    [
        [None, 'OT', 'shass_157', '0', 'unlocked', 'enabled', 'true', 'bidirectional', 'management', 'ODU-1-1-2-0-C10', 'ODU-1-1-2-0-LINE1-TP1', 'odu2', 'client-line', '', 'false', '', '', '', '', '', 'off', 'off', 'off', '', '', '', '', '', '', 'ODU-1-1-2-0-C10:ODU-1-1-2-0-LINE1-TP1', ''], ...
         }
    """
    sleep(0.5)
    table_datas = []
    for el in table_data_web(page):
        if el.inner_text() == '':
            break
        table_datas.append(el.inner_text().split('\t'))
    return table_datas


def table_data_web(page):
    """
    The function returns PlayWright table object which further can be processed by rows or  by cells.
    it is possible to click on cell, read text of cell, read cell attributes (class, color, style, etc)

    """
    return page.locator(f"#{table11_id(page)}id > tbody > tr").all()


def wait_while_table_updated(page, controlled_col_number, controlled_value):
    """
    The function waits while table will be updated during long operations for certain node_name
    :param page:
    :type page:
    :param controlled_col_number:  - defines number of column where node_name stated
    :type controlled_col_number:   - int
    :param controlled_value:        - defines node_name for which change ordered
    :type controlled_value:         - str
    :return:                        - None
    :rtype:
    """
    table = table_data_text(page)
    filtered_table = []
    for el in table:
        if el[controlled_col_number] == controlled_value:
            filtered_table.append(el)
    logger.info('Waiting while table updates')
    while True:
        table1 = table_data_text(page)
        filtered_table1 = []
        for el1 in table1:
            if el1[controlled_col_number] == controlled_value:
                filtered_table1.append(el1)
        if filtered_table != filtered_table1:
            break
        sleep(5)


# ------------------  NMS NOTIFICATIONS ----------------------------
def notice_message_blue(page):
    """
    The function returns text ( and log the text) of notice message in blue frame
    """
    notice_message_el = page.locator('#gritter-notice-wrapper > .bg-blue').nth(-1)
    nt = notice_message_el.inner_text().replace('\n', '. ')
    logger.info(f'{nt}')
    return nt


def notice_message_green(page):
    """
    The function returns text ( and log the text) of notice message in green frame
    """
    notice_message_el = page.locator('#gritter-notice-wrapper > .bg-green').nth(-1)
    nt = notice_message_el.inner_text().replace('\n', '. ')
    logger.info(f'{nt}')
    return nt


def notice_message(page):
    """
    The function returns text ( and log the text) of notice message in any-color frame
    """
    notice_message_el = page.locator('#gritter-notice-wrapper').nth(-1)
    nt = notice_message_el.inner_text().replace('\n', '. ')
    logger.info(f'{nt}')
    return nt


# ------------------  NMS NAVIGATION ----------------------------
def to_system_ne_control(page):
    """
    The function changes current web page to system_ne_control
    """
    sleep(0.5)
    if not (page.locator('#sidebar').locator('.has-sub').locator(f':text("NE Control")').is_visible()):
        page.get_by_role('link', name='System').click()
    sleep(0.5)
    page.get_by_role("link", name="NE Control").click()
    logger.info('Went to tab "System NE Control"')
    sleep(0.5)


def to_system_ip_tunnels(page):
    """
    The function changes current web page to system_ip_tunnels
    """
    if not (page.locator('.has-sub')
            .locator(f':text("IP Tunnels")').is_visible()):
        page.get_by_role('link', name='System').click()
    sleep(0.5)
    page.get_by_role("link", name="IP Tunnels").click()
    logger.info('Went to tab "System IP Tunnels"')
    sleep(0.1)


def to_system_ip_addresses(page):
    """
        The function changes current web page to system_ip_addresses
        """
    if not (page.locator('.has-sub')
            .locator(f':text("IP Addresses")').is_visible()):
        page.get_by_role('link', name='System').click()
    sleep(0.5)
    page.get_by_role("link", name="IP Addresses").click()
    logger.info('Went to tab "System IP Addresses"')
    sleep(0.1)


def to_backup_restore(page):
    """
        The function changes current web page to backup_restore
    """
    if not (page.locator('#sidebar').locator('.has-sub')
            .locator(f':text("Backup / Restore")').is_visible()):  # if menu Backup / Restore isn't visible
        page.get_by_role('link', name='Configuration Management').click()  # click on Configuration Management
        sleep(0.5)
    page.get_by_role("link", name="Backup / Restore").click()
    logger.info('Went to tab "Backup / Restore"')
    sleep(0.5)


def to_archive_log(page):
    """
        The function changes current web page to archive_log
    """
    if not (page.locator('#sidebar').locator('.has-sub')
            .locator(f':text("Backup / Restore")').is_visible()):  # if menu Backup / Restore isn't visible
        page.get_by_role('link', name='Configuration Management').click()  # click on Configuration Management
        sleep(0.5)
    page.get_by_role("link", name="Backup / Restore").click()
    sleep(0.5)
    table1__id = table1_id(page)
    page.locator(f"#{table1__id}_archivebackup").get_by_text("Archive log").click()
    logger.info('Went to tab "Archive Log"')
    sleep(0.5)


def to_system_ne_mngmnt(page, node_name: str):
    """
        The function changes current web page to system_ne_mngmnt
    """
    sleep(0.5)
    if not (page.locator('#sidebar').locator('.has-sub').locator(f':text("NE Control")').is_visible()):
        page.get_by_role('link', name='System').click()
    sleep(0.5)

    page.get_by_role("link", name="NE Control").click()
    page.locator(f'#{table1_id(page)}_cneid >> tbody').get_by_role('cell', name=node_name, exact=True).click(
        button='right')
    page.get_by_role("link", name="NE Management").click()
    logger.info(f'Went to tab "NE Management" for node "{node_name}"')
    sleep(1)


# ------------------  NODE MANIPULATION  ----------------------------
def ne_config_table(page):
    """
    The function read table of management NE and returns text dict, including
    {line_num :
        {status0 : class_of_sign;  tatus1 : class_of_sign; tatus2 : class_of_sign; el_name: el_name, el_indent: el_indent} ....
    }

    """
    ne_config_result = {}
    ne_config = ne_config_web(page)
    line_no = -1
    for el in ne_config:
        ne_el_config = {}
        line_no += 1
        ne_el_config['line_id'] = line_no
        ne_el_config['info'] = {}
        el1 = el.locator('td').nth(0).locator('i').all()
        ne_el_config['status0'] = el1[0].get_attribute('class')[3:]
        ne_el_config['status1'] = el1[1].get_attribute('class')[3:]
        ne_el_config['status2'] = el1[2].get_attribute('class')[3:]
        ne_el_config['el_indent'] = int(el.locator('td').nth(1).locator('span').first.get_attribute('style')[14])
        ne_el_config['el_name'] = el.locator('td').nth(1).locator('span > span').nth(2).text_content()
        ne_config_result[line_no] = ne_el_config
    return ne_config_result


def ne_config_web(page):
    """
    The function read table of management NE and returns list of playwright objects (rows)
    for further processing of the rows (click, read text, unwrap etc)

    """
    return page.locator(f"#{table1_id(page)}_config_treetable > tbody > tr ").all()


def read_modal_dialog_table(page, device_name: str, table_name: Literal["Configuration", "Sensors"]):
    """
    The function reads and returns low-lewel equipment  parameters from modal window
    """
    if table_name == 'Sensors':
        page.locator(f"#{table1_id(page)}_config_treetable") \
            .get_by_text(f'{device_name}', exact=True).click(button='right')
        page.locator('#object_perf').click()  # 'Performance Management.click'
        page.locator('#Sensors').click()  # 'Sensors.click'
        sleep(7)  # mandatory sleep
    if table_name == 'Configuration':
        page.locator(f"#{table1_id(page)}_config_treetable") \
            .get_by_text(f'{device_name}', exact=True).click(button="right")
        page.locator('#Config').click()  # 'Configuration Node table'
        sleep(3)  # mandatory sleep
    table_data_raw = page.locator(f'div.modal-dialog') \
        .locator('form.modal-react').locator('div.overflowContainer') \
        .locator('div.overflowBody').locator('table.overflowBody > tbody > tr').all()
    sleep(1)
    table_data = []
    for el in table_data_raw:
        if el.inner_text() == '':
            break
        table_data.append(el.inner_text().split('\n\t\n'))
    page.get_by_role("button", name="Close").click()
    return table_data


def modify_device_config(page, device_name: str, param: str, value: str):
    """
    for configuration of transponders, amplifiers etc via low-level parameters menu
    """
    logger.info(f'Device "{device_name}" modifying configuration {param}  to "{value}"')
    page.locator(f"#{table1_id(page)}_config_treetable") \
        .get_by_text(f'{device_name}', exact=True).click(button="right")
    page.locator('#Config').click()  # 'Configuration Node table'
    sleep(2)  # mandatory sleep
    table_data = page.locator(f'div.modal-dialog') \
        .locator('form.modal-react').locator('div.overflowContainer') \
        .locator('div.overflowBody').locator('table.overflowBody > tbody > tr').all()
    for el in table_data:
        if f'{param}' in el.inner_text():
            el.locator(
                'td:nth-child(5) > div > .form-group > .form-animated > .react-select-container > .react-select-control') \
                .locator('input:visible').fill(f'{value}')
            el.locator(
                'td:nth-child(5) > div > .form-group > .form-animated > .react-select-container > .react-select-control') \
                .locator('input:visible').press("Enter")
            sleep(0.5)
            break
    page.get_by_role("button", name="Apply").click()  # Apply button is not active if config has not been changed.
    sleep(0.5)
    page.get_by_role("button", name="Yes, Apply changes").click()
    sleep(0.5)
    page.get_by_role("button", name="Close").click()
    logger.info(f'Device "{device_name}" modified configuration {param}  to "{value}"')


def modify_ne_board_state(page, device_name: str,
                          action: Literal["Maintenance", "Lock", "Unlock"]):
    """
    the function prerequisite :
        to_system_ne_mngmnt(page, node_name)

    high-level node manipulation on board-level like "Maintenance", "Lock", "Unlock"
    """
    ne_config_web1 = ne_config_web(page)
    sleep(0.5)
    ne_modified = False
    for i, el in enumerate(ne_config_web1):  # trying to expand element
        el1 = el.locator('td').nth(0).locator('i').all()
        el2 = el.locator('td').nth(1).locator('span').all()
        el_name_web = ""
        for el21 in el2:
            if el21.get_attribute('class') == "fancytree-title":
                el_name_web = el21.text_content()
        if device_name == el_name_web:
            logger.info(f'Reconfiguration  of {device_name} to {action}')
            el.locator('td').nth(1).click(button="right")
            sleep(0.5)
            page.get_by_role("link", name="Adm State").click()
            sleep(0.5)
            if action == "Maintenance":
                page.get_by_role("link", name="Maintenance").click()
                logger.info(f'Device {device_name} set to "Maintenance"')
            if action == "Lock":
                page.get_by_role("link", name="Lock").click()
                logger.info(f'Device {device_name} set to "Lock"')
            if action == "Unlock":
                page.get_by_role("link", name="Unlock").click()
                logger.info(f'Device {device_name} set to "Unlock"')
            sleep(0.5)
            page.get_by_role("button", name="Confirm").click()
            sleep(1)
            notice_message_blue(page)
            notice_message_green(page)
            ne_modified = True
            break
    if ne_modified:
        logger.info(f"Device '{device_name}' changed mode to {action}")
        return
    else:
        logger.info(f"Device '{device_name}' forr change configuration wasn't found in NE")
        return -1


def ne_unwrap_unlock(page, node_name):
    """
    on NE Management window,
    The function unwraps (expose) hidden child elements of Network Element

    :return: list of lists of NE elements ( see table_data_text() function)
    :rtype:
    """
    logger.info(f'Unwrapping {node_name}')
    el_name_web = ''
    config_table = {}
    logger.info(f'Unwrapping NE elements')
    checked_devices = []
    to_system_ne_control(page)
    sleep(0.1)
    page.get_by_role("cell", name=f"{node_name}", exact=True).click(button="right")
    sleep(0.1)
    page.get_by_role("link", name="NE Management").click()
    sleep(0.1)
    table1__id = table1_id(page)
    sleep(0.5)

    need_another_run = True

    # expand wrapped elements
    while need_another_run:
        need_another_run = False
        sleep(0.5)
        config_table = ne_config_table(page)
        ne_config_web1 = ne_config_web(page)
        sleep(0.5)
        for i, el in enumerate(ne_config_web1):  # trying to expand element
            el1 = el.locator('td').nth(0).locator('i').all()
            el_name_web = el.locator('td').nth(1).locator('span > span').nth(2).text_content()
            if el_name_web in checked_devices:
                continue
            checked_devices.append(el_name_web)

            line_no = int([k for k, v in config_table.items() if v['el_name'] == el_name_web][0])
            el_class_list = el.get_attribute("class").split(' ')
            if any([if_el_belongs_to_slot(config_table, line_no, dev) for dev in TESTING_SLOT_NAME]):
                if 'fancytree-ico-c' in el_class_list:
                    # if any([if_el_belongs_to_slot(config_table, line_no, dev) for dev in EXCLUDED_DEVICES]):
                    #     pass
                    el.locator('td').nth(1).locator('span > span').first.click()
                    logger.info(f'Unwrapping {el_name_web}')
                    need_another_run = True

                    sleep(1)
                    config_table = ne_config_table(page)

                el_lock_status = el1[2].get_attribute('class')[3:]
                if el_lock_status == "fa-exclamation-triangle text-grey":  # mode = locked or maintenance : unlocked element
                    logger.info(f'unlock {el_name_web}')
                    el1[0].click(button='right')
                    page.locator('#object_adm').click()
                    page.locator('#Unlock').click()
                    page.get_by_role("button", name="Confirm").click()
                    need_another_run = True
                    sleep(0.5)
    return config_table


def if_el_belongs_to_slot(eqpmnt_table, current_line_no, slotname):
    while True:
        if 'SLOT ' in eqpmnt_table[current_line_no]['el_name'] \
                and slotname in eqpmnt_table[current_line_no]['el_name']:
            return True
        elif 'SLOT ' in eqpmnt_table[current_line_no]['el_name'] \
                and slotname not in eqpmnt_table[current_line_no]['el_name']:
            return False
        elif 'Node' in eqpmnt_table[current_line_no]['el_name']:
            return False
        elif 'CHASSIS' in eqpmnt_table[current_line_no]['el_name']:
            return False
        else:
            current_indent_no = eqpmnt_table[current_line_no]['el_indent']
            change_indent = True
            while change_indent:
                current_line_no -= 1
                if eqpmnt_table[current_line_no]['el_indent'] == current_indent_no:
                    continue
                else:
                    change_indent = False


# ----------------------- NMS SUPPORT FUNCTIONS ----------------------------
def __create_ne(page, node_info):
    """
    The function creates NE after given parameters

    """
    logger.info(f'Creating new node {node_info["node_id"]}')
    page.get_by_role("dialog").locator("input[name=\"ip\"]").click()
    page.get_by_role("dialog").locator("input[name=\"ip\"]").fill(node_info['node_ip'])
    page.get_by_role("dialog").locator("input[name=\"ip\"]").press("Enter")
    logger.info(f'Filled IP address: {node_info["node_ip"]}')

    page.get_by_role("dialog").locator('input[name="node_id"]').click()
    page.get_by_role("dialog").locator('input[name="node_id"]').fill(node_info['node_id'])
    page.get_by_role("dialog").locator('input[name="node_id"]').press("Enter")
    logger.info(f'Filled Node_ID: {node_info["node_id"]}')

    page.locator(
        "div:nth-child(6) > .react-select-container > .react-select-control > .css-fw4xp5 > .css-fo80f6").click()
    page.locator("#react-select-3-option-4").get_by_text(f"{node_info['node_domain']}").click()
    sleep(2)
    page.get_by_role("button", name="Add node").click()

    sleep(2)
    logger.info(f'Node {node_info["node_name"]} created')
    return


def select_ne(page, node_name):
    """
    The function filters strings of table but keeps only strings that belongs to the node_name
    node name must be of type  string or list of strings
    """

    page.locator(f"#{table11_id(page)}id_field_filter").select_option("node")
    # table3__id = table3_id(page)
    if type(node_name) is list:
        node_names = node_name
    elif type(node_name) is str:
        node_names = [node_name]
    else:
        logger.info(f'Variable "node_name" must be of type str or list')
        return

    sleep(0.5)
    table3__id = table3_id(page)
    page.get_by_role("combobox", name="Nothing selected").click()
    for ne_name in node_names:
        logger.info(f'Selecting node: {ne_name}')
        sleep(0.5)
        page.locator(f'#{table3__id}').locator('xpath=.. >> input:visible').click()
        sleep(0.5)
        page.locator(f'#{table3__id}').locator('xpath=.. >> input:visible').fill(ne_name)
        sleep(0.5)
        page.locator(f'#{table3__id}').locator('xpath=.. >> input:visible').press("Enter")
        sleep(0.5)

        if page.locator(f':text("No Results")').is_visible():
            logger.info(f"Menu 'No Results' Shown, NE '{ne_name}' doesn't exist")
            return None
        else:
            page.locator(f'#{table3__id}').locator(f'xpath=.. >> :text("{ne_name}")').click()
            sleep(1)
    page.locator(f"#{table11_id(page)}id_add_filter").click()
    sleep(1)
    return


def __lock_ne(page, node_name):
    """
    The function changed adm_state of NE to "Lock"

    :param node_name: "shass_157"   (exampe)
    :type node_name:    string
    :return:  playwright page

    """
    to_system_ne_control(page)
    # select_ne(page, node_name=node_name)
    sleep(1)
    table_data = table_data_text(page)

    # status = page.locator('//table//tbody//tr//td[6]//i').get_attribute('data-value')
    status = [el[5] for el in table_data if el[2] == node_name][0]
    sleep(1)
    if status == "locked":
        logger.info(f'Узел [ {node_name} ] already locked')
        return
    else:
        page.get_by_role("cell", name=TEST_NODE["node_name"]).first.click(button="right")
        sleep(0.5)
        page.locator(f':text("NE Adm State")').click()
        sleep(0.5)
        page.locator("#Lock").click()
        sleep(0.5)
        page.get_by_role("button", name="Lock node").click()
        sleep(1)
        logger.info(f'NE [ {node_name} ] locked')
        sleep(0.5)
        return


def __unlock_ne(page, node_name):
    """
    The function changed adm_state of NE to "Unlock"

    :param node_name: "shass_157"   (exampe)
    :type node_name:    string
    :return:  playwright page

    """
    to_system_ne_control(page)
    # select_ne(page, node_name=node_name)
    table_data = table_data_text(page)
    # status = page.locator('//table//tbody//tr//td[6]//i').get_attribute('data-value')
    status = [el[5] for el in table_data if el[2] == node_name][0]
    # status = page.locator('//table//tbody//tr//td[6]//i').get_attribute('data-value')
    if status == "unlocked":
        logger.warning(f'Node [ {node_name} ] already unlocked')
        return
    else:
        page.get_by_role("cell", name=node_name).first.click(button="right")
        sleep(1)
        logger.warning(f'Открыто модальное окно узла [ {node_name} ]')
        page.locator("#node_adm").click()
        sleep(0.2)
        page.locator("#node_adm").click()
        sleep(0.5)
        page.locator("#Unlock").click()
        page.get_by_role("button", name="Unlock node").click()
        sleep(1)
        logger.warning(f'Node [ {node_name} ] Unlocked')
        sleep(1)
        return


def if_ne_exists(page, node_name):
    """
    The function checks if NE exists in web page
    :param page:
    :type page:
    :param node_name: "shass_157"
    :type node_name:    string
    :return:  Bool True | False
    :rtype:
    """
    logger.info(f'if_ne_exists starts')
    to_system_ne_control(page)
    sleep(0.5)
    search_status = page.locator('//table//tbody//tr//td[3]').all_text_contents()  # list of all nodes
    result = f'{node_name}' in search_status
    sleep(1)
    if result:
        logger.info(f'Node [ f"{node_name}" ] exists in list')
    else:
        logger.info(f'Node [ f"{node_name}" ] does not exist in list')
    return result


def __delete_ne(page, node_name):
    """
    The function delete line with NE from table "NE Control"
    :param page:
    :type page:
    :param node_name: "shass_157"
    :type node_name:    string
    :return:  None

    """
    to_system_ne_control(page)
    # select_ne(page, node_name=node_name)
    page.get_by_role("cell", name=node_name).first.click(button="right")
    logger.warning(f'Открыто модальное окно узла [ {node_name} ]')
    status = page.locator('//table//tbody//tr//td[6]//i').get_attribute('data-value')
    if status == "unlocked":
        logger.info(f'Node [ {NODE_NAME} ] is unlocked, locking')
        page.locator("#node_adm").click()
        sleep(0.5)
        page.locator("#Lock").click()
        sleep(0.5)
        page.get_by_role("button", name="Lock node").click()
        sleep(0.5)
        logger.info(f'The node [ {node_name} ] locked')
        sleep(3)
    else:
        logger.info(f'The node [ {node_name} ] locked')
    page.get_by_role("cell", name=node_name).first.click(button="right")
    logger.warning(f'Открыто модальное окно узла [ {NODE_NAME} ] для удаления')
    page.locator('#Remove').click()  # Delete NE button
    sleep(0.5)
    page.get_by_role("button", name="Delete node").click()
    logger.info(f'Node {node_name} deleted')
    sleep(2)


#  --------------  BACKUP / RESTORE FUNCTIONS -------------------
def backup_file_upload_to_NMS_archive(page, node_name, backup_comment, file_backup_name: Union[str, list]):
    """
    The function uploads backup_file_upload_to_NMS_archive


    """
    logger.info(f'Backup file uploading to NMS archive')
    to_backup_restore(page)
    sleep(1)
    table1__id = table1_id(page)

    page.locator(f"#{table1__id}_archivebackup").click()
    sleep(1)
    table1__id = table1_id(page)
    page.locator(f"#{table1__id}_UploadBackup").click()
    sleep(1)

    selected_node = page.locator(f"#{table1__id}_modal-form-upload-backup button").first.get_attribute('title')
    if selected_node == 'Select and Begin Typing':
        page.locator(f"#{table1__id}_modal-form-upload-backup button").filter(
            has_text="Select and Begin Typing").click()
        sleep(1)
        page.get_by_role("combobox", name="Search").fill(f"{node_name}")
        sleep(1)
        page.get_by_role("combobox", name="Search").press("Enter")
        sleep(1)
        table2__id = table2_id(page)
        page.locator(f"#{table2__id}-0").click()
        sleep(1)
    elif selected_node == node_name:
        pass
    else:
        page.locator(f"#{table1__id}_modal-form-upload-backup button"). \
            get_by_role("combobox", name=selected_node).click()
        sleep(1)
        page.get_by_role("combobox", name="Search").fill(f"{node_name}")
        sleep(1)
        page.get_by_role("combobox", name="Search").press("Enter")
        sleep(1)
        table2__id = table2_id(page)
        page.locator(f"#{table2__id}-3").click()
        sleep(1)

    # select file from file-chooser window:   https://playwright.dev/python/docs/api/class-filechooser
    with page.expect_file_chooser() as fc_info:
        page.locator(f'#{table1__id}_modal-form-upload-backup').get_by_label("File not selected").click()
    file_chooser = fc_info.value
    file_chooser.set_files(file_backup_name)

    page.locator(f"#{table1__id}_backup_comment").click()
    sleep(1)
    page.locator(f"#{table1__id}_backup_comment").fill(f"{backup_comment}")
    sleep(1)
    page.locator(f"#{table1__id}_backup_comment").press("Enter")
    sleep(1)
    page.locator(f'#{table1__id}_modal-form-upload-backup').get_by_role("button", name="Upload").click()
    sleep(3)
    logger.info(f'Backup file "{file_backup_name}" uploaded to NMS archive')
    all_backups_table = table_data_text(page)
    return all_backups_table


def backup_download_from_nms_to_file(page, node_name, backup_name):
    """
    The function downloads backup from nms to file

    """
    to_archive_log(page)
    sleep(1)
    table_data = table_data_web(page)
    for el in table_data:
        el_text = el.all_inner_texts()[0].split('\t')
        if el_text == ['']:
            logger.info(f'Backup for node "{node_name}" named "{backup_name}" not found')
            return
        if el_text[1] == node_name and el_text[3] == backup_name:
            el.get_by_role("cell", name=f"{backup_name}").click(button="right")
            sleep(0.5)
            break

    with page.expect_download(timeout=5000) as download_info:
        sleep(2)
        page.get_by_role("link", name="Download archive").click()
    sleep(5)
    download = download_info.value
    path = download.path()
    logger.info(f'Backup for node "{node_name}" named "{backup_name}" downloaded from NMS to file')
    return path


def backup_upload_from_nms_to_ne(page, node_name: str, backup_name: str):
    """
    The function uploads backup from_nms_to_ne

    """
    to_backup_restore(page)
    sleep(1)
    all_table_data = table_data_web(page)
    for el in all_table_data:
        el_str = el.all_inner_texts()[0].split("\t")
        if el_str == ['']:
            logger.info(f'The archive {backup_name} for NE {node_name} not found')
            return -1
        if el_str[2] == node_name and el_str[11] == backup_name:
            el.get_by_role("cell", name=f"{node_name}", exact=True).click(button="right")
            break
    page.get_by_role("link", name="Restore from backup").click()
    page.get_by_label("Configuration search").locator("b").click()
    page.get_by_role("option", name=f"{backup_name}").click()
    sleep(1)
    page.get_by_role("button", name="Restore to node").click()
    page.get_by_role("button", name="I am definitely confident in").click()
    sleep(1)
    logger.info(f'Backup "{backup_name}" restored to NE"{node_name}"')


def backup_manual_download_from_ne_to_nms(page, node_name: str, backup_name: str):
    """
    the function download_nms_archive_backupconfig_from_ne
    """

    to_backup_restore(page)
    sleep(1)
    page.get_by_role("cell", name=f"{node_name}", exact=True).click(button="right")
    page.get_by_role("link", name="Manual backup").click()

    table1__id = table1_id(page)
    page.locator(f'#{table1__id}_layout') \
        .locator(f'#{table1__id}_modal-form-backup') \
        .locator("input[name=\"backupname\"]").fill(f'{backup_name}')
    sleep(1)
    page.locator(f'#{table1__id}_layout') \
        .locator(f'#{table1__id}_modal-form-backup') \
        .locator(f'#{table1__id}_backup_submit_button').click()
    sleep(1)

    notice_message_blue(page)
    notice_message_green(page)
    logger.info(f'Backup downloaded from ne "{node_name}"to NMS with name "{backup_name}" ')
    return


def backup_autosave_from_ne_to_nms(page, node_name: str, enabled: bool, num_days: str, num_backups: str):
    """
    The function configure and runs backup autosave

    num_days :  if format '2' > set num of days
                if format '+2' > set extended num of days
    """
    logger.info('Backup autosave configuration started')
    to_backup_restore(page)
    sleep(0.5)
    page.get_by_role("cell", name=f"{node_name}", exact=True).click(button="right")
    page.get_by_role("link", name="Autosave settings").click()
    table1__id = table1_id(page)
    if enabled:
        page.locator(f"#{table1__id}_periodSelect").select_option("enabled")  #
    else:
        page.locator(f"#{table1__id}_periodSelect").select_option("disabled")
    sleep(0.5)
    if num_days:
        page.locator(f"#{table1__id}_modal-form-backupconfig").get_by_placeholder("Day").click()
        sleep(0.5)
        page.locator(f"#{table1__id}_modal-form-backupconfig").get_by_placeholder("Day").fill(num_days)
        sleep(0.5)
        page.locator(f"#{table1__id}_modal-form-backupconfig").get_by_placeholder("Day").press("Enter")
        sleep(1)
    page.locator("input[name=\"backup_start_datetime\"]").click()
    sleep(0.5)
    dayTime_to_start = datetime.now(pytz.timezone('Europe/Moscow')) + timedelta(minutes=1)
    time_string = dayTime_to_start.strftime("%Y-%m-%d %H:%M")
    logger.info(f'Autobackup will start at : {time_string}')
    page.locator("input[name=\"backup_start_datetime\"]").fill(time_string)
    sleep(0.5)
    if num_backups:
        if '+' in num_backups:
            delta_backups = int(num_backups)
            num_of_backups = page.locator("input[name=\"backup_store_record\"]").input_value()
            page.locator("input[name=\"backup_store_record\"]").fill(f'{int(num_of_backups) + delta_backups}')
        else:
            num_backups = int(num_backups)
            page.locator("input[name=\"backup_store_record\"]").fill(f'{num_backups}')
        sleep(0.5)
    page.get_by_role("button", name="Apply").click()
    notice_message_blue(page)

    wait_while_table_updated(page,
                             controlled_col_number=2,
                             controlled_value=node_name)


def backup_nms_delete(page, node_name: str, nms_archive_name: str):
    """
    The function delete backup record from NMS

    """
    to_archive_log(page)
    all_table_data = table_data_web(page)
    for el in all_table_data:
        el_str = el.all_inner_texts()[0].split(
            "\t")  # el_str=['', 'NE_241', '23.04.2024, 11:42:53.893', 'autobackup-2024-04-23T11:42:36', 'A']
        if el_str == '':
            logger.info(f'The backup {nms_archive_name} for NE {node_name} was not found')
            return -1
        if el_str[1] == node_name and el_str[3] == nms_archive_name:
            el.get_by_role("cell", name=f'{nms_archive_name}').first.click(button="right")
            break
    page.get_by_role("link", name="Delete archive").click()
    page.get_by_role("button", name="Delete").click()
    logger.info(f'Backup_record "{nms_archive_name}" deleted')
    sleep(1)
    notice_message_blue(page)
    logger.info(f'Backup "{nms_archive_name}" deleted from NMS')


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
# NMS Netconf
# ---------------------------------
@pytest.fixture
def netconf(option_args):
    net = NetconfCli(*option_args['chs'], login='cli', password='cli')
    logger.info(f'Соединение с узлом {option_args["chs"]} открыто')
    yield net
    net.disconnect()
    logger.info(f'Соединение с узлом {option_args["chs"]} закрыто')


@pytest.fixture
def xml_data():
    xml = XmlData()
    yield xml


@pytest.fixture
def unlock_after_test(netconf, xml_data, request, option_args):
    yield
    if request.param.format(option_args['slot']) == LINE_PORT.format(option_args['slot']):
        netconf.edit_conf_and_commit(xml_data.change_adm_st('unlocked', request.param.format(option_args['slot'])))
        (logger.warning(
            f'Разблокировка адм. состояния после теста для [ {request.param.format(option_args["slot"])} ]'))
    else:
        netconf.edit_conf_and_commit(
            xml_data.change_adm_st_interface('unlocked', request.param.format(option_args['slot'])))
        logger.warning(
            f'Разблокирование административного состояния после теста для '
            f'[ {request.param.format(option_args["slot"])} ]')


@pytest.fixture
def on_transmitter(netconf, xml_data, request, option_args):
    yield
    netconf.edit_conf_and_commit(xml_data.change_tx_enable('true', request.param.format(option_args['slot'])))
    logger.warning(f'Передатчик после теста на интерфейсе [ {request.param.format(option_args["slot"])} ] включен')


@pytest.fixture
def set_opt_power_before_test(netconf, xml_data, option_args):
    value = netconf.get_state(LINE_OPT.format(option_args['slot']), 'tx_opt_pwr')['tx-optical-power']
    yield
    netconf.edit_conf_and_commit(xml_data.change_tx_power(value, LINE_OPT.format(option_args['slot'])))
    logger.warning(
        f'Значение выходной мощности передатчика на интерфейсе '
        f'[ {LINE_OPT.format(option_args["slot"])} ] после теста [ {value} ]')


@pytest.fixture
def get_oper_st_for_odu_conn_before_test(netconf, option_args):
    all_oper_st: list[dict] | dict = netconf.get_state('ODU-1-1-{}'.format(option_args['slot']), 'odu_conn_op_st')

    if isinstance(all_oper_st, list):
        return list(map(lambda d: d.get('operational-state'), all_oper_st))

    return all_oper_st.get('operational-state')


# ---------------------------------
# NMS Restconf
# ---------------------------------
@pytest.fixture
def reboot_slot(option_args):
    response = None
    swm = SWM(node_ip=''.join(option_args.get('chs')))

    if option_args.get('reboot_mode')[0] == 'cold':
        response = swm.cold_reboot(name=''.join(option_args.get('reboot_slot')))
        logger.warning(f'Команда на cold rebot устройства {option_args.get("reboot_slot")} отправлена')
    elif option_args.get('reboot_mode')[0] == 'warm':
        response = swm.warm_reboot(name=''.join(option_args.get('reboot_slot')))
        logger.warning(f'Команда на warm rebot устройства {option_args.get("reboot_slot")} отправлена')

    if response == ('', '', ''):
        logger.warning(f'Команда {option_args.get("reboot_mode")[0]} reboot прошла успешно')
    else:
        logger.critical(response)


@pytest.fixture
def get_froadm_data_before_reboot(netconf):
    connection_nmc = netconf.get_state('NMC-1-2-10', 'nmc_connection')
    addrops = netconf.get_state('ROADMG-1-2-10', 'add_drop')
    degr = netconf.get_state('DEGR-1-2-10', 'degrees')
    logger.info(f'NMC, ADD-DROP, DEGREES до перезагрузки собраны')
    logger.warning(f'{connection_nmc}----{addrops}----{degr}')

    return connection_nmc, addrops, degr


@pytest.fixture
def froadm_reboot_fixture(get_froadm_data_before_reboot, reboot_slot):
    yield get_froadm_data_before_reboot


# ---------------------------------
# NMS API
# ---------------------------------
@pytest.fixture
def backup_nms(option_args):
    bp = Backup()
    ref_bp = bp.get_backup(node_id=''.join(option_args.get('node_id')), backup_name='refBackup')
    # logger.warning(f'Backup до перезагрузки [ {ref_bp} ]')
    yield ref_bp, bp
    bp.disconnect()


# ---------------------------------
# CNE LLF
# ---------------------------------
@pytest.fixture
def llf_cne(exfoftb):
    result_dict = dict()
    for dl, dr, pr in zip(DELAY, DURATION, PERIOD):
        Cfg23Chs().config_cl1_slot1(llf_delay=dl, duration=dr, period=pr)
        logger.info(f'Установка параметров [ DELAY: {dl} ms ] [ DURATION: {dr} ms ] [ PERIOD: {pr} ms ]')
        sleep(5)
        exfoftb.on_off_laser_alllanes('OFF')
        sleep(5)
        exfoftb.on_off_laser_alllanes('ON')
        start = perf_counter()
        while True:
            exfoftb.reset_test_for_module()
            if exfoftb.status():
                result_dict[(dl, dr, pr)] = perf_counter() - start
                break
    yield result_dict


@pytest.fixture
def write_result():
    def wrapper(file):
        logger.info('Запись результата в файл')
        with open('result', 'a') as f:
            print(file, file=f)
            max_item = max(file.items(), key=ig(1))
            min_item = min(file.items(), key=ig(1))
            aver_item = sum(file.values()) / len(file.values())
            logger.info(
                f'Максимальное время восстановление трафика [ {max_item[1]} s ] для значений [ DELAY: {max_item[0][0]}'
                f' ms; DURATION: {max_item[0][1]} ms; PERIOD: {max_item[0][2]} ms ]')
            logger.info(
                f'Минимальное время восстановление трафика [ {min_item[1]} s ] для значений [ DELAY: {min_item[0][0]}'
                f' ms; DURATION: {min_item[0][1]} ms; PERIOD: {min_item[0][2]} ms ]')
            logger.info(
                f'Среднее время восстановление трафика [ {aver_item} s ]')
            print(max_item, file=f)

    return wrapper


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
