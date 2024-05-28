import logging
from time import sleep
from typing import Optional, Literal
from _pytest.fixtures import SubRequest

import pytest
from pytest import param
from py.xml import html
from playwright.sync_api import sync_playwright

from Utilities.all import (
    URL_LOGIN_NMS,
    IP, TEST_NODE, NODE_NAME, TEST_NODE,
    NODE_NAME1,  # Used test_transition_to_ne_management_t634
    USER_FOR_NE,
    PASSWD_FOR_NE, PORT, TEST_PASSWD_NMS, TEST_LOGIN_NMS,
    CHANGE_IP, CHANGE_PORT,
    IP_TUNNEL_DATA1, IP_TUNNEL_DATA2,
    PING_DATA, TRACEROUTE_DATA, NODE_LIST_FOR_MASS_OPS,
)
from tests.conftest import to_system_ip_tunnels, table4_id, table1_id, to_system_ne_control, \
    __unlock_ne, __delete_ne, __lock_ne, __create_ne, if_ne_exists, select_ne, to_system_ip_addresses, table11_id, \
    table_data_web, table_data_text, to_system_ne_mngmnt, ne_config_table

logger = logging.getLogger(__name__)


def pytest_html_results_table_header(cells):
    cells.insert(1, html.th("Time", class_="sortable time", col="time"))


def if_ip_tunnel_exist(page, tunnel_data:dict):
    logger.info(f'Checking if_ip_tunnel_exist {tunnel_data}')
    to_system_ip_tunnels(page)
    sleep(0.5)
    all_tunnel_info = table_data_text(page)
    for i, tunnel_info in enumerate(all_tunnel_info):
        if tunnel_info[1] == tunnel_data['node1_name'] and \
                tunnel_info[2] == tunnel_data['tunnel_name'] and \
                tunnel_info[3] == tunnel_data['local_ip'] and \
                tunnel_info[4] == tunnel_data['remote_ip'] and \
                tunnel_info[5] == tunnel_data['role']:
            return True
    return False


def ip_tunnel_delete(page, tunnel_data: dict):
    to_system_ip_tunnels(page)
    sleep(1)

    all_ip_tunnels = table_data_web(page)
    tunnel_found = False
    for el in all_ip_tunnels:
        if el.inner_text() == '':
            logger.info('The IP Tunnel not found in list')
            return -1

        ip_table_record = el.inner_text().split('\t')
        if ip_table_record[1] == tunnel_data['node1_name'] and \
                ip_table_record[2] == tunnel_data['tunnel_name'] and \
                ip_table_record[3] == tunnel_data['local_ip'] and \
                ip_table_record[4] == tunnel_data['remote_ip']:
            el.get_by_role("cell", name=f'{TRACEROUTE_DATA["node_name"]}', exact=True).click(button='right')
            tunnel_found = True
            break
    if not tunnel_found:
        logger.info('The target TRACEROUTE_DATA node not found in list')
        return -1

    page.locator("#delAD").click()
    sleep(0.5)
    page.locator('.modal-dialog:visible').get_by_role("button", name="Delete").click()
    sleep(1)
    logger.info(f'IP Tunnel deleted for node: {tunnel_data["node1_name"]} named: {tunnel_data["tunnel_name"]}')
    return


def ip_tunnel_create(page, tunnel_data: dict):
    to_system_ip_tunnels(page)

    if if_ip_tunnel_exist(page, tunnel_data=tunnel_data):
        return -1
    logger.info(f'IP Tunnel creating')
    page.get_by_text("Add IP Tunnel").click()
    sleep(0.5)
    table4__id = table4_id(page)
    page.locator(f"#{table1_id(page)}_modal-dialog-add-ad") \
        .locator(f'button:has-text("Select and Begin Typing")').click()
    sleep(0.5)

    page.get_by_role("combobox", name="Search").fill(f'{tunnel_data["node1_name"]}')
    sleep(0.5)
    page.get_by_role("combobox", name="Search").press("Enter")
    sleep(0.3)
    page.locator(f"#{table4__id}-0").click()
    sleep(0.3)

    page.get_by_label("Add IP Tunnel").locator("input[name=\"name\"]").click()
    sleep(0.5)
    page.get_by_label("Add IP Tunnel").locator("input[name=\"name\"]").fill(f'{tunnel_data["tunnel_name"]}')
    sleep(0.3)
    page.locator("input[name=\"local_ip\"]").click()
    sleep(0.5)
    page.locator("input[name=\"local_ip\"]").fill(f'{tunnel_data["local_ip"]}')
    sleep(0.3)
    page.locator("input[name=\"remote_ip\"]").click()
    sleep(0.5)
    page.locator("input[name=\"remote_ip\"]").fill(f'{tunnel_data["remote_ip"]}')
    sleep(0.3)
    page.get_by_label("Add IP Tunnel").locator("select[name=\"adm_state\"]").select_option("OSC")
    sleep(0.3)
    page.get_by_label("Add IP Tunnel").locator("input[name=\"desc\"]").click()
    sleep(0.5)
    page.get_by_label("Add IP Tunnel").locator("input[name=\"desc\"]").fill(f'{tunnel_data["description"]}')
    sleep(0.3)
    page.get_by_role("button", name="Add").click()
    sleep(4)
    logger.info(f'IP Tunnel for node: {tunnel_data["node1_name"]}   named: {tunnel_data["tunnel_name"]} created')
    return


def ip_tunnel_edit(page, tunnel_data1: dict, tunnel_data2: dict):
    logger.info(f'Editing IP Tunnell for node: {tunnel_data1["node1_name"]}')
    to_system_ip_tunnels(page)
    sleep(2)  # Mandatory timeout to refresh page

    all_ip_tunnels = table_data_web(page)
    tunnel_found = False
    for el in all_ip_tunnels:
        if el.inner_text() == '':
            logger.info('The IP Tunnel not found in list')
            return -1

        ip_table_record = el.inner_text().split('\t')
        if ip_table_record[1] == tunnel_data1['node1_name'] and \
                ip_table_record[2] == tunnel_data1['tunnel_name'] and \
                ip_table_record[3] == tunnel_data1['local_ip'] and \
                ip_table_record[4] == tunnel_data1['remote_ip']:
            el.get_by_role("cell", name=f'{TRACEROUTE_DATA["node_name"]}', exact=True).click(button='right')
            tunnel_found = True
            logger.info(f'IP Tunnel edited to {tunnel_data2}')
            break
    if not tunnel_found:
        logger.info('The target TRACEROUTE_DATA node not found in list')
        return -1

    page.locator("#EditAD").click()
    sleep(0.3)
    page.locator("input[name=\"local_ip\"]").click()
    page.locator("input[name=\"local_ip\"]").fill(f'{tunnel_data2["local_ip"]}')
    sleep(0.3)
    page.locator("input[name=\"remote_ip\"]").click()
    page.locator("input[name=\"remote_ip\"]").fill(f'{tunnel_data2["remote_ip"]}')
    sleep(0.3)
    page.locator('.modal-tunnel:visible').locator("input[name=\"desc\"]").click()
    page.locator('.modal-tunnel:visible').locator("input[name=\"desc\"]").fill(f'{tunnel_data2["description"]}')
    sleep(0.3)
    page.get_by_role("button", name="Apply").click()
    logger.info(f'IP Tunnel changed to : {IP_TUNNEL_DATA2}')
    sleep(4)  # Mandatory timeout to refresh page


@pytest.fixture
def ne_control_fixture_T618(login_via_playwright):
    logger.info('Тест-кейс ne_control_fixture_T618')
    page = login_via_playwright

    to_system_ne_control(page)
    logger.info(f'Get lost of tabs')
    check = str(page.get_by_role('button', name='Add Node')).split('"')[1]
    logger.info(f'{check=}')
    yield check
    page.get_by_title('NE Control').click(button='middle')


@pytest.fixture
def ne_discovered_accept_fixture(ne_discovered_fixture):
    logger.info('Тест-кейс Т1169')
    if ne_discovered_fixture.locator('//table//tbody').all_text_contents():
        ne_discovered_fixture.locator('//table//tbody//tr[1]//td[3]').click(button='right')
        yield True if ne_discovered_fixture.locator('#Accept').text_content().strip() == 'Accept NE' else False
    else:
        logger.critical(f"{ne_discovered_fixture.locator('#Accept').text_content()}")
        yield False


@pytest.fixture
def ne_discovered_remove_fixture(ne_discovered_fixture):
    logger.info('Тест-кейс Т1170')
    if ne_discovered_fixture.locator('//table//tbody').all_text_contents():
        ne_discovered_fixture.locator('//table//tbody//tr[1]//td[3]').click(button='right')
        yield True if ne_discovered_fixture.locator('#Remove').text_content().strip() == 'Remove NE' else False
    else:
        logger.critical(f"{ne_discovered_fixture.locator('#Remove').text_content()}")
        yield False


