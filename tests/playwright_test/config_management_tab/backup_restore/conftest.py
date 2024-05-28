import logging
import os
import shutil

import requests

import pytest
from time import perf_counter, sleep
from datetime import datetime, timedelta
import pytz
from playwright.sync_api import sync_playwright

from Utilities.all import (
    URL_LOGIN_NMS,
    TEST_PASSWD_NMS,
    TEST_LOGIN_NMS,
    NODE_NAME1,
)
from tests.conftest import to_backup_restore, table1_id, table2_id, to_archive_log, notice_message_blue, \
    notice_message_green, wait_while_table_updated, ne_config_table, to_system_ne_mngmnt, \
    login_via_playwright, backup_manual_download_from_ne_to_nms, \
    backup_download_from_nms_to_file, backup_nms_delete, backup_autosave_from_ne_to_nms, \
    backup_file_upload_to_NMS_archive, backup_upload_from_nms_to_ne, table_data_text, modify_ne_board_state, \
    table_data_web

logger = logging.getLogger(__name__)
FILE_BACKUP_NAME1 = ''
FILE_BACKUP_NAME2 = ''



@pytest.fixture()
def setup_backup_restore(login_via_playwright):
    global FILE_BACKUP_NAME1, FILE_BACKUP_NAME2
    logger.info('Setup started')
    page = login_via_playwright
    current_path = os.getcwd()
    backup_folder = os.path.join(current_path, 'backup_folder')
    if not os.path.exists(backup_folder):
        os.mkdir(backup_folder)
    logger.info(f'Backup folder {backup_folder} created')

    backup_manual_download_from_ne_to_nms(page, node_name=NODE_NAME1,
                                               backup_name=f'{NODE_NAME1}_backup_test1')
    logger.info(f'Backup_record "{NODE_NAME1}_backup_test1" created')
    sleep(1)
    backup_manual_download_from_ne_to_nms(page, node_name=NODE_NAME1,
                                               backup_name=f'{NODE_NAME1}_backup_test2')
    logger.info(f'Backup_record "{NODE_NAME1}_backup_test2" created')
    sleep(1)
    backup_file1_fullname1 = str(
        backup_download_from_nms_to_file(page, node_name=NODE_NAME1, backup_name=f'{NODE_NAME1}_backup_test1'))
    sleep(1)
    backup_file2_fullname1 = str(
        backup_download_from_nms_to_file(page, node_name=NODE_NAME1, backup_name=f'{NODE_NAME1}_backup_test2'))
    sleep(1)
    backup_file1_fullname2 = os.path.join(backup_folder, 'backup_file1')
    backup_file2_fullname2 = os.path.join(backup_folder, 'backup_file2')
    os.rename(backup_file1_fullname1, backup_file1_fullname2)
    logger.info(f'Backup_file1 moved to  "{backup_file1_fullname2}" ')
    os.rename(backup_file2_fullname1, backup_file2_fullname2)
    logger.info(f'Backup_file1 moved to  "{backup_file2_fullname2}" ')
    FILE_BACKUP_NAME1 = backup_file1_fullname2
    FILE_BACKUP_NAME2 = backup_file2_fullname2
    logger.info(f'NOW TEST RUNS ')

    to_archive_log(page)

    logger.info('Cleaning old archives')
    backup_info = table_data_text(page)
    backup_names = []
    for el in backup_info:
        if el[1] == NODE_NAME1:
            backup_names.append(el[3])
    archives_to_check = [f'{NODE_NAME1}_backup_test1',
                         f'{NODE_NAME1}_backup_test2',
                         'backup_file1 test_upload_file',
                         'backup_file2 test_upload_file',
                         '1234567_test',]

    for arch_name in archives_to_check:
        if arch_name in backup_names:
            backup_nms_delete(page=page, node_name=NODE_NAME1, nms_archive_name=arch_name)

    logger.info(f'NOW TEST RUNS ')

