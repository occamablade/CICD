import logging
from time import sleep

import pytest

logger = logging.getLogger(__name__)


class TestAzov2sLoopback:

    @pytest.mark.parametrize('clnum, unlockp', [(i, n) for i, n in enumerate(range(1, 21), 1)], indirect=['unlockp'])
    def test_cl2cl_loopback(self, atlas_session, option_args, clnum, unlockp, mts5800):
        if not clnum % 2:  # если чётный клиент
            logger.info(f'Установка loopback на [ Cl{clnum} ] [ слот {option_args["slots"][1]} ]')
            atlas_session.cl_lpbk(f'mjc2:{option_args["slots"][1]}:Cl{clnum}',
                                  'cl')  # 6 слот, т.к. параметры передаются 6,4
            logger.info(f'Выключение порта на [ Cl{clnum} ] [ слот {option_args["slots"][0]} ]')
            atlas_session.tx_off(f'mjc2:{option_args["slots"][0]}:Cl{clnum}')
            sleep(30)
            mts5800.restart_test(1)
            assert mts5800.status_test(1)
        else:
            logger.info(f'Установка loopback на [ Cl{clnum} ] [ слот {option_args["slots"][0]} ]')
            atlas_session.cl_lpbk(f'mjc2:{option_args["slots"][0]}:Cl{clnum}', 'cl')  # 4 слот
            logger.info(f'Выключение порта на [ Cl{clnum} ] [ слот {option_args["slots"][1]} ]')
            atlas_session.tx_off(f'mjc2:{option_args["slots"][1]}:Cl{clnum}')
            sleep(30)
            mts5800.restart_test(1)
            assert mts5800.status_test(1)

    @pytest.mark.parametrize('clnum, unlockpcl2ln', [(i, n) for i, n in enumerate(range(1, 21), 1)],
                             indirect=['unlockpcl2ln'])
    def test_cl2ln_loopback(self, atlas_session, option_args, clnum, unlockpcl2ln, mts5800):
        if not clnum % 2:  # если чётный клиент
            logger.info(f'Установка loopback на [ Cl{clnum} ] [ слот {option_args["slots"][0]} ]')
            atlas_session.cl_lpbk(f'mjc2:{option_args["slots"][0]}:Cl{clnum}',
                                  'ln')  # 6 слот, т.к. параметры передаются 6,4
            if clnum == 20:
                logger.info(f'Выключение порта на [ Cl{clnum} ] [ слот {option_args["slots"][0]} ]')
                atlas_session.tx_off(f'mjc2:{option_args["slots"][0]}:Cl20')
                mts5800.restart_test(1)
                assert mts5800.status_test(1)
            else:
                logger.info(f'Выключение порта на [ Cl{clnum} ] [ слот {option_args["slots"][0]} ]')
                atlas_session.tx_off(f'mjc2:{option_args["slots"][0]}:Cl{clnum + 1}')
                mts5800.restart_test(1)
                assert mts5800.status_test(1)
        else:
            logger.info(f'Установка loopback на [ Cl{clnum} ] [ слот {option_args["slots"][1]} ]')
            atlas_session.cl_lpbk(f'mjc2:{option_args["slots"][1]}:Cl{clnum}', 'ln')  # 4 слот
            logger.info(f'Выключение порта на [ Cl{clnum} ] [ слот {option_args["slots"][1]} ]')
            atlas_session.tx_off(f'mjc2:{option_args["slots"][1]}:Cl{clnum + 1}')
            mts5800.restart_test(1)
            assert mts5800.status_test(1)

    def test_ln2cl_loopback(self, atlas_session, option_args, mts5800):
        atlas_session.tx_off(f'mjc2:{option_args["slots"][1]}:Ln1')
        atlas_session.ln_lpbk(f'mjc2:{option_args["slots"][0]}:Ln1', 'cl')
        mts5800.restart_test(1)
        assert mts5800.status_test(1)
        atlas_session.del_lpbk(f'mjc2:{option_args["slots"][0]}:Ln1')
        atlas_session.tx_on(f'mjc2:{option_args["slots"][1]}:Ln1')

    def test_ln2ln_loopback(self, atlas_session, option_args, mts5800):
        atlas_session.ln_lpbk(f'mjc2:{option_args["slots"][1]}:Ln1', 'ln')
        atlas_session.tx_off(f'mjc2:{option_args["slots"][1]}:Cl1')
        mts5800.restart_test(1)
        assert mts5800.status_test(1)
        atlas_session.unlock(f'mjc2:{option_args["slots"][1]}:Ln1')
        atlas_session.tx_on(f'mjc2:{option_args["slots"][1]}:Cl1')