@pytest.fixture()
def create_new_ne_t622(login_via_playwright):
    logger.info('Тест-кейс create_new_ne_t622')
    page = login_via_playwright

    to_system_ne_control(page)
    sleep(0.5)

    if not if_ne_exists(page, node_name=f'{TEST_NODE["node_name"]}'):
        page.get_by_text("Add Node").click()
        __create_ne(page=page, node_info=TEST_NODE)
        result = page.locator('//table//tbody//tr//td[3]').all_text_contents()
        logger.info(f'{result=}')
        yield result
    else:
        logger.info(f'The node already exists')
        yield f"NE_Not_Added"


@pytest.fixture
def create_new_ne_via_context_menu_t623(login_via_playwright):
    logger.info('Тест-кейс create_new_ne_via_context_menu T623')
    page = login_via_playwright
    to_system_ne_control(page)
    if if_ne_exists(page, node_name=f'{TEST_NODE["node_name"]}'):
        logger.info(f'Node {TEST_NODE["node_name"]} already exist, Node has not been created')
        yield None

    page.locator('//table//tbody//tr//td[3]').all()[0].click(button='right')
    page.locator('#node_add').click()
    __create_ne(page=page, node_info=TEST_NODE)
    result = page.locator('//table//tbody//tr//td[3]').all_text_contents()
    logger.info(f'{result=}')
    yield result


@pytest.fixture
def lock_ne_via_ne_control_fixture_t624(login_via_playwright):
    logger.info('Тест-кейс lock_ne_via_ne_control_fixture_t624')
    page = login_via_playwright
    to_system_ne_control(page)
    select_ne(page, node_name=f'{TEST_NODE["node_name"]}')

    status = page.locator('//table//tbody//tr//td[6]//i').get_attribute('data-value')
    while status == "locked":
        logger.warning(f'Узел [ {TEST_NODE["node_name"]} ] already locked, unlocking')
        __unlock_ne(page, TEST_NODE["node_name"])
        sleep(1)
        status = page.locator('//table//tbody//tr//td[6]//i').get_attribute('data-value')

    logger.info(f'Node {TEST_NODE["node_name"]}  status: {status}')

    __lock_ne(page, TEST_NODE["node_name"])

    status = page.locator('//table//tbody//tr//td[6]//i').get_attribute('data-value')
    logger.info(f'{status=}')
    yield status


@pytest.fixture
def unlock_ne_via_ne_control_fixture_t626(login_via_playwright):
    logger.info('Тест-кейс test_unlock_ne T626')

    page = login_via_playwright
    to_system_ne_control(page)
    select_ne(page, node_name=f'{TEST_NODE["node_name"]}')

    status = page.locator('//table//tbody//tr//td[6]//i').get_attribute('data-value')
    if status == "unlocked":
        logger.warning(f'Узел [ {TEST_NODE["node_name"]} ] already unlocked')
        __lock_ne(page, TEST_NODE["node_name"])
        status = page.locator('//table//tbody//tr//td[6]//i').get_attribute('data-value')

    logger.info(f'Node {TEST_NODE["node_name"]}  status: {status}')
    __unlock_ne(page, TEST_NODE["node_name"])
    sleep(3)
    status = page.locator('//table//tbody//tr//td[6]//i').get_attribute('data-value')
    logger.info(f'{status=}')
    yield status


@pytest.fixture
def delete_ne_t638(login_via_playwright):
    logger.info('Тест-кейс delete_ne T638')

    page = login_via_playwright
    to_system_ne_control(page)
    select_ne(page, node_name=f'{TEST_NODE["node_name"]}')
    __delete_ne(page, TEST_NODE["node_name"])
    sleep(2)
    to_system_ne_control(page)
    sleep(0.5)
    all_nodes = table_data_text(page)
    result = [el[2] for el in all_nodes]  # node_names
    logger.info(f'{result=}')
    yield result


@pytest.fixture
def edit_name_ne_fixture_t627(login_via_playwright):
    logger.info('Тест-кейс edit_name_ne_fixture T627')

    page = login_via_playwright
    to_system_ne_control(page)
    select_ne(page, node_name=TEST_NODE["node_name"] )
    sleep(1)
    __lock_ne(page, node_name=TEST_NODE["node_name"])
    sleep(1)
    page.get_by_role("cell", name=TEST_NODE["node_name"]).first.click(button="right")

    sleep(0.5)
    page.locator('#node_edit').click()
    logger.info(f'Click "NodeEdit"')
    sleep(0.5)
    logger.warning(f'Открыто модальное окно узла [ {TEST_NODE["node_name"]} ] для изменения имени на [ {TEST_NODE["node_name"]}_1 ]')
    page.get_by_role("dialog").locator('input[name="node_name"]').click()
    sleep(0.5)
    page.get_by_role("dialog").locator('input[name="node_name"]').fill(f'{TEST_NODE["node_name"]}_1')
    page.get_by_role("dialog").locator('input[name="node_name"]').press("Enter")
    page.get_by_role("button", name="Update node").click()
    sleep(0.5)
    logger.warning(f'Имя узла изменено с [ {TEST_NODE["node_name"]} ] на [ {TEST_NODE["node_name"]+ "_1"} ]')
    sleep(5)
    result = page.locator('//table//tbody//tr//td[3]').all_text_contents()
    logger.info(f'{result}')
    yield result

    page.get_by_role("cell", name=f'{NODE_NAME}_1').first.click(button="right")
    page.locator('#node_edit').click()
    sleep(0.5)
    logger.warning(f'Открыто модальное окно узла [ {TEST_NODE["node_name"]}_1 ] для изменения имени узла на [ {TEST_NODE["node_name"]} ]')
    page.get_by_role("dialog").locator('input[name="node_name"]').click()
    sleep(0.5)
    page.get_by_role("dialog").locator('input[name="node_name"]').fill(TEST_NODE["node_name"])
    page.get_by_role("dialog").locator('input[name="node_name"]').press("Enter")
    page.get_by_role("button", name="Update node").click()
    sleep(0.5)
    logger.warning(f'Имя узла изменено с [ {TEST_NODE["node_name"]}_1 ] на [ {TEST_NODE["node_name"]} ]')
    sleep(5)
    __unlock_ne(page, node_name=TEST_NODE["node_name"])


@pytest.fixture
def edit_ne_domain_fixture_t628(login_via_playwright):
    logger.info('Тест-кейс edit_ne_domain T628')
    page = login_via_playwright
    to_system_ne_control(page)
    select_ne(page, node_name=TEST_NODE['node_name'])
    sleep(0.5)
    __lock_ne(page, node_name=TEST_NODE['node_name'])
    sleep(0.5)
    page.get_by_role("cell", name=NODE_NAME).first.click(button="right")
    page.locator('#node_edit').click()
    sleep(0.5)
    logger.warning(f'Открыто модальное окно узла [ {NODE_NAME} ] для изменения домена узла на [ Beeline ]')
    sleep(0.5)

    page.locator("div:nth-child(8) > .react-select-container > .react-select-control > .css-fw4xp5 > .css-fo80f6").click()
    page.get_by_role("option", name="Beeline").click()


    sleep(1)
    page.get_by_role("button", name="Update node").click()
    sleep(0.5)
    logger.warning(f'Домен узла изменен на [ Beeline ]')
    sleep(1)
    node_table = table_data_text(page)
    logger.info(f'node_table: {node_table[0][1]}')
    yield node_table[0][1]

    page.get_by_role("cell", name=f'{TEST_NODE["node_name"]}').first.click(button="right")
    page.locator('#node_edit').click()
    sleep(0.5)

    logger.warning(f'Открыто модальное окно узла [ {TEST_NODE["node_name"]} ] для изменения домена узла на [ OT ]')
    # react_id_domain(page)
    page.locator("div:nth-child(8) > .react-select-container > .react-select-control > .css-fw4xp5 > .css-fo80f6").click()
    sleep(0.5)
    page.get_by_role("option", name="education").click()
    sleep(1)
    page.get_by_role("button", name="Update node").click()
    sleep(0.5)
    logger.warning(f'Домен узла изменен на [ education ]')
    sleep(0.5)
    __unlock_ne(page, node_name=TEST_NODE["node_name"])
    sleep(0.5)