@pytest.fixture()
def teardown_backup_restore(login_via_playwright):
    logger.info('Teardown started')

    names_to_check = [f'{NODE_NAME1}_backup_test1',
                         f'{NODE_NAME1}_backup_test2',
                         'backup_file1 test_upload_file',
                         'backup_file2 test_upload_file',
                         '1234567_test',]

    current_path = os.getcwd()
    backup_folder = os.path.join(current_path, 'backup_folder')
    page = login_via_playwright
    to_archive_log(page)

    logger.info('Cleaning created archives ')
    backup_info = table_data_web(page)
    for el in backup_info:
        el_str = el.all_inner_texts()[0].split("\t")
        if el_str == ['']:
            break
        if el_str[1] == f"{NODE_NAME1}" and el_str[3] in names_to_check:
            el.get_by_role("cell", name=f"{NODE_NAME1}", exact=True).click(button="right")
            page.get_by_role("link", name="Delete archive").click()
            page.get_by_role("button", name="Delete").click()
            logger.info(f'Backup_record "{el_str[3]}" deleted')
            sleep(0.5)

    if os.path.exists(backup_folder):
        shutil.rmtree(backup_folder)
        logger.info(f'Backup_folder "{backup_folder}" deleted')


# ---------------------------- TEST FIXTURES STARTS HERE -----------------
@pytest.fixture
def config_autobackup_t156(login_via_playwright):
    logger.info('TC_156 config_autobackup_t156 started')
    page = login_via_playwright

    backup_autosave_from_ne_to_nms(page=page,
                                    node_name=NODE_NAME1,
                                    enabled=True,
                                    num_days='1', num_backups="+1")

    backup_table = table_data_text(page)
    result = ''
    for el in backup_table:
        if el[2] == NODE_NAME1:
            result = el[10]
    logger.info(f'Test_T156 result: {result}')
    yield result   # '29.03.2024, 16:42:08.309'

@pytest.fixture
def autobackup_2days_t157(login_via_playwright):
    # testcase T157    https://jira.t8.ru/secure/Tests.jspa#/design?projectId=10102
    logger.info('TC-157 autobackup_2days_t157 started')
    page = login_via_playwright
    to_backup_restore(page)
    sleep(1)
    backup_autosave_from_ne_to_nms(page=page,
                                    node_name=NODE_NAME1,
                                    enabled=True,
                                    num_days='2',
                                    num_backups="")

    sleep(3)
    backup_table = table_data_text(page)

    result = ""
    for el in backup_table:
        if el[2] == NODE_NAME1:
            result = el[7]
    logger.info(f'Test_T157 result: {result}')
    yield result


@pytest.fixture
def autobackup_max_backups_t158(login_via_playwright):
    # testcase T158    https://jira.t8.ru/secure/Tests.jspa#/design?projectId=10102
    # https://jira.t8.ru/secure/Tests.jspa#/testCase/MP-T158
    logger.info('TC-158 autobackup_max_backups_t158 started')
    page = login_via_playwright
    to_archive_log(page)
    sleep(1)

    backup_table = table_data_text(page)

    list_of_existing_backups = []   # list of existing backups
    for el in backup_table:  # get last backup time
        if el[1] == NODE_NAME1 and "autobackup" in el[3]:
            list_of_existing_backups.append(el)
    backup_names_existing = [el[3] for el in list_of_existing_backups]
    backup_names_existing.sort()
    num_of_backups = len(list_of_existing_backups) if list_of_existing_backups else 1

    backup_autosave_from_ne_to_nms(page=page,
                                    node_name=NODE_NAME1,
                                    enabled=True,
                                    num_days='1', num_backups=f"{num_of_backups}")

    to_archive_log(page)
    backup_table = table_data_text(page)
    list_of_new_backups = []  # list of new backups
    for el in backup_table:
        if el[1] == NODE_NAME1 and "autobackup" in el[3]:
            list_of_new_backups.append(el)
    backup_names_new = [el[3] for el in list_of_new_backups]
    backup_names_new.sort()
    logger.info(f'Test_T158 result: {backup_names_existing=}')
    logger.info(f'Test_T158 result: {backup_names_new=}')
    yield backup_names_existing, backup_names_new


