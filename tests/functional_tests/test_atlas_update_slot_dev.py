import logging
from time import sleep

from deepdiff import DeepDiff
from Utilities.readableDiff import readable_diff

logger = logging.getLogger(__name__)


class TestUpdate:

    # @pytest.mark.parametrize('atlas_session', [CHS194], indirect=['atlas_session'])
    def test_update_slot(self, get_fw_file, backup_before_test, option_args, atlas_session):
        assert get_fw_file, 'ВПО не найдены'
        for get_fw in get_fw_file:
            atlas_session.update_slot(dc=option_args.get('dev_cls')[0], slot=option_args.get('upd_slot'),
                                      firmware=get_fw)
            sleep(10)
            atlas_session.backup(option_args.get('backup_slot'), *option_args.get('dev_cls'))
            logger.info('Backup после теста создан')
            backup_after_test = atlas_session.get_param_backup_data(option_args.get('backup_slot'),
                                                                    *option_args.get('dev_cls'))
            logger.info(f'Backup после теста сохранён {backup_after_test}')
            diff = DeepDiff(backup_before_test, backup_after_test, verbose_level=2)
            assert not diff, (f'После обновления параметры не совпадают: [ {diff.pretty()} '
                              f'\n{readable_diff(diff.pretty(), backup_after_test)} ]')
