import pytest
import logging
from time import time, strftime, gmtime

logger = logging.getLogger(__name__)


@pytest.mark.usefixtures('get_sw_data')
class TestLineSpeedInterface:

    @pytest.mark.parametrize(
        'mode',
        [
            ('2', '0')
        ],
        ids=['DRSet OFF -> 100G']
    )
    def test_line_speed_drset_off_100g(self, atlas_session, option_args, oos_is_adm_st, mode):
        drset_off, drset_100g = mode
        logger.info(f'Смена режимов линейного интерфейса DRSet')

        atlas_session.set_param(f'{option_args.get("dev_cls")}_{option_args.get("slot")}_ATP1Ln1DRSet', drset_off)
        logger.info(
            f'Установка параметра ATP1Ln1DRSet на устройстве в слоту {option_args.get("slot")} в состояние ВЫКЛ')
        start = time()

        atlas_session.check_response(f'{option_args.get("dev_cls")}_{option_args.get("slot")}_ATP1Ln1DRSet', drset_off)
        logger.info(f'ATP1Ln1DRSet на устройстве в слоту {option_args.get("slot")} ВЫКЛ')

        atlas_session.set_param(f'{option_args.get("dev_cls")}_{option_args.get("slot")}_ATP1Ln1DRSet', drset_100g)
        logger.info(
            f'Установка параметра ATP1Ln1DRSet на устройстве в слоту {option_args.get("slot")} в состояние 100G')
        atlas_session.check_response(f'{option_args.get("dev_cls")}_{option_args.get("slot")}_ATP1Ln1DRSet', drset_100g)
        logger.info(f'ATP1Ln1DRSet на устройстве в слоту {option_args.get("slot")} 100G')

        mod_state = atlas_session.get_param(f'{option_args.get("dev_cls")}_{option_args.get("slot")}_CFP1ModState')
        logger.info(f'Состояние модуля [ {mod_state} ]')

        assert atlas_session.check_response(f'{option_args.get("dev_cls")}_{option_args.get("slot")}_CFP1ModState',
                                            '5') is None, atlas_session.get_param(
            f'{option_args.get("dev_cls")}_{option_args.get("slot")}_CFP1ModState')

        elapsed = time() - start
        logger.info(f'Переход DRSet OFF -> 100G длился: [ {strftime("%H:%M:%S", gmtime(elapsed))} ]')

    @pytest.mark.parametrize(
        'mode',
        [
            ('0', '2')
        ],
        ids=['DRSet 100G -> OFF']
    )
    def test_line_speed_drset_100g_off(self, atlas_session, option_args, oos_is_adm_st, mode):
        drset_100g, drset_off = mode
        logger.info(f'Смена режимов линейного интерфейса DRSet')

        atlas_session.set_param(f'{option_args.get("dev_cls")}_{option_args.get("slot")}_ATP1Ln1DRSet', drset_100g)
        logger.info(
            f'Установка параметра ATP1Ln1DRSet на устройстве в слоту {option_args.get("slot")} в состояние 100G')
        start = time()

        atlas_session.check_response(f'{option_args.get("dev_cls")}_{option_args.get("slot")}_ATP1Ln1DRSet', drset_100g)
        logger.info(f'ATP1Ln1DRSet на устройстве в слоту {option_args.get("slot")} 100G')

        atlas_session.set_param(f'{option_args.get("dev_cls")}_{option_args.get("slot")}_ATP1Ln1DRSet', drset_off)
        logger.info(
            f'Установка параметра ATP1Ln1DRSet на устройстве в слоту {option_args.get("slot")} в состояние ВЫКЛ')
        atlas_session.check_response(f'{option_args.get("dev_cls")}_{option_args.get("slot")}_ATP1Ln1DRSet', drset_off)
        logger.info(f'ATP1Ln1DRSet на устройстве в слоту {option_args.get("slot")} ВЫКЛ')

        mod_state = atlas_session.get_param(f'{option_args.get("dev_cls")}_{option_args.get("slot")}_CFP1ModState')
        logger.info(f'Состояние модуля [ {mod_state} ]')

        assert atlas_session.check_response(f'{option_args.get("dev_cls")}_{option_args.get("slot")}_CFP1ModState',
                                            '5') is None, atlas_session.get_param(
            f'{option_args.get("dev_cls")}_{option_args.get("slot")}_CFP1ModState')

        elapsed = time() - start
        logger.info(f'Переход DRSet 100G -> OFF длился: [ {strftime("%H:%M:%S", gmtime(elapsed))} ]')
