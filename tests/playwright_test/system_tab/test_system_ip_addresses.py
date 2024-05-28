import logging

import pytest

from Utilities.all import PING_DATA, TRACEROUTE_DATA, NODE_NAME1, TEST_NODE

logger = logging.getLogger(__name__)


class TestSystemTabIpAddresses:

    def test_transition_to_object_t1174(self, transition_to_object_fixture_t1174):
        assert transition_to_object_fixture_t1174 == f'Management {NODE_NAME1}', \
            'Тест-кейс Т1174 прошёл с ошибкой, Incorrect window name'
        logger.warning('Тест-кейс Т1174 completed')

    def test_traceroute_ne_t1173(self, traceroute_ne_t1173):
        assert TRACEROUTE_DATA['target_ip'] in traceroute_ne_t1173, "Тест-кейс Т1173 прошёл с ошибкой, TraceRoute isn't successful"
        logger.warning('Тест-кейс Т1173 completed')


    def test_ping_ne_t1172(self, ping_ne_t1172):
        control_text = '3 packets transmitted, 3 received, 0% packet loss'
        assert control_text in ping_ne_t1172, "Тест-кейс Т1172 прошёл с ошибкой, Ping isn't successful"
        logger.warning('Тест-кейс Т1172 completed')
