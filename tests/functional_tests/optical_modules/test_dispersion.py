import logging

import pytest

logger = logging.getLogger(__name__)


@pytest.mark.usefixtures('get_sw_data')
class TestDispersion:

    @pytest.mark.parametrize(
        'disp',
        [
            str(d) for d in range(0, 100000, 20000)
        ],
        ids=lambda d: f'Dispersion {d}'
    )
    def test_low_dispersion_set(self, atlas_session, disp, option_args):
        logger.info(f'Установка значения нижнего порога поиска хроматической дисперсии [ {disp} пс/нм ]')
        atlas_session.set_param(f'{option_args["dev_cls"]}_{option_args["slot"]}_ATP1Ln1DispLowSet', disp)
        assert atlas_session.check_response(f'{option_args["dev_cls"]}_{option_args["slot"]}_ATP1Ln1DispLowSet',
                                            disp) is None

    @pytest.mark.parametrize(
        'disp',
        [
            str(d) for d in range(-80000, 0, 20000)
        ],
        ids=lambda d: f'Dispersion {d}'
    )
    def test_high_dispersion_set(self, atlas_session, disp, option_args):
        logger.info(f'Установка значения верхнего порога поиска хроматической дисперсии [ {disp} пс/нм ]')
        atlas_session.set_param(f'{option_args["dev_cls"]}_{option_args["slot"]}_ATP1Ln1DispHighSet', disp)
        assert atlas_session.check_response(f'{option_args["dev_cls"]}_{option_args["slot"]}_ATP1Ln1DispHighSet',
                                            disp) is None
