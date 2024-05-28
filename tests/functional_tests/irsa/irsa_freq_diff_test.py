import logging

import pytest

from Utilities.all import CHS192, FREQ_GET, FREQ_SET

logger = logging.getLogger(__name__)


@pytest.mark.usefixtures('create_csv_file')
class TestFreq:

    # @pytest.mark.parametrize('atlas_session', [CHS192], indirect=['atlas_session'])
    @pytest.mark.parametrize('freq',
                             [(FREQ_GET, FREQ_SET, str(round(191300.0 + n * 6.25, 3))) for
                              n in range(768)], indirect=['freq'])
    def test_freq(self, freq, atlas_session, csv_writer):
        logger.info(f'Вывод {freq}')
        try:
            assert freq[-1] == 0.0
        except AssertionError as err:
            logger.exception(f'FAIL {err}')
            freq.append('FAIL')
            csv_writer.writerows([freq])
        else:
            logger.info('PASS')
            freq.append('PASS')
            csv_writer.writerows([freq])