@pytest.fixture
def edit_login_for_ne_fixture_t632(login_via_playwright):
    logger.info('Тест-кейс edit_login_for_ne T632')
    page = login_via_playwright
    to_system_ne_control(page)
    select_ne(page, node_name=TEST_NODE['node_name'])
    __lock_ne(page, node_name=TEST_NODE['node_name'])
    page.get_by_role("cell", name=TEST_NODE['node_name']).first.click(button="right")
    sleep(0.5)
    page.locator('#node_edit').click()
    logger.info(f'Click "Node Edit"')
    sleep(1)
    logger.warning(f'Открыто модальное окно узла [ {NODE_NAME} ] для изменения имени пользователя узла на [ {USER_FOR_NE}s ]')
    page.get_by_role("dialog").locator('input[name="user"]').click()
    sleep(0.5)
    page.get_by_role("dialog").locator('input[name="user"]').fill(f'{TEST_NODE["node_user"]}s')
    sleep(0.5)
    page.get_by_role("dialog").locator('input[name="user"]').press("Enter")
    page.get_by_role("button", name="Update node").click()
    sleep(0.5)
    logger.warning(f'Имя пользователя изменено с [ {TEST_NODE["node_user"]} ] на [ {TEST_NODE["node_user"]}s ]')
    sleep(5)
    result = page.locator('//table//tbody//tr//td[3]').all_text_contents()
    logger.info(f'{result=}')
    yield result

    page.get_by_role("cell", name=TEST_NODE["node_name"]).first.click(button="right")
    sleep(0.5)
    page.locator('#node_edit').click()
    sleep(0.5)
    logger.warning(f'Открыто модальное окно узла [ {TEST_NODE["node_user"]}s ] для изменения имени узла на [ {TEST_NODE["node_user"]} ]')
    page.get_by_role("dialog").locator('input[name="user"]').click()
    sleep(0.5)
    page.get_by_role("dialog").locator('input[name="user"]').fill(f'{TEST_NODE["node_user"]}')
    page.get_by_role("dialog").locator('input[name="user"]').press("Enter")
    page.get_by_role("button", name="Update node").click()
    sleep(0.5)
    logger.warning(f'Имя пользователя изменено с [ {TEST_NODE["node_name"]}s  ] на [ {TEST_NODE["node_name"]}]')
    sleep(5)
    __unlock_ne(page, node_name=TEST_NODE["node_name"])
    sleep(0.5)


@pytest.fixture
def edit_passwd_for_ne_fixture_t633(login_via_playwright):
    logger.info('Тест-кейс edit_passwd_for_ne T633')
    page = login_via_playwright
    to_system_ne_control(page)
    select_ne(page, node_name=TEST_NODE['node_name'])
    __lock_ne(page, node_name=TEST_NODE['node_name'])
    page.get_by_role("cell", name=TEST_NODE['node_name']).first.click(button="right")
    page.locator('#node_edit').click()
    sleep(0.5)
    logger.warning(f'Открыто модальное окно узла [ {TEST_NODE["node_name"]} ]')
    page.get_by_role("dialog").locator('input[name="password"]').click()
    page.get_by_role("dialog").locator('input[name="password"]').fill(f'{TEST_NODE["node_passw"]}')
    page.get_by_role("dialog").locator('input[name="password"]').press("Enter")
    page.get_by_role("button", name="Update node").click()
    sleep(0.5)
    logger.warning(f'Password пользователя изменен с [ {TEST_NODE["node_passw"]} ] на [ {TEST_NODE["node_passw"]+ "s"} ]')
    sleep(5)

    result = page.locator('//table//tbody//tr//td[3]').all_text_contents()
    logger.info(f'{result=}')
    yield result

    page.get_by_role("cell", name=TEST_NODE["node_name"]).first.click(button="right")
    sleep(0.5)
    page.locator('#node_edit').click()
    sleep(0.5)
    logger.warning(f'Открыто модальное окно узла [ {TEST_NODE["node_name"]} ]')
    page.get_by_role("dialog").locator('input[name="password"]').click()
    page.get_by_role("dialog").locator('input[name="password"]').fill(f'{TEST_NODE["node_passw"]}')
    page.get_by_role("dialog").locator('input[name="password"]').press("Enter")
    page.get_by_role("button", name="Update node").click()
    sleep(0.5)
    logger.warning(f'Password пользователя изменен с [ {TEST_NODE["node_passw"]+ "s"} ] на [ {TEST_NODE["node_passw"]} ]')
    sleep(5)
    __unlock_ne(page, node_name=TEST_NODE["node_name"])
    sleep(0.5)


@pytest.fixture
def edit_ip_ne_fixture_t625(login_via_playwright):
    logger.info('Тест-кейс edit_ip_ne T625')
    page = login_via_playwright
    to_system_ne_control(page)
    select_ne(page, node_name=TEST_NODE['node_name'])

    __lock_ne(page, TEST_NODE['node_name'])

    page.get_by_role("cell", name=TEST_NODE["node_name"]).first.click(button="right")
    page.locator('#node_edit').click()
    sleep(0.5)
    logger.warning(f'Открыто модальное окно узла [ {TEST_NODE["node_name"]} ] для изменения IP адреса узла')
    page.get_by_role("dialog").locator('input[name=\"ip\"]').click()
    page.get_by_role("dialog").locator('input[name=\"ip\"]').fill(CHANGE_IP)
    page.get_by_role("dialog").locator('input[name=\"ip\"]').press("Enter")
    page.get_by_role("button", name="Update node").click()
    sleep(0.5)
    logger.warning(f'IP адрес узла изменен с [ {TEST_NODE["node_ip"]} ] на [ {CHANGE_IP} ]')
    sleep(5)

    result = page.locator('//table//tbody//tr//td[10]').text_content()
    logger.info(f'{result=}')
    yield result

    page.get_by_role("cell", name=TEST_NODE["node_name"]).first.click(button="right")
    page.locator('#node_edit').click()
    sleep(0.5)
    logger.warning(f'Открыто модальное окно узла [ {TEST_NODE["node_name"]} ] для изменения IP адреса узла')
    page.get_by_role("dialog").locator('input[name=\"ip\"]').click()
    page.get_by_role("dialog").locator('input[name=\"ip\"]').fill(f'{TEST_NODE["node_ip"]}')
    page.get_by_role("dialog").locator('input[name=\"ip\"]').press("Enter")
    page.get_by_role("button", name="Update node").click()
    sleep(0.5)
    logger.warning(f'IP адрес узла [ {TEST_NODE["node_name"]} ] изменён с [ {CHANGE_IP} ] на [ {TEST_NODE["node_ip"]} ]')
    sleep(5)
    __unlock_ne(page, node_name=TEST_NODE["node_name"])
    sleep(0.5)


@pytest.fixture
def edit_port_for_ne_fixture_t631(login_via_playwright):
    logger.info('Тест-кейс edit_port_for_ne T631')
    page = login_via_playwright
    to_system_ne_control(page)
    select_ne(page, node_name=TEST_NODE['node_name'])

    __lock_ne(page, node_name=TEST_NODE['node_name'])

    page.get_by_role("cell", name=TEST_NODE['node_name']).first.click(button="right")
    page.locator('#node_edit').click()
    sleep(0.5)
    logger.warning(f'Открыто модальное окно узла [ {TEST_NODE["node_name"]} ] для изменения порта узла')
    page.get_by_role("dialog").locator('input[name="port"]').click()
    page.get_by_role("dialog").locator('input[name="port"]').fill(CHANGE_PORT)
    page.get_by_role("dialog").locator('input[name="port"]').press("Enter")
    page.get_by_role("button", name="Update node").click()
    sleep(0.5)
    logger.warning(f'Порт изменён с [ {TEST_NODE["node_port"]} ] на [ {CHANGE_PORT} ]')
    sleep(5)

    result = page.locator('//table//tbody//tr//td[3]').all_text_contents()
    logger.info(f'{result=}')
    yield result

    page.get_by_role("cell", name=TEST_NODE['node_name']).first.click(button="right")
    sleep(0.5)
    page.locator('#node_edit').click()
    sleep(0.5)
    logger.warning(f'Открыто модальное окно узла [ {TEST_NODE["node_name"]} ] для изменения порта узла')
    page.get_by_role("dialog").locator('input[name="port"]').click()
    page.get_by_role("dialog").locator('input[name="port"]').fill(f'{TEST_NODE["node_port"]}')
    page.get_by_role("dialog").locator('input[name="port"]').press("Enter")
    page.get_by_role("button", name="Update node").click()
    sleep(0.5)
    logger.warning(f'Порт изменён с [ {CHANGE_PORT} ] на [ {TEST_NODE["node_port"]} ]')
    sleep(5)
    __unlock_ne(page, node_name=TEST_NODE["node_name"])
    sleep(0.5)


@pytest.fixture
def transition_to_ne_management_t634(login_via_playwright):
    page = login_via_playwright
    logger.info('Тест-кейс transition_to_ne_management T634')

    page.get_by_role("cell", name=NODE_NAME1, exact=True).click(button='right')
    sleep(1)
    logger.warning(f'Открыто модальное окно узла [ {NODE_NAME1} ]')
    sleep(1)
    page.locator('#NodeGraphConfig').click()
    sleep(1)
    logger.warning('Открытие вкладки Management NE')
    result = page.locator(
        '#page-container > div.content-layout.h-100 > div > div > div.lm_header > ul.lm_tabs > li.lm_active')\
           .text_content()
    logger.info(f'{result=}')  # result='Management NE_50_TEST'
    yield result
    sleep(1)
    page.get_by_title(f'Management {NODE_NAME1}').locator('.lm_close_tab').click()
    sleep(1)
    logger.warning('Вкладка Management NE закрыта')
    sleep(1)


