import logging
from Utilities.all import (
    IP_TUNNEL_DATA1, IP_TUNNEL_DATA2
)

logger = logging.getLogger(__name__)


class TestSystemTabIpTunnels:
    def test_ip_tunnel_setup(self, ip_tunnel_setup):
        pass

    def test_ip_tunnel_create_t1176(self, ip_tunnel_create_1176):
        tunnel_data = list(IP_TUNNEL_DATA1.values())
        assert tunnel_data in ip_tunnel_create_1176, "IP Tunnel not in list "
        logger.warning('Тест-кейс Т1176 completed')

    def test_ip_tunnel_edit_t1177(self, ip_tunnel_edit_1177):
        tunnel_data = list(IP_TUNNEL_DATA2.values())
        assert tunnel_data in ip_tunnel_edit_1177, "IP Tunnel not in list "
        logger.warning('Тест-кейс Т1177 completed')

    def test_ip_tunnel_delete_t1178(self, ip_tunnel_delete_1178):
        tunnel_data = list(IP_TUNNEL_DATA2.values())
        assert tunnel_data not in ip_tunnel_delete_1178, "IP Tunnel wasn't deleted "
        logger.warning('Тест-кейс Т1178 completed')

    def test_ip_tunnel_teardown(self, ip_tunnel_teardown):
        pass

    # def test_tmp(self, tmp):
    #     pass
