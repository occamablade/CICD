import logging
from time import sleep

import pytest
from deepdiff import DeepDiff


logger = logging.getLogger(__name__)


class TestRebootFroadm:

    @pytest.mark.parametrize(
        'count',
        list(range(1, 10)),
        ids=lambda r: f'Reboot number {r}'
    )
    def test_reboot_froadm(self, froadm_reboot_fixture, netconf, count):
        nmc_before, addrops_before, degr_before = froadm_reboot_fixture
        sleep(90)
        connection_nmc_after = netconf.get_state('NMC-1-2-10', 'nmc_connection')
        addrops_after = netconf.get_state('ROADMG-1-2-10', 'add_drop')
        degr_after = netconf.get_state('DEGR-1-2-10', 'degrees')
        logger.info(f'NMC, ADD-DROP, DEGREES после перезагрузки собраны')
        logger.warning(f'{connection_nmc_after}----{addrops_after}----{degr_after}')
        diff_nmc = DeepDiff(nmc_before, connection_nmc_after, verbose_level=2)
        diff_addrops = DeepDiff(addrops_before, addrops_after, verbose_level=2)
        diff_degr = DeepDiff(degr_before, degr_after, verbose_level=2)
        # logger.critical(f'**{diff_nmc}**----**{diff_addrops}**----**{diff_degr}')
        assert not any((diff_nmc, diff_addrops, diff_degr)), f'**{diff_nmc}**----**{diff_addrops}**----**{diff_degr}'