@pytest.fixture
def transition_to_oduxc_sncp_fixture_t1108(login_via_playwright):
    logger.info('Тест-кейс transition_to_oduxc_sncp T1108')
    page = login_via_playwright
    to_system_ne_control(page)
    select_ne(page, node_name=NODE_NAME1)

    page.get_by_role("cell", name=NODE_NAME1, exact=True).click(button='right')
    sleep(1)
    logger.warning(f'Открыто модальное окно узла [ {NODE_NAME1} ]')
    sleep(1)
    page.locator('#node_otn').click()
    sleep(1)
    page.locator('#NodeXCConfig').click()
    sleep(0.5)
    logger.warning('Открытие вкладки ODU XC & SNCP')

    result = page.locator('#page-container > div.content-layout.h-100 > div > div > div.lm_header > ul.lm_tabs > li.lm_active').text_content()
    logger.info(f'{result=}')
    yield result

    sleep(1)
    page.get_by_title(f'ODU CrossConnections Node {NODE_NAME1}').locator('.lm_close_tab').click()
    sleep(1)
    logger.warning('Вкладка ODU XC & SNCP закрыта')
    sleep(1)

@pytest.fixture
def transition_to_odu_protect_t1110(login_via_playwright):
    logger.info('Тест-кейс  transition_to_odu_protect T1110')

    page = login_via_playwright
    to_system_ne_control(page)
    select_ne(page, node_name=NODE_NAME1)

    page.get_by_role("cell", name=NODE_NAME1, exact=True).click(button='right')
    sleep(1)
    logger.warning(f'Открыто модальное окно узла [ {NODE_NAME1} ]')
    sleep(1)
    page.locator('#node_otn').click()
    sleep(1)
    page.locator('#NodeODUProtConfig').click()
    sleep(1)
    logger.warning('Открытие вкладки ODU Protection')
    sleep(1)

    result =  page.locator('#page-container > div.content-layout.h-100 > div > div > div.lm_header > ul.lm_tabs  > li.lm_active')\
        .text_content()
    logger.info(f'{result=}')
    yield result

    page.get_by_title(f'ODU Protection Node {NODE_NAME1}').locator('.lm_close_tab').click()
    logger.warning('Вкладка ODU Protection закрыта')


@pytest.fixture
def transition_to_odu_mux_t1112(login_via_playwright):
    logger.info('Тест-кейс transition_to_odu_mux T1112')

    page = login_via_playwright
    to_system_ne_control(page)
    select_ne(page, node_name=NODE_NAME1)

    page.get_by_role("cell", name=f'{NODE_NAME1}', exact=True).click(button='right')
    sleep(1)
    logger.warning(f'Открыто модальное окно узла [ {NODE_NAME1} ]')
    sleep(1)
    page.locator('#node_otn').click()
    sleep(1)
    page.locator('#NodeMuxConfig').click()
    sleep(1)
    logger.warning('Открытие вкладки ODU Multiplexing')
    sleep(1)

    result = page.locator('#page-container > div.content-layout.h-100 > div > div > div.lm_header > ul.lm_tabs')\
        .text_content()
    logger.info(f'{result=}')
    yield result

    sleep(1)
    page.get_by_title(f'ODU Multiplexing Node {NODE_NAME1}').locator('.lm_close_tab').click()
    sleep(1)
    logger.warning('Вкладка ODU Multiplexing закрыта')


@pytest.fixture
def transition_to_vroadm_t1129(login_via_playwright):
    logger.info('Тест-кейс transition_to_vroadm_t1129 T1129')

    page = login_via_playwright
    to_system_ne_control(page)
    select_ne(page, node_name=NODE_NAME1)

    page.get_by_role("cell", name=f'{NODE_NAME1}', exact=True).click(button='right')
    sleep(1)
    logger.warning(f'Открыто модальное окно узла [ {NODE_NAME1} ]')
    sleep(1)
    page.locator('#node_opt').click()
    sleep(1)
    page.locator('#NodeVROADMConfig').click()
    sleep(1)
    logger.warning('Открытие вкладки VROADM')
    sleep(1)

    result = page.locator('#page-container > div.content-layout.h-100 > div > div > div.lm_header > ul.lm_tabs > li.lm_active')\
        .text_content()
    logger.info(f'{result=}')
    yield result

    sleep(1)
    page.get_by_title(f'VROADM Node {NODE_NAME1}').locator('.lm_close_tab').click()
    sleep(1)
    logger.warning('Вкладка VROADM закрыта')
    sleep(1)


@pytest.fixture
def transition_to_nmc_connect_t1130(login_via_playwright):
    logger.info('Тест-кейс transition_to_nmc_connect T1130')

    page = login_via_playwright
    to_system_ne_control(page)
    select_ne(page, node_name=NODE_NAME1)

    page.get_by_role("cell", name=NODE_NAME1, exact=True).click(button='right')
    sleep(1)
    logger.warning(f'Открыто модальное окно узла [ {NODE_NAME1} ]')
    sleep(1)
    page.locator('#node_opt').click()
    sleep(1)
    page.locator('#NodeNMCConnConfig').click()
    sleep(1)
    logger.warning('Открытие вкладки NMC Connections')
    sleep(1)
    result = page.locator('#page-container > div.content-layout.h-100 > div > div > div.lm_header > ul.lm_tabs  > li.lm_active')\
        .text_content()
    logger.info(f'{result=}')
    yield result

    sleep(1)
    page.get_by_title(f'NMC Connections Node {NODE_NAME1}').locator('.lm_close_tab').click()
    sleep(1)
    logger.warning('Вкладка NMC Connections закрыта')
    sleep(1)


@pytest.fixture
def transition_to_opt_protect_t1131(login_via_playwright):
    logger.info('Тест-кейс transition_to_opt_protect T1131')

    page = login_via_playwright
    to_system_ne_control(page)
    select_ne(page, node_name=NODE_NAME1)

    page.get_by_role("cell", name=f'{NODE_NAME1}', exact=True).click(button='right')
    sleep(1)
    logger.warning(f'Открыто модальное окно узла [ {NODE_NAME1} ]')
    sleep(1)
    page.locator('#node_opt').click()
    sleep(1)
    page.locator('#NodeOPGConfig').click()
    sleep(1)
    logger.warning('Открытие вкладки Optical protection')

    result = page.locator('#page-container > div.content-layout.h-100 > div > div > div.lm_header > ul.lm_tabs  > li.lm_active')\
        .text_content()
    logger.info(f'{result=}')
    yield result

    sleep(1)
    page.get_by_title(f'Optical protection Node {NODE_NAME1}').locator('.lm_close_tab').click()
    sleep(1)
    logger.warning('Вкладка Optical protection закрыта')
    sleep(1)


@pytest.fixture
def transition_to_alarm_log_t636(login_via_playwright):
    logger.info('Тест-кейс transition_to_alarm_log T636')

    page = login_via_playwright
    to_system_ne_control(page)
    select_ne(page, node_name=NODE_NAME1)

    page.get_by_role("cell", name=f'{NODE_NAME1}', exact=True).click(button='right')
    sleep(2)
    logger.warning(f'Открыто модальное окно узла {NODE_NAME1} ')
    sleep(2)
    page.locator('#node_fault').click()
    sleep(2)
    page.locator('#NodeAlarms').click()
    sleep(2)
    logger.warning('Открытие вкладки Current Alarms')
    sleep(2)

    result = page.locator(
        '#page-container > div.content-layout.h-100 > div > div > div.lm_header > ul.lm_tabs > li.lm_active')\
        .text_content()
    logger.info(f'{result=}')
    yield result

    sleep(1)
    page.get_by_title(f'Current Alarms Node {NODE_NAME1}').locator('.lm_close_tab').click()
    sleep(1)
    logger.warning('Вкладка Current Alarms закрыта')
    sleep(1)


@pytest.fixture
def transition_to_event_log_t637(login_via_playwright):
    logger.info('Тест-кейс transition_to_event_log T637')

    page = login_via_playwright
    to_system_ne_control(page)
    select_ne(page, node_name=NODE_NAME1)

    page.get_by_role("cell", name=NODE_NAME1, exact=True).click(button='right')
    logger.warning(f'Открыто модальное окно узла {NODE_NAME1}')
    sleep(0.5)
    page.locator('#node_fault').click()
    sleep(0.5)
    page.locator('#NodeEvents').click()
    sleep(10)
    logger.warning('Открытие вкладки Events')
    result_text = page.locator(
        '#page-container > div.content-layout.h-100 > div > div > div.lm_header > ul.lm_tabs > li.lm_active').text_content()
    sleep(0.5)
    logger.info(f'{result_text=}')
    yield result_text

    page.get_by_title(f'Events Node {NODE_NAME1}').locator('.lm_close_tab').click()
    sleep(0.5)
    logger.warning('Вкладка Events закрыта')
    sleep(0.5)


