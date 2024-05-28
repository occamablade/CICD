# TODO оптимизировать!!!
import logging
from enum import Enum

import pytest


logger = logging.getLogger(__name__)


class AdmStateValue(Enum):
    IS = '2'
    OOS_MT = '1'
    OOS = '0'


def wmax_value(cmax):
    if cmax == 100:
        return 50


@pytest.fixture
def status_color_fixture(atlas_session, option_args, get_5_section, request):

    if request.param == 1:
        current_color = get_5_section[1]
        logger.info('Проверка зеленого цвета')
        logger.info(f'Значение диода STATUS из секции t5: {current_color}')
        yield current_color

    if request.param == 2:
        # TODO действие, которое приведет к окраске в желтый цвет
        current_color = get_5_section[1]
        logger.info('Проверка желтого цвета')
        logger.info(f'Значение диода STATUS из секции t5: {current_color}')
        yield current_color
        # TODO отменить прошлое действие

    if request.param == 3:
        logger.info('Проверка красного цвета')
        atlas_session.tx_off_ln(dev=option_args.get('dev_cls'), slot=option_args.get('slot'), port='1')
        current_color = get_5_section[1]
        logger.info(f'Значение диода STATUS из секции t5: {current_color}')
        yield current_color
        atlas_session.tx_on_ln(dev=option_args.get('dev_cls'), slot=option_args.get('slot'), port='1')


@pytest.fixture
def line_color_fixture(atlas_session, option_args, get_5_section, request):
    ports = [str(i) for i in range(1, int(option_args.get("line_port")) + 2)]

    if request.param == 1:
        current_color_ln1, current_color_ln2 = get_5_section[2:4]
        logger.info('Проверка зеленого цвета')
        logger.info(f'Значение диодов Ln1 и Ln2 из секции t5: {current_color_ln1, current_color_ln2}')
        yield [current_color_ln1, current_color_ln2]

    if request.param == 2:
        logger.info('Проверка желтого цвета')
        for port in ports:
            pass  # TODO действие, которое окрасит линейные порты в желтый
        current_color_ln1, current_color_ln2 = get_5_section[2:4]
        logger.info(f'Значение диодов Ln1 и Ln2 из секции t5: {current_color_ln1, current_color_ln2}')
        yield [current_color_ln1, current_color_ln2]
        for port in ports:
            pass  # TODO отменить действие по окраске портов

    if request.param == 3:
        logger.info('Проверка красного цвета')
        for port in ports:
            atlas_session.tx_off_ln(dev=option_args.get('dev_cls'), slot=option_args.get('slot'), port=port)
        current_color_ln1, current_color_ln2 = get_5_section[2:4]
        logger.info(f'Значение диодов Ln1 и Ln2 из секции t5: {current_color_ln1, current_color_ln2}')
        yield [current_color_ln1, current_color_ln2]
        for port in ports:
            atlas_session.tx_on_ln(dev=option_args.get('dev_cls'), slot=option_args.get('slot'), port=port)

    if request.param == 4:
        logger.info('Проверка отсутствия цвета')
        for port in ports:
            atlas_session.maintenance_ln_port(dev=option_args.get('dev_cls'), slot=option_args.get('slot'), port=port)
        current_color_ln1, current_color_ln2 = get_5_section[2:4]
        logger.info(f'Значение диодов Ln1 и Ln2 из секции t5: {current_color_ln1, current_color_ln2}')
        yield [current_color_ln1, current_color_ln2]
        for port in ports:
            atlas_session.unlock_ln_port(dev=option_args.get('dev_cls'), slot=option_args.get('slot'), port=port)


@pytest.fixture
def client_color_fixture(atlas_session, option_args, get_5_section, request):
    ports = [str(i) for i in range(1, 9)]

    if request.param == 1:
        current_client_colors = get_5_section[4::]
        logger.info('Проверка зеленого цвета')
        logger.info(f'Значение диодов Cl1 - Cl8 из секции t5: {current_client_colors}')
        yield current_client_colors

    if request.param == 2:
        logger.info('Проверка желтого цвета')
        for port in ports:
            pass  # TODO действие, которое окрасит линейные порты в желтый
        current_client_colors = get_5_section[4::]
        logger.info(f'Значение диодов Cl1 - Cl8 из секции t5: {current_client_colors}')
        yield current_client_colors
        for port in ports:
            pass  # TODO отменить действие по окраске портов

    if request.param == 3:
        logger.info('Проверка красного цвета')
        for port in ports:
            atlas_session.tx_off_cl(dev=option_args.get('dev_cls'), slot=option_args.get('slot'), port=port)
        current_client_colors = get_5_section[4::]
        logger.info(f'Значение диодов Cl1 - Cl8 из секции t5: {current_client_colors}')
        yield current_client_colors
        for port in ports:
            atlas_session.tx_on_cl(dev=option_args.get('dev_cls'), slot=option_args.get('slot'), port=port)

    if request.param == 4:
        logger.info('Проверка отсутствия цвета')
        for port in ports:
            atlas_session.maintenance_cl_port(dev=option_args.get('dev_cls'), slot=option_args.get('slot'), port=port)
        current_client_colors = get_5_section[4::]
        logger.info(f'Значение диодов Cl1 - Cl8 из секции t5: {current_client_colors}')
        yield current_client_colors
        for port in ports:
            atlas_session.unlock_cl_port(dev=option_args.get('dev_cls'), slot=option_args.get('slot'), port=port)
