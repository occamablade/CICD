import logging
from time import sleep

import pytest
from numpy import arange

from Utilities.all import (
    LINE_PORT,
    LINE_OPT,
    LINE_ODU,
    LINE_OTU,
    # PPM
)

logger = logging.getLogger(__name__)


class TestAdmStConfig:

    # @pytest.mark.parametrize(
    #     'info',
    #     [
    #         [PPM, 'model'],
    #         [PPM, 'vendor'],
    #         [PPM, 'rev'],
    #         [PPM, 'serial']
    #     ],
    #     indirect=['info']
    # )
    # def module_info(self, info):
    #     logger.info('Информация по тестируемому модулю')

    @pytest.mark.parametrize(
        'unlock_after_test',
        [
            LINE_PORT
        ],
        indirect=['unlock_after_test']
    )
    def test_adm_st(self, netconf, xml_data, unlock_after_test, option_args):

        state_before = netconf.get_state(LINE_PORT.format(option_args['slot']), 'adm_state')
        lock = 'locked'
        logger.warning(
            f'Административное состояние линейной оптики ДО изменения [ {state_before["administrative-state"]} ]')

        netconf.edit_conf_and_commit(xml_data.change_adm_st(lock, LINE_PORT.format(option_args['slot'])))
        sleep(5)

        state_after = netconf.get_state(LINE_PORT.format(option_args['slot']), 'adm_state')
        logger.warning(
            f'Административное состояние линейной оптики ПОСЛЕ изменения [ {state_after["administrative-state"]} ]')

        assert netconf.get_state(LINE_PORT.format(option_args['slot']), 'adm_state')['administrative-state'] == lock
        assert netconf.get_state(LINE_ODU.format(option_args['slot']), 'adm_state')['administrative-state'] == lock
        assert netconf.get_state(LINE_OPT.format(option_args['slot']), 'adm_state')['administrative-state'] == lock
        assert netconf.get_state(LINE_OTU.format(option_args['slot']), 'adm_state')['administrative-state'] == lock

    @pytest.mark.parametrize(
        'intfc, unlock_after_test',
        [
            [LINE_ODU] * 2,
            [LINE_OPT] * 2,
            [LINE_OTU] * 2
        ],
        ids=lambda i: f' Testable interface [ {i} ] ',
        indirect=['unlock_after_test']
    )
    def test_port_config(self, netconf, xml_data, intfc, unlock_after_test, option_args):

        state_before = netconf.get_state(intfc.format(option_args['slot']), 'adm_state')
        lock = 'locked'
        logger.warning(
            f'Административное состояние интерфейса [ {intfc.format(option_args["slot"])} ] ДО изменения [ {state_before["administrative-state"]} ]')

        netconf.edit_conf_and_commit(xml_data.change_adm_st_interface(lock, intfc.format(option_args['slot'])))

        state_after = netconf.get_state(intfc.format(option_args['slot']), 'adm_state')
        logger.warning(
            f'Административное состояние интерфейса [ {intfc.format(option_args["slot"])} ] ПОСЛЕ изменения [ {state_after["administrative-state"]} ]')

        if intfc == LINE_ODU.format(option_args['slot']):
            assert netconf.get_state(LINE_ODU.format(option_args['slot']), 'adm_state')['administrative-state'] == lock
        elif intfc == LINE_OPT.format(option_args['slot']):
            assert netconf.get_state(LINE_OPT.format(option_args['slot']), 'adm_state')['administrative-state'] == lock
        elif intfc == LINE_OTU.format(option_args['slot']):
            assert netconf.get_state(LINE_OTU.format(option_args['slot']), 'adm_state')['administrative-state'] == lock