@pytest.fixture
def archive_file_download_t147(login_via_playwright):
    # testcase T147    https://jira.t8.ru/secure/Tests.jspa#/design?projectId=10102
    # https://jira.t8.ru/secure/Tests.jspa#/testCase/MP-T147
    logger.info('TC-147 archive_file_download_t147 started')
    page = login_via_playwright
    to_archive_log(page)
    sleep(1)

    backup_table = table_data_text(page)

    list_of_existing_backups = []  # list of existing backups
    for el in backup_table:  # get last backup time
        if el[1] == NODE_NAME1 and "autobackup" in el[3]:
            list_of_existing_backups.append(el)
    backup_names_existing = [el[3] for el in list_of_existing_backups]
    backup_names_existing.sort()

    latest_backup_name = f"{backup_names_existing[-1]}"  # latest backup name 'autobackup-2024-04-01T14:37'
    logger.info(f'{latest_backup_name=}')
    file_path = backup_download_from_nms_to_file(page,
                                                 node_name=NODE_NAME1, backup_name=latest_backup_name)
    logger.info(f'Test_T157 result: {file_path=}')
    yield file_path


@pytest.fixture
def archive_file_upload_t148(login_via_playwright):
    # testcase T148    https://jira.t8.ru/secure/Tests.jspa#/design?projectId=10102
    # https://jira.t8.ru/secure/Tests.jspa#/testCase/MP-T148
    logger.info('TC-148 archive_file_upload_t148 started')
    page = login_via_playwright
    to_backup_restore(page)

    backup_file_upload_to_NMS_archive(page,
                                      node_name=NODE_NAME1,
                                      backup_comment='test_upload_file',
                                      file_backup_name=FILE_BACKUP_NAME1)

    all_backups_table = table_data_text(page)
    logger.info(f'Test_T148 result: {all_backups_table=}')
    return all_backups_table


# #########################################################################
@pytest.fixture
def ne_config_recovery_t149(login_via_playwright):
    # testcase T149    https://jira.t8.ru/secure/Tests.jspa#/design?projectId=10102
    # https://jira.t8.ru/secure/Tests.jspa#/testCase/MP-T149
    logger.info('TC-149  ne_config_recovery_t149 started')
    page = login_via_playwright
    node_name = NODE_NAME1
    slot_name = 'SLOT FU '
    backup_manual_download_from_ne_to_nms(page, node_name=node_name, backup_name='1234567_test')
    to_system_ne_mngmnt(page, node_name)
    sleep(1)
    ne_config_before = ne_config_table(page)
    ne_config = ne_config_table(page)
    slot_status_now = ""
    for key, value in ne_config.items():
        if value['el_name'] == slot_name and 'text-grey' in value['status2']:
            slot_status_now = 'maintainance'
            break
        elif value['el_name'] == slot_name and 'text-green' in value['status2']:
            slot_status_now = 'unlock'
            break
    if slot_status_now == "":
        logger.info(f'Slot named "{slot_name}" not found in node "{node_name}"')
        return -1
    logger.info(f'Status of "SLOT FU " is "{slot_status_now}"')
    if slot_status_now == 'maintainance':
        modify_ne_board_state(page, action="Unlock", device_name="SLOT FU ")
    if slot_status_now == 'unlock':
        modify_ne_board_state(page, action="Maintenance", device_name="SLOT FU ")
    sleep(1)
    backup_upload_from_nms_to_ne(page, node_name=node_name, backup_name='1234567_test')
    sleep(1)
    notice_message_blue(page)
    notice_message_green(page)
    to_system_ne_mngmnt(page, node_name)
    sleep(1)
    ne_config_after = ne_config_table(page)
    sleep(1)
    logger.info(f'Test_T149 result: {ne_config_before=}')
    logger.info(f'Test_T149 result: {ne_config_after=}')
    yield ne_config_before, ne_config_after


@pytest.fixture
def backup_delete_t150(login_via_playwright):
    # testcase T150    https://jira.t8.ru/secure/Tests.jspa#/design?projectId=10102
    # https://jira.t8.ru/secure/Tests.jspa#/testCase/MP-T150
    logger.info('TC-150 backup_delete_t150 started')
    page = login_via_playwright
    sleep(1)

    backup_manual_download_from_ne_to_nms(page, node_name=NODE_NAME1, backup_name='1234567_test')

    to_archive_log(page)
    sleep(1)

    all_backups_data = table_data_text(page)  # ['\tshass_157\t03.04.2024, 16:13:49.909\t1234567_test\tM', ... ]
    all_backups_data1 =[]
    for el in all_backups_data:
        if NODE_NAME1 in el and '1234567_test' in el:
            all_backups_data1.append(el)

    backup_nms_delete(page, node_name=NODE_NAME1, nms_archive_name='1234567_test')

    sleep(1)

    all_backups_data = table_data_text(page)
    sleep(0.5)
    all_backups_data2 =[]
    for el in all_backups_data:
        if NODE_NAME1 in el and '1234567_test' in el:
            all_backups_data2.append(el)
    sleep(1)
    logger.info(f'Test_T150 result: {all_backups_data1=}')
    logger.info(f'Test_T150 result: {all_backups_data2=}')
    yield all_backups_data1, all_backups_data2


