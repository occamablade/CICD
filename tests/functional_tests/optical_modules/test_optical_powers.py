import pytest
import logging

logger = logging.getLogger(__name__)


@pytest.mark.usefixtures('get_sw_data')
class TestOutOpticalPower:

    @pytest.mark.parametrize(
        'power',
        [
            str(p) for p in range(-15, 4)
        ],
        ids=lambda p: f'Power {p}'
    )
    def test_output_optical_power(self, atlas_session, power, option_args):
        logger.info(f'Установка значения вых. мощности [ {power} дБм ]')
        atlas_session.set_param(f'{option_args["dev_cls"]}_{option_args["slot"]}_ATP1Ln1SetTxPwr', power)
        assert atlas_session.check_response(f'{option_args["dev_cls"]}_{option_args["slot"]}_ATP1Ln1Pout',
                                            str(float(power))) is None
