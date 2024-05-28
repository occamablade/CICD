import logging
import os
from datetime import datetime, timedelta

import pytest

logger = logging.getLogger(__name__)

current_path = os.getcwd()
backup_folder = os.path.join(current_path, 'backup_folder')
FILE_BACKUP_NAME1 = os.path.join(backup_folder, 'backup_file1')
FILE_BACKUP_NAME2 = os.path.join(backup_folder, 'backup_file1')


class TestSystemConfigMngmntBackupRestore:

    def test_setup(self, setup_backup_restore):
        pass

    def test_autobackup_t156(self, config_autobackup_t156):
        if config_autobackup_t156:
            backup_time = datetime.strptime(config_autobackup_t156[:20], '%d.%m.%Y, %H:%M:%S')
            logger.info(f'Backup_time: {backup_time.strftime("%m.%d.%Y, %H:%M:%S")}')
            assert (backup_time - datetime.now() <
                    timedelta(minutes=1, seconds=30)), 'test  config_autobackup_t156 not passed'
            logger.info(f'Test test_autobackup_t156 passed')
        else:
            logger.info(f'No backup record found for test_autobackup_t156')
            logger.info(f'Test test_autobackup_t156 failed')

    def test_autobackup_2days_t157(self, autobackup_2days_t157):
        assert autobackup_2days_t157 == '2', "Test autobackup__2days_t157 Not Passed"
        logger.info(f'Test autobackup__2days_t157 completed')

    def test_autobackup_max_backups_t158(self, autobackup_max_backups_t158):
        backup_names_existing, backup_names_new = autobackup_max_backups_t158
        assert backup_names_existing[0] not in backup_names_new, 'TC 158 Not Passed : oldest backup hasn"t been deleted'
        backup_time_string = f'{backup_names_new[-1][11:21]} {backup_names_new[-1][22:31]}'
        backup_time = datetime.strptime(backup_time_string, '%Y-%m-%d %H:%M:%S')
        logger.info(f'backup_time: {backup_time.strftime("%d.%m.%Y, %H:%M:%S")}')
        assert (backup_time - datetime.now() <
                timedelta(minutes=1, seconds=30)), 'test  config_autobackup_t158 not passed'
        logger.info(f'Test test_autobackup_t158 passed')

    def test_archive_file_download_t147(self, archive_file_download_t147):
        file_path = f'{archive_file_download_t147}'
        assert os.path.exists(file_path) == True, 'test archive_download_t147 not passed'
        if file_path:
            os.remove(file_path)
        logger.info(f'Test test_archive_download_t147 passed')

    def test_archive_file_upload_t148(self, archive_file_upload_t148):
        backup_name = f'{FILE_BACKUP_NAME1.split("/")[-1]} test_upload_file'
        all_backup_names = [el[3] for el in archive_file_upload_t148]
        assert backup_name in all_backup_names , 'Test archive_upload_t148 not passed'
        logger.info(f'Test archive_upload_t148 passed')

    def test_ne_config_recovery_t149(self, ne_config_recovery_t149):
        ne_config_before, ne_config_after = ne_config_recovery_t149
        assert ne_config_before == ne_config_after, 'Test config_recovery_t149 FAILED'
        logger.info(f'Test_config_recovery_t149 passed')

    def test_backup_delete_t150(self, backup_delete_t150):
        all_backups_data1, all_backups_data2 = backup_delete_t150
        logger.info(f'{all_backups_data1=}')
        logger.info(f'{all_backups_data2=}')
        test1 = any("1234567_test" in string for string in all_backups_data1)
        assert test1 == True, "Backup named '12345567_test' wasn't in list before delete"
        test2 = any("1234567_test" in string for string in all_backups_data2)
        assert test2 == False, "Backup named '12345567_test' hasn't been deleted"
        logger.info(f'Test_config_delete_t150 passed')

    def test_invalid_backup_file_type_t151(self, invalid_backup_filetype_t151):
        assert all("test_image_1.png" not in string for string in invalid_backup_filetype_t151)
        logger.info(f'Test_invalid_backup_t151 passed')

    def test_archive_upload_few_t152(self, archive_upload_few_t152):
        backup_times = archive_upload_few_t152
        backup_times.sort()
        backup_time1 = datetime.strptime(backup_times[-1], '%d.%m.%Y, %H:%M:%S')
        backup_time2 = datetime.strptime(backup_times[-2], '%d.%m.%Y, %H:%M:%S')
        assert (backup_time1 - datetime.now() <
                timedelta(seconds=30)), 'test1  test_archive_upload_few_t152 FAILED '
        assert (backup_time2 - datetime.now() <
                timedelta(seconds=30)), 'test2  test_archive_upload_few_t152 FAILED '
        logger.info(f'Test_archive_upload_few_t152 PASSED')

    def test_archive_upload_same_name_t154(self, archive_upload_same_name_t154):
        backup_time1 = (
            datetime.strptime(archive_upload_same_name_t154[2][:20],
                              '%d.%m.%Y, %H:%M:%S'))

        assert (backup_time1 - datetime.now() <
                timedelta(seconds=30)), 'test1  test_archive_upload_few_t152 FAILED '

    def test_teardown(self, teardown_backup_restore):
        pass

    # def test_tmp(self, tmp1):
    #     pass


