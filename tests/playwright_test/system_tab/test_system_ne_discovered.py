import logging

import pytest

logger = logging.getLogger(__name__)


class TestSystemTabNeDiscovered:

    @pytest.mark.skip
    def test_accept_discovered_ne_t1169(self, ne_discovered_accept_fixture):
        assert ne_discovered_accept_fixture, 'Тест-кейс Т1169 прошёл с ошибкой. [ Accept NE ] не найдено'
        logger.warning('Тест-кейс Т1169 прошёл успешно')

    @pytest.mark.skip
    def test_remove_discovered_ne_t1170(self, ne_discovered_remove_fixture):
        assert ne_discovered_remove_fixture, 'Тест-кейс Т1170 прошёл с ошибкой. [ Remove NE ] не найдено'
        logger.warning('Тест-кейс Т1170 прошёл успешно')