@pytest.fixture
def invalid_backup_filetype_t151(login_via_playwright):
    # testcase T151    https://jira.t8.ru/secure/Tests.jspa#/design?projectId=10102
    # https://jira.t8.ru/secure/Tests.jspa#/testCase/MP-T151
    logger.info('TC-151 invalid_backup_filetype_t151 started')
    current_path = os.getcwd()
    img_filename = os.path.join(current_path, 'backup_folder','test_image_1.png')
    img_data = requests.get('http://placehold.it/120x120&text=image1').content
    with open(img_filename, 'wb') as handler:
        handler.write(img_data)

    page = login_via_playwright

    backup_file_upload_to_NMS_archive(page=page,
                                      node_name=NODE_NAME1,
                                      backup_comment="test_upload_file",
                                      file_backup_name=img_filename)

    backup_table = table_data_text(page)
    list_of_ne_backups = []
    for el in backup_table:  # get last of backup time
        if el[1] == NODE_NAME1:
            list_of_ne_backups.append(el[3])
    logger.info(f'Test_T151 result: {list_of_ne_backups=}')
    yield list_of_ne_backups


@pytest.fixture
def archive_upload_few_t152(login_via_playwright):
    # testcase T152   https://jira.t8.ru/secure/Tests.jspa#/design?projectId=10102
    # https://jira.t8.ru/secure/Tests.jspa#/testCase/MP-T152

    logger.info('TC-152 archive_upload_few_t152 started')
    page = login_via_playwright

    backup_file_upload_to_NMS_archive(page=page,
                                      node_name=NODE_NAME1,
                                      backup_comment="test_upload_file",
                                      file_backup_name=[f"{FILE_BACKUP_NAME1}", f"{FILE_BACKUP_NAME2}"]
                                      )
    sleep(1)

    table_data3 = table_data_text(page)
    backup_time = []
    for el in table_data3:
        if el[1] == NODE_NAME1:
            backup_time.append(el[2][:20])
    logger.info(f'Test_T151 result: {backup_time=}')
    yield backup_time


@pytest.fixture
def archive_upload_same_name_t154(login_via_playwright):
    # testcase T154   https://jira.t8.ru/secure/Tests.jspa#/design?projectId=10102
    # https://jira.t8.ru/secure/Tests.jspa#/testCase/MP-T154

    logger.info('TC-154 archive_upload_same_name_t154 started')
    page = login_via_playwright
    to_archive_log(page)
    sleep(1)
    backup_table = table_data_text(page)

    backup_file_short_name = FILE_BACKUP_NAME1.split('/')[-1]
    list_of_existing_backups = []  # list of existing backups
    for el in backup_table:  # get last backup time
        if el[1] == NODE_NAME1 and el[3] == f'{backup_file_short_name} test_upload_file':
            list_of_existing_backups.append(el)
    backup_names_existing = [el[3] for el in list_of_existing_backups]
    if f'{backup_file_short_name} test_upload_file' not in backup_names_existing:
        logger.info(f'Prerequisites not fulfilled, backup record with name "{FILE_BACKUP_NAME1} test_upload_file" not found')
        return

    backup_file_upload_to_NMS_archive(page,
                                      node_name=NODE_NAME1,
                                      backup_comment='test_upload_file',
                                      file_backup_name=FILE_BACKUP_NAME1)
    sleep(2)

    backup_table = table_data_text(page)
    list_of_ne_backups = []
    for el in backup_table:  # get last backup time
        if el[1] == NODE_NAME1 and el[3] == f'{backup_file_short_name} test_upload_file':
            list_of_ne_backups.append(el)
    new_record = sorted(list_of_ne_backups, key=lambda elem: elem[2])[-1]
    logger.info(f'Test_T154 result: {new_record=}')
    return new_record

