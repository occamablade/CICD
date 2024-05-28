import logging
from time import sleep

from deepdiff import DeepDiff

from Utilities.all import REBOOT_VAL, WAIT_REBOOT

logger = logging.getLogger(__name__)


class TestReboot:

    def test_reboot_slot(self, atlas_session, backup_before_test, option_args):

        for i in range(int(option_args.get('cnt'))):
            logger.info(f'Перезагрузка слотового устройства № {i + 1}')
            atlas_session.set_param(*option_args.get('reboot_slot'), REBOOT_VAL)
            sleep(WAIT_REBOOT)

        atlas_session.backup(option_args.get('backup_slot'), option_args.get('dev_cls'))
        logger.info('Backup после теста создан')
        backup_after_test = atlas_session.get_param_backup_data(option_args.get('backup_slot'),
                                                                option_args.get('dev_cls'))
        logger.info(f'Backup после теста сохранён {backup_after_test}')
        diff = DeepDiff(backup_before_test, backup_after_test, verbose_level=2)

        assert not diff, (f'После перезагрузки слотового устройства параметры не совпадают: '
                          f'\n[ {diff.pretty()}  ]')