@pytest.fixture
def transition_to_asap_profile_fixture_t1105(login_via_playwright):
    logger.info('Тест-кейс transition_to_asap_profile T1105')

    page = login_via_playwright
    to_system_ne_control(page)
    select_ne(page, node_name=NODE_NAME1)

    page.get_by_role("cell", name=NODE_NAME1, exact=True).click(button='right')
    sleep(1)
    logger.warning(f'Открыто модальное окно узла {NODE_NAME1}')
    sleep(1)
    page.locator('#node_fault').click()
    sleep(1)
    page.locator('#NodeASAPConfig').click()
    sleep(1)
    logger.warning('Открытие вкладки ASAP')
    sleep(1)

    result = page.locator('#page-container > div.content-layout.h-100 > div > div > div.lm_header > ul.lm_tabs  > li.lm_active')\
        .text_content()
    logger.info(f'{result=}')
    yield result

    sleep(1)
    page.get_by_title(f'ASAP Node {NODE_NAME1}').locator('.lm_close_tab').click()
    sleep(1)
    logger.warning('Вкладка ASAP закрыта')


@pytest.fixture
def transition_to_asap_exception_fixture_t1106(login_via_playwright):
    logger.info('Тест-кейс transition_to_asap_exception T1106')

    page = login_via_playwright
    to_system_ne_control(page)
    select_ne(page, node_name=NODE_NAME1)

    page.get_by_role("cell", name=NODE_NAME1, exact=True).click(button='right')
    sleep(0.5)
    logger.warning(f'Открыто модальное окно узла [ {NODE_NAME1} ]')
    page.locator('#node_fault').click()
    sleep(0.5)
    page.locator('#NodeASAPExConfig').click()
    sleep(0.5)
    logger.warning('Открытие вкладки ASAP Exceptions')

    result = page.locator('#page-container > div.content-layout.h-100 > div > div > div.lm_header > ul.lm_tabs  > li.lm_active')\
        .text_content()
    logger.info(f'{result=}')
    yield result

    page.get_by_title(f'ASAP Exceptions Node {NODE_NAME1}').locator('.lm_close_tab').click()
    sleep(0.5)
    logger.warning('Вкладка ASAP Exceptions закрыта')


@pytest.fixture
def transition_to_sens_tca_fixture_t1132(login_via_playwright):
    logger.info('Тест-кейс transition_to_sens_tca T1132')

    page = login_via_playwright
    to_system_ne_control(page)
    select_ne(page, node_name=NODE_NAME1)

    page.get_by_role("cell", name=NODE_NAME1, exact=True).click(button='right')
    sleep(1)
    logger.warning(f'Открыто модальное окно узла {NODE_NAME1}')
    sleep(1)
    page.locator('#node_perf').click()
    sleep(1)
    page.locator('#NodeTCAConfig').click()
    sleep(1)
    logger.warning('Открытие вкладки Sensors & TCA')
    sleep(1)

    result = page.locator('#page-container > div.content-layout.h-100 > div > div > div.lm_header > ul.lm_tabs  > li.lm_active')\
        .text_content()
    logger.info(f'{result=}')
    yield result

    sleep(1)
    page.get_by_title(f'Sensors & TCA Node {NODE_NAME1}').locator('.lm_close_tab').click()
    sleep(1)
    logger.warning('Вкладка Sensors & TCA закрыта')
    sleep(1)



@pytest.fixture
def mass_adm_unlock_t1133(login_via_playwright):
    logger.info('Тест-кейс mass_adm_unlock T1333')   # Mass edit nodes

    page = login_via_playwright
    to_system_ne_control(page)
    select_ne(page, node_name=NODE_LIST_FOR_MASS_OPS)

    table11__id = table11_id(page)    # example: 'pid_GXyc'

    # below; get table data  with selected 3 nodes
    table_rows = table_data_web(page)
    # # logger.info(f'{table_info=}')

    # below: make list of NE names in the group
    ne_names = []
    for el in table_rows:
        if el.get_attribute('class') != 'h-100':
            sleep(0.5)
            ne_names.append(el.locator('//td').all_text_contents()[2])
    logger.info(f'{ne_names=}')

    # below: select each node in the group
    for el in ne_names:
        page.locator(f'#{table11__id}id_scrollableTableContainer') \
            .locator('tbody').locator(f'tr:has-text("{el}"):visible').locator('i').first.click()
        sleep(1)

    # below: click on first node and mass-lock the group
    page.locator(f'#{table11__id}id_scrollableTableContainer') \
        .locator('tbody').locator(f'tr:has-text("{ne_names[0]}"):visible')\
        .get_by_role("cell", name=f"{ne_names[0]}", exact=True).click(button='right')
    sleep(1)
    page.get_by_role("link", name="Mass Adm State").click()
    sleep(1)
    # page.get_by_role("link", name=f"Unlock {len(ne_names)} nodes").first.click()
    page.locator('#Unlock').first.click()
    sleep(2)
    page.get_by_role("button", name=f"Unlock {len(ne_names)} nodes").click()
    sleep(2)

    # below: check status of subject nodes : "Locked"/"Unlocked"
    result = []
    for el in ne_names:
        attr = page.locator(f'#{table11__id}id_scrollableTableContainer') \
            .locator('tbody').locator(f'tr:has-text("{el}"):visible') \
            .locator('td').nth(5).locator('i').get_attribute('data-value')

        result.append(attr)

    logger.info(f'{result=}')
    yield result

    # below: close page "NE Control"
    page.locator(
        '#page-container > div.content-layout.h-100 > div > div > div.lm_header > ul.lm_tabs > li.lm_active')\
        .click(button='middle')
    sleep(1)
    logger.warning('Вкладка "NE Control" закрыта')
    sleep(1)


@pytest.fixture
def transition_to_gauge_stat_fixture_t1134(login_via_playwright):
    logger.info('Тест-кейс transition_to_gauge_stat T1134')

    page = login_via_playwright
    to_system_ne_control(page)
    select_ne(page, node_name=NODE_NAME1)

    page.get_by_role("cell", name=NODE_NAME1, exact=True).click(button='right')
    sleep(1)
    logger.warning(f'Открыто модальное окно узла {NODE_NAME} ')
    page.get_by_role("cell", name=f'{NODE_NAME1}', exact=True).click(button='right')
    sleep(1)
    page.locator('#node_perf').click()
    sleep(1)
    page.locator('#NodePMG').click()
    sleep(1)
    logger.warning('Открытие вкладки Gauge Statistics')
    sleep(1)

    result = page.locator('#page-container > div.content-layout.h-100 > div > div > div.lm_header > ul.lm_tabs  > li.lm_active')\
        .text_content()
    logger.info(f'{result=}')
    yield result

    sleep(1)
    page.get_by_title(f'Gauge Statistics Node {NODE_NAME1}').locator('.lm_close_tab').click()
    sleep(1)
    logger.warning('Вкладка Gauge Statistics закрыта')
    sleep(1)


@pytest.fixture
def transition_to_pm_stat_fixture_t1135(login_via_playwright):
    logger.info('Тест-кейс transition_to_pm_stat T1135')

    page = login_via_playwright
    to_system_ne_control(page)
    select_ne(page, node_name=f'{NODE_NAME1}')

    page.get_by_role("cell", name=f'{NODE_NAME1}', exact=True).click(button='right')
    sleep(1)
    logger.warning(f'Открыто модальное окно узла [ {NODE_NAME1} ]')
    sleep(1)
    page.locator('#node_perf').click()
    sleep(1)
    page.locator('#NodePM').click()
    sleep(1)
    logger.warning('Открытие вкладки PM Statistics')
    sleep(1)

    result = page.locator('#page-container > div.content-layout.h-100 > div > div > div.lm_header > ul.lm_tabs  > li.lm_active')\
        .text_content()
    logger.info(f'{result=}')
    yield result

    page.get_by_title(f'PM Statistics Node {NODE_NAME1}').locator('.lm_close_tab').click()
    sleep(0.5)
    logger.warning('Вкладка PM Statistics закрыта')


@pytest.fixture
def transition_to_chs_view_fixture_t1166(login_via_playwright):
    logger.info('Тест-кейс transition_to_chs_view T1166')

    page = login_via_playwright
    to_system_ne_control(page)
    select_ne(page, node_name=f'{NODE_NAME1}')

    page.get_by_role("cell", name=f'{NODE_NAME1}', exact=True).click(button='right')
    sleep(1)
    logger.warning(f'Открыто модальное окно узла [ {NODE_NAME1} ]')
    sleep(1)
    page.locator('#node_phys').click()
    sleep(1)
    page.locator('#NodeLinkConfig').click()
    sleep(1)
    logger.warning('Открытие вкладки Link Management')
    sleep(1)

    result = page.locator('#page-container > div.content-layout.h-100 > div > div > div.lm_header > ul.lm_tabs  > li.lm_active')\
        .text_content()
    logger.info(f'{result=}')
    yield result

    sleep(1)
    page.get_by_title(f'Link Management {NODE_NAME1}').locator('.lm_close_tab').click()
    sleep(1)
    logger.warning('Вкладка Link Management закрыта')
    sleep(1)


