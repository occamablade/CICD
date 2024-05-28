import logging
from enum import Enum

import pytest

logger = logging.getLogger(__name__)


class AlsValue(Enum):
    OFF = '0'
    ON = '1'
    AUTO = '2'
    MANUAL = '3'


@pytest.fixture
def get_sw_data(atlas_session, option_args):
    cfp_name = atlas_session.get_param(f'{option_args["dev_cls"]}_{option_args["slot"]}_CFP1PtNumber')
    mcu_sw = atlas_session.get_param(f'{option_args["dev_cls"]}_{option_args["slot"]}_SwNumber')
    logger.info(f'PtNumber cfp модуля - [ {cfp_name} ]')
    logger.info(f'Версия ВПО платы - [ {mcu_sw} ]')


@pytest.fixture
def als_ln2ln_fixture(atlas_session, option_args):
    ports = [str(i) for i in range(1, int(option_args.get("line_port")) + 2)]

    for port in ports:
        atlas_session.unlock_ln_port(dev=option_args.get("dev_cls"),
                                     slot=option_args.get("slot"),
                                     port=port
                                     )
    tx_power_before = atlas_session.get_param(
        f'{option_args["dev_cls"]}_{option_args["slot"]}_ATP1Ln{option_args.get("line_port")}Pout')
    logger.info(f'Уровень выходной мощности с линии {ports[0]}: {tx_power_before} дБм до ALS')
    atlas_session.check_response(
        f'{option_args.get("dev_cls")}_{option_args.get("slot")}_ATP1Ln{option_args.get("line_port")}ALSLn',
        AlsValue.AUTO.value)
    logger.info(f'ALS с линии на линию на порту Ln{ports[0]} включен в автоматическом режиме')
    atlas_session.tx_off_ln(dev=option_args.get("dev_cls"), slot=option_args.get("slot"), port=ports[1])

    tx_power_after = atlas_session.get_param(
        f'{option_args["dev_cls"]}_{option_args["slot"]}_ATP1Ln{option_args.get("line_port")}Pout')
    yield tx_power_after

    atlas_session.check_response(
        f'{option_args.get("dev_cls")}_{option_args.get("slot")}_ATP1Ln{option_args.get("line_port")}ALSLn',
        AlsValue.OFF.value)
    logger.info(f'ALS на порту Ln{ports[0]} ВЫКЛЮЧЕН')
    atlas_session.tx_on_ln(dev=option_args.get("dev_cls"), slot=option_args.get("slot"), port=ports[1])


@pytest.fixture
def als_cls2ln_fixture(atlas_session, option_args):
    atlas_session.unlock_ln_port(dev=option_args.get("dev_cls"),
                                 slot=option_args.get("slot"),
                                 port=option_args.get("line_port")
                                 )
    atlas_session.unlock_cl_port(dev=option_args.get("dev_cls"),
                                 slot=option_args.get("slot"),
                                 port='1'
                                 )
    tx_power_before = atlas_session.get_param(
        f'{option_args["dev_cls"]}_{option_args["slot"]}_ATP1Ln{option_args.get("line_port")}Pout')
    logger.info(f'Уровень выходной мощности с линии {option_args.get("line_port")}: {tx_power_before} дБм до ALS')
    atlas_session.check_response(
        f'{option_args.get("dev_cls")}_{option_args.get("slot")}_ATP1Ln{option_args.get("line_port")}ALSCl',
        AlsValue.AUTO.value)
    logger.info(f'ALS с клиентов на линии на порту Ln{option_args.get("line_port")} включен в автоматическом режиме')
    atlas_session.tx_off_cl(dev=option_args.get("dev_cls"), slot=option_args.get("slot"), port='1')

    tx_power_after = atlas_session.get_param(
        f'{option_args["dev_cls"]}_{option_args["slot"]}_ATP1Ln{option_args.get("line_port")}Pout')
    yield tx_power_after

    atlas_session.check_response(
        f'{option_args.get("dev_cls")}_{option_args.get("slot")}_ATP1Ln{option_args.get("line_port")}ALSCl',
        AlsValue.OFF.value)
    logger.info(f'ALS на порту Ln{option_args.get("line_port")} ВЫКЛЮЧЕН')
    atlas_session.tx_on_cl(dev=option_args.get("dev_cls"), slot=option_args.get("slot"), port='1')
