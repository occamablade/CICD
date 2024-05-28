import logging
from time import sleep

import pytest
import numpy as np

from Utilities.commWrap import freq_str_create

logger = logging.getLogger(__name__)


@pytest.mark.usefixtures('get_sw_data')
class TestWavelength:

    @pytest.mark.parametrize(
        'ch',
        [
            str(round(c, 2)) for c in np.arange(13, 61.5, 0.5)
        ],
        ids=lambda c: f'Channel {c}'
    )
    def test_wavelength_(self, atlas_session, ch, option_args):
        logger.info(f'Установка номера канала [ {ch} ]')
        atlas_session.set_param(f'{option_args["dev_cls"]}_{option_args["slot"]}_ATP1Ln1SetTxITU', ch)
        sleep(15)
        logger.info(f'Ожидаемая частота [ {freq_str_create(ch)} ГГц ]')
        assert atlas_session.check_response(f'{option_args["dev_cls"]}_{option_args["slot"]}_ATP1Ln1Frq',
                                            freq_str_create(ch)) is None