@pytest.fixture
def transition_to_2d_diagram_fixture_t1165(login_via_playwright):
    logger.info('Тест-кейс transition_to_2d_diagram T1165')

    page = login_via_playwright
    to_system_ne_control(page)
    select_ne(page, node_name=f'{NODE_NAME1}')

    page.get_by_role("cell", name=f'{NODE_NAME1}', exact=True).click(button='right')
    sleep(1)
    logger.warning(f'Открыто модальное окно узла [ {NODE_NAME1} ]')
    sleep(1)
    page.locator('#node_phys').click()
    sleep(1)
    page.locator('#SmartPhysLinkConfig').click()
    sleep(1)
    logger.warning('Открытие вкладки Graph link Management')
    sleep(1)

    result = page.locator('#page-container > div.content-layout.h-100 > div > div > div.lm_header > ul.lm_tabs  > li.lm_active')\
        .text_content()
    logger.info(f'{result=}')
    yield result

    sleep(1)
    page.get_by_title(f'Graph link Management {NODE_NAME1}').locator('.lm_close_tab').click()
    sleep(1)
    logger.warning('Вкладка Graph link Management закрыта')
    sleep(1)


@pytest.fixture
def transition_to_conf_tree_fixture_t1167(login_via_playwright):
    logger.info('Тест-кейс transition_to_conf_tree T1167')

    page = login_via_playwright
    to_system_ne_control(page)
    select_ne(page, node_name=f'{NODE_NAME1}')

    page.get_by_role("cell", name=f'{NODE_NAME1}', exact=True).click(button='right')
    sleep(1)
    logger.warning(f'Открыто модальное окно узла [ {NODE_NAME1} ]')
    sleep(1)
    page.locator('#NodeConfig').click()
    sleep(1)
    logger.warning('Открытие вкладки Config Tree')
    sleep(1)

    result = page.locator('#page-container > div.content-layout.h-100 > div > div > div.lm_header > ul.lm_tabs  > li.lm_active')\
        .text_content()
    logger.info(f'{result=}')
    yield result

    sleep(1)
    page.get_by_title(f'Config Tree {NODE_NAME1}').locator('.lm_close_tab').click()
    sleep(1)
    logger.warning('Вкладка Config Tree закрыта')


@pytest.fixture
def transition_to_software_upgrade_fixture_t635(login_via_playwright):
    logger.info('Тест-кейс transition_to_software_upgrade T635')

    page = login_via_playwright
    to_system_ne_control(page)
    select_ne(page, node_name=NODE_NAME1)

    page.get_by_role("cell", name=f"{NODE_NAME1}", exact=True).click(button='right')
    sleep(0.5)
    logger.warning(f'Открыто модальное окно узла {NODE_NAME1}')
    sleep(0.5)
    page.locator('#nodeSWUpgrade').click()
    sleep(0.5)
    logger.warning('Открытие вкладки "Software Upgrade" ')
    sleep(1)

    result = page.locator('#page-container > div.content-layout.h-100 > div > div > div.lm_header > ul.lm_tabs  > li.lm_active')\
        .text_content()
    logger.info(f'{result=}')
    yield result

    sleep(1)
    page.get_by_title(f'Node {NODE_NAME1} upgrade management').locator('.lm_close_tab').click()
    sleep(2)
    logger.warning('Вкладка Upgrade management закрыта')


@pytest.fixture
def transition_to_lct_t1168(login_via_playwright):
    logger.info('Тест-кейс transition_to_lct T1168')

    NODE_NAME1 = 'shass_157'

    page = login_via_playwright
    to_system_ne_control(page)
    select_ne(page, node_name=NODE_NAME1)

    page.get_by_role("cell", name=f'{NODE_NAME1}', exact=True).click(button='right')
    sleep(0.5)
    logger.warning(f'Открыто модальное окно узла [ {NODE_NAME1} ]')
    sleep(0.5)
    with page.expect_popup() as page1_info:
        page.locator('#nodeOpenLCT').click()
    sleep(5)

    page1 = page1_info.value
    result = page1.locator('.brand').text_content()
    sleep(1)
    if "T8 АКСОН" in result:
        result = "T8 АКСОН"
        logger.info(f'{result=}')
        yield result
    else:
        yield None
    if page1:
        logger.info("LCT page closed")
        page1.close()
        sleep(0.5)


@pytest.fixture
def ping_ne_t1172(login_via_playwright):
    logger.info('Тест-кейс ping_ne Т1172 for shass_157')

    page = login_via_playwright
    to_system_ip_addresses(page)
    select_ne(page, node_name=f'{PING_DATA["node_name"]}')

    sleep(0.5)
    table_info = table_data_web(page)

    ip_found = False
    for el in table_info:
        if el.inner_text() == '':
            break
        ip_table_record = el.inner_text().split('\t')
        logger.info(f'{ip_table_record[1]=}   {ip_table_record[5]=}')

        if ip_table_record[1] == PING_DATA['node_name'] and ip_table_record[5] == PING_DATA['target_ip']:
            el.get_by_role("cell", name=f'{PING_DATA["node_name"]}', exact=True).click(button='right')
            logger.info(f'Node {PING_DATA["node_name"]} found, click')
            ip_found = True
            break
    if not ip_found:
        logger.info('The target PING_DATA node not found in list')
        return -1

    sleep(0.5)
    page.locator('#ping').click()
    sleep(0.5)

    logger.warning(f'Открыто модальное окно PING')
    sleep(0.5)

    page.locator('.modal-dialog >> .modal-content:visible').\
        locator('.modal-react >> .form-group').first.locator('input').click()
    sleep(0.5)
    page.locator('.modal-dialog >> .modal-content:visible'). \
        locator('.modal-react >> .form-group').first.locator('input').fill(f'{PING_DATA["target_ip"]}')
    logger.info(f'Fill IP: {PING_DATA["target_ip"]}')
    sleep(0.5)

    current_input = page.locator(".modal-dialog >> .modal-content:visible").\
        locator(".modal-react >> .form-group:nth-child(2) >> .react-select-container >> .react-select-control").inner_text()
    logger.info(f'{PING_DATA["source"]=}')

    if current_input == PING_DATA['source']:
        pass
    else:
        page.locator(".modal-dialog >> .modal-content:visible")\
            .locator(".modal-react >> .form-group:nth-child(2) >> .react-select-container >> .react-select-control").click()
        page.get_by_role("option", name=f'{PING_DATA["source"]}').click()
        sleep(0.5)
    logger.info(f'Fill Source: {PING_DATA["source"]}')

    page.locator('.modal-dialog >> .modal-content:visible').\
        locator('.modal-react >> .form-group').nth(2).locator('input').click()
    page.locator('.modal-dialog >> .modal-content:visible').\
        locator('.modal-react >> .form-group').nth(2).locator('input').fill(f'{PING_DATA["packet_len"]}')
    logger.info(f'Fill Packet_Length: {PING_DATA["packet_len"]}')
    sleep(0.5)

    page.locator('.modal-dialog >> .modal-content:visible').\
        locator('.modal-react >> .form-group').nth(3).locator('input').click()
    page.locator('.modal-dialog >> .modal-content:visible').\
        locator('.modal-react >> .form-group').nth(3).locator('input').fill(f'{PING_DATA["quantity"]}')
    logger.info(f'Fill Packet_Quantity: {PING_DATA["quantity"]}')
    sleep(0.5)

    page.locator('.modal-dialog >> .modal-content:visible').\
        locator('.modal-react >> .form-group').nth(4).locator('input').click()
    page.locator('.modal-dialog >> .modal-content:visible').\
        locator('.modal-react >> .form-group').nth(4).locator('input').fill(f'{PING_DATA["interval"]}')
    logger.info(f'Fill Ping_Interval: {PING_DATA["interval"]}')
    sleep(0.5)

    page.locator('.modal-dialog >> .modal-content:visible').\
        locator('.modal-react >> .form-group').nth(5).locator('input').click()
    page.locator('.modal-dialog >> .modal-content:visible').\
        locator('.modal-react >> .form-group').nth(5).locator('input').fill(f'{PING_DATA["timeout"]}')
    logger.info(f'Fill Timeout: {PING_DATA["timeout"]}')
    sleep(0.5)

    page.locator('div.modal-dialog >> div.modal-content')\
        .page.get_by_role("button", name="Execute").click()
    logger.info(f'Click "Execute"')
    sleep(1)
    ping_not_ready = True
    result_dict = {}
    while ping_not_ready:
        result = page.locator(f'#container_item_2').all_inner_texts()
        result = result[0].split('\n')
        for el in result:
            el_list = el.split(":")
            result_dict[el_list[0]] = el_list[1].strip()
        if result_dict['Status'] == 'done':
            break
        sleep(0.5)
    logger.info(f'Reading results')
    page.locator(f'#container_item_2').click()
    sleep(5)
    result_text = page.locator('#id_div_target_log > div').nth(1).inner_text()
    page.locator('div.modal-dialog >> div.modal-content') \
        .page.get_by_role("button", name="Close").click()

    sleep(1)
    logger.info(f'{result_text=}')
    yield result_text

    page.locator(
        '#page-container > div.content-layout.h-100 > div > div > div.lm_header > ul.lm_tabs > li.lm_active') \
        .click(button='middle')
    sleep(0.5)