class TestLineOPT:

    @pytest.mark.parametrize(
        'aid, on_transmitter',
        [
            [LINE_OPT] * 2
        ],
        indirect=['on_transmitter']
    )
    def test_transmitter(self, netconf, xml_data, aid, on_transmitter, option_args):
        state_before = netconf.get_state(aid.format(option_args['slot']), 'tx_enable')
        false = 'false'
        logger.warning(
            f'Состояние передатчика [ {aid.format(option_args["slot"])} ] ДО изменения [ {state_before["tx-enable"]} ]')

        netconf.edit_conf_and_commit(xml_data.change_tx_enable(false, aid.format(option_args['slot'])))
        sleep(30)

        state_after = netconf.get_state(aid.format(option_args['slot']), 'tx_enable')
        logger.warning(
            f'Состояние передатчика [ {aid.format(option_args["slot"])} ] ПОСЛЕ изменения [ {state_after["tx-enable"]} ]')

        assert netconf.get_state(aid.format(option_args['slot']), 'tx_enable')['tx-enable'] == false

    @pytest.mark.parametrize(
        'value',
        [
            str(p) for p in range(-15, 4)
        ]
    )
    def test_transmitter_opt_pw(self, value, netconf, xml_data, option_args):
        logger.warning(f'Установка выходной мощности [ {value} ]')
        netconf.edit_conf_and_commit(xml_data.change_tx_power(value=value, aid=LINE_OPT.format(option_args['slot'])))
        sleep(60)

        assert float(netconf.get_state(LINE_OPT.format(option_args['slot']), 'tx_opt_pwr')['tx-optical-power']) == float(value)

    @pytest.mark.parametrize(
        'mode',
        [
            'necemot:ndiff-16qam-ofec-200g',
            'necemot:ndiff-8qam-ofec-200g',
            'necemot:ndiff-qpsk-ofec-200g',
            'necemot:ndiff-qpsk-ofec-100g'
        ]
    )
    def test_mode_of_coh_opt(self, mode, netconf, xml_data, option_args):
        logger.warning(f'Установка режима работы когерентной оптики [ {mode} ]')
        netconf.edit_conf_and_commit(xml_data.select_coherent_opt_mode(mode, LINE_OPT.format(option_args['slot'])))
        sleep(120)

        assert netconf.get_state(LINE_OPT.format(option_args['slot']), 'coh_oper_mode')['coherent-operating-mode']['#text'] == mode

    @pytest.mark.parametrize(
        'ch',
        [
            str(f'C{int(x)}') if not x % 1 else str(f'C{int(x)}e') for x in arange(13, 61.5, 0.5)
        ]
    )
    def test_sel_ch_num(self, ch, netconf, xml_data, option_args):
        logger.warning(f'Установка номера канала [ {ch} ]')
        netconf.edit_conf_and_commit(xml_data.select_wavelength_via_ch(ch, LINE_OPT.format(option_args['slot'])))
        sleep(30)

        assert netconf.get_state(LINE_OPT.format(option_args['slot']), 'ch_state')['wavelength']['channel']['#text'] == ch

    @pytest.mark.parametrize(
        'disp',
        [
            str(d) for d in range(0, 100000, 20000)
        ],
        ids=lambda d: f'Dispersion {d}'
    )
    def test_min_dispersion_set(self, disp, netconf, xml_data, option_args):
        logger.warning(f'Установка значения нижнего порога поиска хроматической дисперсии [ {disp} пс/нм ]')
        netconf.edit_conf_and_commit(xml_data.change_min_thr_dispersion(disp, LINE_OPT.format(option_args['slot'])))
        sleep(90)

        assert netconf.get_state(LINE_OPT.format(option_args['slot']), 'min_thr_disp')['chromatic-dispersion-min-threshold'] == disp

    @pytest.mark.parametrize(
        'disp',
        [
            str(d) for d in range(-80000, 0, 20000)
        ],
        ids=lambda d: f'Dispersion {d}'
    )
    def test_max_dispersion_set(self, disp, netconf, xml_data, option_args):
        logger.warning(f'Установка значения верхнего порога поиска хроматической дисперсии [ {disp} пс/нм ]')
        netconf.edit_conf_and_commit(xml_data.change_max_thr_dispersion(disp, LINE_OPT.format(option_args['slot'])))
        sleep(90)

        assert netconf.get_state(LINE_OPT.format(option_args['slot']), 'max_thr_disp')['chromatic-dispersion-max-threshold'] == disp
