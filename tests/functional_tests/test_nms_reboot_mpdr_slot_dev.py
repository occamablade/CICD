import logging
from time import sleep

import pytest
from deepdiff import DeepDiff

from Utilities.instance import is_instance

logger = logging.getLogger(__name__)


class TestRebootSlot:

    @pytest.mark.parametrize(
        'name',
        [
            f'Test_backup_{i}' for i in range(1, 81)
        ]
    )
    def test_reboot_slot(
            self,
            slot_reboot_via_rest,
            reboot_data,
            backup_nms,
            name,
            option_args,
            get_oper_st_for_odu_conn_before_test,
            netconf
    ):
        ref_bp = backup_nms[0]
        op_st = get_oper_st_for_odu_conn_before_test
        sleep(5)

        ans = slot_reboot_via_rest.execute_rpc(reboot_data)
        logger.warning(f'Перезагрузка слота [ {ans} ]')
        sleep(150)

        backup_nms[1].create_backup(node_id=''.join(option_args.get('node_id')), backup_name=name)
        sleep(3)

        bp = backup_nms[1].get_backup(node_id=''.join(option_args.get('node_id')), backup_name=name)

        after_op_st = netconf.get_state('ODU-1-1-{}'.format(option_args['slot']), 'odu_conn_op_st')
        after_op_st_list = is_instance(after_op_st)

        diff = DeepDiff(ref_bp, bp, verbose_level=2)
        assert not diff, (f'После перезагрузки слотового устройства параметры не совпадают: '
                          f'\n[ {diff.pretty()} ]')
        assert op_st == after_op_st_list, 'Операционное состояние odu-connections не совпадает'