@pytest.fixture
def traceroute_ne_t1173(login_via_playwright):
    logger.info('Тест-кейс test_traceroute_ne T1173 ')

    page = login_via_playwright
    to_system_ip_addresses(page)
    select_ne(page, node_name=f'{TRACEROUTE_DATA["node_name"]}')

    sleep(0.5)
    table_info = table_data_web(page)

    ip_found = False
    for el in table_info:
        if el.inner_text() == '':
            break
        ip_table_record = el.inner_text().split('\t')

        if ip_table_record[1] == TRACEROUTE_DATA['node_name'] and ip_table_record[5] == TRACEROUTE_DATA['target_ip']:
            el.get_by_role("cell", name=f'{TRACEROUTE_DATA["node_name"]}', exact=True).click(button='right')
            ip_found = True
            break
    if not ip_found:
        logger.info('The target TRACEROUTE_DATA node not found in list')
        return -1

    sleep(0.5)
    page.locator('#traceroute').click()
    logger.info('Click on "traceroute"')
    sleep(0.5)

    logger.warning(f'Открыто модальное окно TRACEROUTE')
    sleep(0.5)

    page.locator('.modal-dialog >> .modal-content:visible'). \
        locator('.modal-react >> .form-group').first.locator('input').click()
    sleep(0.5)
    page.locator('.modal-dialog >> .modal-content:visible'). \
        locator('.modal-react >> .form-group').first.locator('input').fill(f'{TRACEROUTE_DATA["target_ip"]}')
    logger.info(f'Fill IP: {TRACEROUTE_DATA["target_ip"]}')
    sleep(0.5)

    current_input = page.locator(".modal-dialog >> .modal-content:visible"). \
        locator(
        ".modal-react >> .form-group:nth-child(2) >> .react-select-container >> .react-select-control").inner_text()

    if current_input == TRACEROUTE_DATA['source']:
        pass
    else:
        page.locator(".modal-dialog >> .modal-content:visible") \
            .locator(
            ".modal-react >> .form-group:nth-child(2) >> .react-select-container >> .react-select-control").click()
        page.get_by_role("option", name=f'{TRACEROUTE_DATA["source"]}').click()
        sleep(0.5)
    logger.info(f'Fill Source: {TRACEROUTE_DATA["source"]}')

    page.locator('.modal-dialog >> .modal-content:visible'). \
        locator('.modal-react >> .form-group').nth(2).locator('input').click()
    page.locator('.modal-dialog >> .modal-content:visible'). \
        locator('.modal-react >> .form-group').nth(2).locator('input').fill(f'{TRACEROUTE_DATA["timeout"]}')
    logger.info(f'Fill Timeout: {TRACEROUTE_DATA["timeout"]}')
    sleep(0.5)

    page.locator('.modal-dialog >> .modal-content:visible'). \
        locator('.modal-react >> .form-group').nth(3).locator('input').click()
    page.locator('.modal-dialog >> .modal-content:visible'). \
        locator('.modal-react >> .form-group').nth(3).locator('input').fill(f'{TRACEROUTE_DATA["max_ttl"]}')
    logger.info(f'Fill Max TTL: {TRACEROUTE_DATA["max_ttl"]}')
    sleep(0.5)

    page.locator('div.modal-dialog >> div.modal-content') \
        .page.get_by_role("button", name="Execute").click()
    sleep(0.5)
    ping_not_ready = True
    result_dict = {}
    while ping_not_ready:
        result = page.locator(f'#container_item_2').all_inner_texts()
        result = result[0].split('\n')
        for el in result:
            el_list = el.split(":")
            result_dict[el_list[0]] = el_list[1].strip()
        if result_dict['Status'] == 'done':
            break
        sleep(0.5)
    logger.info('Open result table')
    page.locator(f'#container_item_2').click()
    result_text = page.locator('#log_ul_2').inner_text()
    result_text = result_text.split(',')

    sleep(0.5)
    page.locator('div.modal-dialog >> div.modal-content') \
        .page.get_by_role("button", name="Close").click()
    logger.info(f'result_text: {result_text[2]}')
    yield result_text[2]

    sleep(0.5)
    page.locator(
        '#page-container > div.content-layout.h-100 > div > div > div.lm_header > ul.lm_tabs > li.lm_active') \
        .click(button='middle')
    sleep(2)


@pytest.fixture
def transition_to_object_fixture_t1174(login_via_playwright):
    logger.info('Тест-кейс test_transition_to_object_t1174 for shass_157')

    page = login_via_playwright
    to_system_ip_addresses(page)
    select_ne(page, node_name=f'{NODE_NAME1}')

    table_info = table_data_web(page)
    for row in table_info:
        if f'{NODE_NAME1}' in row.inner_text() and '192.168.' in row.inner_text() :
            row.get_by_role("cell", name=f"{NODE_NAME1}", exact=True).click(button='right')
            page.locator('#showObject').click()
            break
    table_header = page.locator(
        '#page-container > div.content-layout.h-100 > div > div > div.lm_header > ul.lm_tabs > li.lm_active')\
        .text_content()
    logger.info('Get list of all table headers')
    logger.info(f'{table_header=}')
    yield table_header

    sleep(0.5)
    page.locator(
        '#page-container > div.content-layout.h-100 > div > div > div.lm_header > ul.lm_tabs > li.lm_active') \
        .click(button='middle')
    sleep(0.5)
    logger.warning('Вкладка "IP Addresses" закрыта')
    sleep(0.5)



@pytest.fixture
def mass_edit_network_nodes_t1331(login_via_playwright):
    logger.info('Тест-кейс mass_edit_network_nodes T1331')   # Mass edit nodes


    page = login_via_playwright
    to_system_ne_control(page)
    select_ne(page, node_name=NODE_LIST_FOR_MASS_OPS)

    table11__id = table11_id(page)    # example: 'pid_GXyc'
    table_rows = table_data_web(page)

    ne_names = []
    for el in table_rows:
        if el.get_attribute('class') != 'h-100':
            sleep(0.5)
            # logger.info(f"{el.locator('//td').all_text_contents()[2]=}")
            ne_names.append(el.locator('//td').all_text_contents()[2])
    logger.info(f'{ne_names=}')

    # below: select each node in the group
    for el in ne_names:
        page.locator(f'#{table11__id}id_scrollableTableContainer') \
            .locator('tbody').locator(f'tr:has-text("{el}"):visible').locator('i').first.click()
        sleep(1)

    # below: click on first node and mass-lock the group
    page.locator(f'#{table11__id}id_scrollableTableContainer') \
        .locator('tbody').locator(f'tr:has-text("{ne_names[0]}"):visible')\
        .get_by_role("cell", name=f"{ne_names[0]}", exact=True).click(button='right')
    sleep(1)
    page.get_by_role("link", name="Mass Edit Network nodes").click()
    sleep(1)
    # page.get_by_role("link", name=f"Lock {len(ne_names)} nodes").first.click()

    # below doesn't work

    page.locator("input[name=\"domain_flag\"]").click()  # click on "Domain" check-box
    page.locator("#react-select-3-input").fill("education")     # trying to change Domain to education - Not Success
    page.locator("#react-select-3-input").press("Enter")
    page.locator("svg").nth(1).click()                 # tryting to het domain list - Not Success
    sleep(0.5)

    # below: check status of subject nodes : "Locked"/"Unlocked"
    result = []
    for el in ne_names:
        attr = page.locator(f'#{table11__id}id_scrollableTableContainer') \
            .locator('tbody').locator(f'tr:has-text("{el}"):visible') \
            .locator('td').nth(5).locator('i').get_attribute('data-value')

        result.append(attr)

    # below: close page "NE Control"
    logger.info(f'{result=}')
    yield result

    page.locator(
        '#page-container > div.content-layout.h-100 > div > div > div.lm_header > ul.lm_tabs > li.lm_active')\
        .click(button='middle')
    sleep(1)
    logger.warning('Вкладка "NE Control" закрыта')
    sleep(1)


