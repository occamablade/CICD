import logging
from time import sleep

import pytest


logger = logging.getLogger(__name__)


class TestDelConfig:

    def test_restore_default_settings(self, atlas_session, option_args):
        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_SetDefaultSettings', '0')
        sleep(3)

    @pytest.mark.parametrize('index, val', [(i, v) for i, v in enumerate(range(1, 11))])
    def test_clear_mux1(self, atlas_session, index, val, option_args):
        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux1OPUTpSelect', f'{val}')
        assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux1OPUTpSelect', f'{val}') is None
        logger.info(f'Выбран трибутарный порт OPU [ OPUkTp{val} ]')

        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux1OPUTpDel', '1')
        sleep(5)
        assert atlas_session.get_param(f'mjc2_{option_args.get("slot")}_ATPMux1OPUkState').split()[index] == 'XXXXXXXX'
        logger.info(f'Порт OPU [ OPUkTp{val} ] удалён из матрицы MUX1')

    @pytest.mark.parametrize('index, val', [(i, v) for i, v in enumerate(range(1, 11))])
    def test_clear_mux2(self, atlas_session, index, val, option_args):
        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux2OPUTpSelect', f'{val}')
        assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux2OPUTpSelect', f'{val}') is None
        logger.info(f'Выбран трибутарный порт OPU [ OPUkTp{val} ]')

        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux2OPUTpDel', '1')
        sleep(5)
        assert atlas_session.get_param(f'mjc2_{option_args.get("slot")}_ATPMux2OPUkState').split()[index] == 'XXXXXXXX'
        logger.info(f'Порт OPU [ OPUkTp{val} ] удалён из матрицы MUX2')
