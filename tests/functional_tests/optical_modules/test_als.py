import pytest
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class ReferencePower(Enum):
    REF = -40.0


#  TODO закончить тест
@pytest.mark.usefixtures('get_sw_data')
class TestALS:

    def test_als_ln2ln(self, als_ln2ln_fixture):
        logger.info(f'Уровень выходной мощности с линии: {als_ln2ln_fixture} дБм после ALS')
        assert float(als_ln2ln_fixture) <= ReferencePower.REF.value

    def test_als_cls2ln(self, als_cls2ln_fixture):
        logger.info(f'Уровень выходной мощности с линии: {als_cls2ln_fixture} дБм после ALS')
        assert float(als_cls2ln_fixture) <= ReferencePower.REF.value