@pytest.fixture
def mass_adm_lock_t1332(login_via_playwright):
    logger.info('Тест-кейс mass_adm_lock T1332')  # Mass lock nodes
    page = login_via_playwright
    to_system_ne_control(page)
    select_ne(page, node_name=NODE_LIST_FOR_MASS_OPS)
    table11__id = table11_id(page)
    # below; get table data  with selected 3 nodes
    table_rows = table_data_web(page)
    # logger.info(f'{table_info=}')

    # below: make list of NE names in the group
    ne_names = []
    for el in table_rows:
        if el.get_attribute('class') != 'h-100':
            sleep(0.5)
            # logger.info(f"{el.locator('//td').all_text_contents()[2]=}")
            ne_names.append(el.locator('//td').all_text_contents()[2])

    # below: select each node in the group
    for el in ne_names:
        page.locator(f'#{table11__id}id_scrollableTableContainer') \
            .locator('tbody').locator(f'tr:has-text("{el}"):visible').locator('i').first.click()
        logger.info(f'Selected node {el}')
        sleep(1)
    sleep(1)

    # below: click on first node and mass-lock the group
    page.locator(f'#{table11__id}id_scrollableTableContainer') \
        .locator('tbody').locator(f'tr:has-text("{ne_names[0]}"):visible') \
        .get_by_role("cell", name=f"{ne_names[0]}", exact=True).click(button='right')
    sleep(1)
    page.get_by_role("link", name="Mass Adm State").click()
    sleep(1)

    page.locator('#Lock').first.click()
    sleep(2)
    page.get_by_role("button", name=f"Lock {len(ne_names)} nodes").click()
    sleep(2)

    # below: check status of subject nodes : "Locked"/"Unlocked"
    result = []
    for el in ne_names:
        attr = page.locator(f'#{table11__id}id_scrollableTableContainer') \
            .locator('tbody').locator(f'tr:has-text("{el}"):visible') \
            .locator('td').nth(5).locator('i').get_attribute('data-value')

        result.append(attr)
    logger.info(f'{result=}')
    yield result

    # below: close page "NE Control"
    page.locator(
        '#page-container > div.content-layout.h-100 > div > div > div.lm_header > ul.lm_tabs > li.lm_active') \
        .click(button='middle')
    sleep(1)
    logger.warning('Вкладка "NE Control" закрыта')
    sleep(1)


@pytest.fixture
def mass_adm_unlock_t1333(login_via_playwright):
    logger.info('Тест-кейс mass_adm_unlock T1333')   # Mass edit nodes

    page = login_via_playwright
    to_system_ne_control(page)
    select_ne(page, node_name=NODE_LIST_FOR_MASS_OPS)

    table11__id = table11_id(page)    # example: 'pid_GXyc'

    # below; get table data  with selected 3 nodes
    table_rows = table_data_web(page)
    # # logger.info(f'{table_info=}')

    # below: make list of NE names in the group
    ne_names = []
    for el in table_rows:
        if el.get_attribute('class') != 'h-100':
            sleep(0.5)
            ne_names.append(el.locator('//td').all_text_contents()[2])
    logger.info(f'{ne_names=}')

    # below: select each node in the group
    for el in ne_names:
        page.locator(f'#{table11__id}id_scrollableTableContainer') \
            .locator('tbody').locator(f'tr:has-text("{el}"):visible').locator('i').first.click()
        logger.info(f'Selected node {el}')
        sleep(1)

    # below: click on first node and mass-lock the group
    page.locator(f'#{table11__id}id_scrollableTableContainer') \
        .locator('tbody').locator(f'tr:has-text("{ne_names[0]}"):visible')\
        .get_by_role("cell", name=f"{ne_names[0]}", exact=True).click(button='right')
    sleep(1)
    page.get_by_role("link", name="Mass Adm State").click()
    sleep(1)

    page.locator('#Unlock').first.click()
    sleep(2)
    page.get_by_role("button", name=f"Unlock {len(ne_names)} nodes").click()
    sleep(2)

    # below: check status of subject nodes : "Locked"/"Unlocked"
    result = []
    for el in ne_names:
        attr = page.locator(f'#{table11__id}id_scrollableTableContainer') \
            .locator('tbody').locator(f'tr:has-text("{el}"):visible') \
            .locator('td').nth(5).locator('i').get_attribute('data-value')

        result.append(attr)

    logger.info(f'{result=}')
    yield result

    # below: close page "NE Control"
    page.locator(
        '#page-container > div.content-layout.h-100 > div > div > div.lm_header > ul.lm_tabs > li.lm_active')\
        .click(button='middle')
    sleep(1)
    logger.warning('Вкладка "NE Control" закрыта')
    sleep(1)

# ----------------------------------
#       IP TUNNELS TEST CASES BELOW
# ----------------------------------


@pytest.fixture
def ip_tunnel_create_1176(login_via_playwright):
    logger.info('Тест-кейс ip_tunnel_create T1176')   # IP Tunnel Create

    page = login_via_playwright
    to_system_ip_tunnels(page)
    sleep(0.5)
    if if_ip_tunnel_exist(page, tunnel_data=IP_TUNNEL_DATA1):
        return -1
    ip_tunnel_create(page, tunnel_data=IP_TUNNEL_DATA1)
    sleep(4)   # Mandatory Timeout to refresh page

    logger.info('Reading result table')
    all_ip_tunnels = table_data_text(page)
    result = [el[1:] for el in all_ip_tunnels]

    logger.info(f'{result=}')
    yield result

    page.locator(
        '#page-container > div.content-layout.h-100 > div > div > div.lm_header > ul.lm_tabs > li.lm_active') \
        .click(button='middle')
    sleep(0.5)


@pytest.fixture
def ip_tunnel_edit_1177(login_via_playwright):
    logger.info('Тест-кейс ip_tunnel_edit T1177')   # IP Tunnel Edit

    page = login_via_playwright
    to_system_ip_tunnels(page)

    sleep(2)  # Mandatory timeout to refresh page

    if not if_ip_tunnel_exist(page, tunnel_data=IP_TUNNEL_DATA1):
        logger.info('The IP Tunnel not found in list')
        return -1
    ip_tunnel_edit(page, IP_TUNNEL_DATA1, IP_TUNNEL_DATA2)

    sleep(2)  # Mandatory timeout to refresh page

    logger.info('Reading result table')
    all_ip_tunnels = table_data_text(page)
    sleep(0.5)

    result = [el[1:] for el in all_ip_tunnels]
    logger.info(f'{result=}')
    yield result

    page.locator(
        '#page-container > div.content-layout.h-100 > div > div > div.lm_header > ul.lm_tabs > li.lm_active') \
        .click(button='middle')

    sleep(0.5)


@pytest.fixture
def ip_tunnel_delete_1178(login_via_playwright):
    page = login_via_playwright
    logger.info('Тест-кейс ip_tunnel_delete T1178')   # IP Tunnel Delete
    to_system_ip_tunnels(page)
    sleep(1)

    if not if_ip_tunnel_exist(page, IP_TUNNEL_DATA2):
        return -1
    sleep(0.5)
    ip_tunnel_delete(page, IP_TUNNEL_DATA2)
    sleep(2)  # Mandatory timeout to refresh page

    logger.info('Reading result table')
    all_ip_tunnels = table_data_text(page)
    sleep(0.5)

    result = [el[1:] for el in all_ip_tunnels]
    logger.info(f'{result=}')
    yield result

    page.locator(
        '#page-container > div.content-layout.h-100 > div > div > div.lm_header > ul.lm_tabs > li.lm_active') \
        .click(button='middle')


@pytest.fixture
def ip_tunnel_setup(login_via_playwright):
    logger.info('ip_tunnel_setup started')
    page = login_via_playwright
    to_system_ip_tunnels(page)
    select_ne(page, IP_TUNNEL_DATA1['node1_name'])
    sleep(2)  # Mandatory timeout to refresh page
    if if_ip_tunnel_exist(page, IP_TUNNEL_DATA1):
        ip_tunnel_delete(page, IP_TUNNEL_DATA1)
        sleep(0.5)
    if if_ip_tunnel_exist(page, IP_TUNNEL_DATA2):
        ip_tunnel_delete(page, IP_TUNNEL_DATA2)
        sleep(0.5)
    return


@pytest.fixture
def ip_tunnel_teardown(login_via_playwright):
    logger.info('ip_tunnel_teardown started')
    page = login_via_playwright
    to_system_ip_tunnels(page)
    sleep(2)  # Mandatory timeout to refresh page
    if if_ip_tunnel_exist(page, IP_TUNNEL_DATA1):
        ip_tunnel_delete(page, IP_TUNNEL_DATA1)
        sleep(0.5)
    if if_ip_tunnel_exist(page, IP_TUNNEL_DATA2):
        ip_tunnel_delete(page, IP_TUNNEL_DATA2)
        sleep(0.5)
    return


@pytest.fixture
def system_tab_ne_control_setup(login_via_playwright):
    logger.info('system_tab_ne_control_setup started')
    page = login_via_playwright

    if if_ne_exists(page, node_name=TEST_NODE['node_name']):
        to_system_ne_control(page)
        select_ne(page, node_name=TEST_NODE['node_name'])
        __delete_ne(page, node_name=TEST_NODE['node_name'])
        sleep(0.5)


@pytest.fixture
def system_tab_ne_control_teardown(login_via_playwright):
    logger.info('system_tab_ne_control_teardown started')
    page = login_via_playwright
    if if_ne_exists(page, node_name=TEST_NODE['node_name']):
        to_system_ne_control(page)
        select_ne(page, node_name=TEST_NODE['node_name'])
        sleep(1)
        __delete_ne(page, node_name=TEST_NODE['node_name'])
        sleep(0.5)


# @pytest.fixture
# def tmp1(login_via_playwright):
#
#     logger.info('1')
#     page = login_via_playwright
#     to_system_ne_mngmnt(page, 'shass_157')
#     logger.info(f'{ne_config_table(page)=}')
#     sleep(2)




