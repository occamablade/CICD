import logging
from time import sleep

import pytest

logger = logging.getLogger(__name__)

opukTpDestMux1Dict = {
    '1': '80000',
    '2': '40000',
    '3': '20000',
    '4': '10000',
    '5': '8000',
    '6': '4000',
    '7': '2000',
    '8': '1000',
    '9': '800',
    '10': '400'
}

opukTpDestMux2Dict = {
    '1': '200',
    '2': '100',
    '3': '80',
    '4': '40',
    '5': '20',
    '6': '10',
    '7': '8',
    '8': '4',
    '9': '2',
    '10': '1'
}

opukTpDestMux1DictOffset3 = {
    '4': '10000',
    '5': '8000',
    '6': '4000',
    '7': '2000',
    '8': '1000',
    '9': '800',
    '10': '400',
    '11': '200',
    '12': '100',
    '13': '80'
}

opukTpDestMux2DictOffset3 = {
    '14': '40',
    '15': '20',
    '16': '10',
    '17': '8',
    '18': '4',
    '19': '2',
    '20': '1',
    '1': '80000',
    '2': '40000',
    '3': '20000'
}

opukTpDestMux1DictOffset4 = {
    '17': '8',
    '18': '4',
    '19': '2',
    '20': '1',
    '1': '80000',
    '2': '40000',
    '3': '20000',
    '4': '10000',
    '5': '8000',
    '6': '4000'
}

opukTpDestMux2DictOffset4 = {
    '7': '2000',
    '8': '1000',
    '9': '800',
    '10': '400',
    '11': '200',
    '12': '100',
    '13': '80',
    '14': '40',
    '15': '20',
    '16': '10'
}

maskDict = {
    '1': '000000FF 00000000 00000000',
    '2': '0000FF00 00000000 00000000',
    '3': '00FF0000 00000000 00000000',
    '4': 'FF000000 00000000 00000000',
    '5': '00000000 000000FF 00000000',
    '6': '00000000 0000FF00 00000000',
    '7': '00000000 00FF0000 00000000',
    '8': '00000000 FF000000 00000000',
    '9': '00000000 00000000 000000FF',
    '10': '00000000 00000000 0000FF00'
}


class TestTraffic:

    @pytest.mark.parametrize('port', [p for p in range(1, 21)])
    @pytest.mark.forward
    @pytest.mark.reverse
    @pytest.mark.offset3
    @pytest.mark.offset4
    def test_unlock_cl_ports(self, atlas_session, port, option_args):
        atlas_session.unlock(set_req=f'mjc2:{option_args.get("slot")}:Cl{port}')
        assert atlas_session.get_param(f'mjc2_{option_args.get("slot")}_ATP1Cl{port}PortState') == '2'
        assert atlas_session.get_param(f'mjc2_{option_args.get("slot")}_ATP1Cl{port}TxEnable') == '1'
        logger.info(f'Порт {port} разблокирован')

    @pytest.mark.parametrize('port', [f'{p}' for p in range(1, 21)])
    @pytest.mark.forward
    @pytest.mark.reverse
    @pytest.mark.offset3
    def test_traffic_type_on_cl_ports(self, atlas_session, port, option_args):
        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATP1Cl{port}DRSet', option_args.get('tr_type'))
        assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATP1Cl{port}DRSet',
                                            option_args.get('tr_type')) is None
        logger.info(f'Тип трафика на Cl{port} установлен')

    @pytest.mark.parametrize('port', [p for p in range(1, 21)])
    @pytest.mark.offset4
    def test_traffic_type_on_cl_ports_half(self, atlas_session, port, option_args):
        if port <= 10:
            atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATP1Cl{port}DRSet', option_args.get('half')[0])
            assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATP1Cl{port}DRSet',
                                                option_args.get('half')[0]) is None
            logger.info(f'Тип трафика на Cl{port} установлен')
        else:
            atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATP1Cl{port}DRSet', option_args.get('half')[1])
            assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATP1Cl{port}DRSet',
                                                option_args.get('half')[1]) is None
            logger.info(f'Тип трафика на Cl{port} установлен')

    @pytest.mark.forward
    @pytest.mark.reverse
    @pytest.mark.offset3
    @pytest.mark.offset4
    def test_setup_ln1(self, atlas_session, option_args):
        atlas_session.unlock(set_req=f'mjc2:{option_args.get("slot")}:Ln1')
        assert atlas_session.get_param(f'mjc2_{option_args.get("slot")}_ATP1Ln1PortState') == '2'
        logger.info(f'Порт Ln1 разблокирован')
        sleep(160)
        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATP1Ln1DRSet', '1')
        assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATP1Ln1DRSet', '1') is None
        logger.info(f'Тип трафика на Ln1 200G')

        # atlas_session.set_param('mjc2_4_ATP1Ln1OPUkTp1Src', '3')
        # assert atlas_session.check_response('mjc2_4_ATP1Ln1OPUkTp1Src', '3') is None
        # logger.info(f'Установка источника для Ln1OPUkTp1 завершена')
        #
        # atlas_session.set_param(f'mjc2_4_ATP1Ln1OPUkTp1DestAdd', '1')
        # assert atlas_session.check_response('mjc2_4_ATP1Ln1OPUkTp1Dest', '2') is None
        # logger.info('Добавление направление для Ln1OPUkTp1 завершена')

    @pytest.mark.parametrize('val', [v for v in range(1, 11)])
    @pytest.mark.forward
    def test_setup_mux1(self, atlas_session, val, option_args):
        if option_args['mask'] == '1':
            logger.info('Добавление ТР через MaskSet')
            atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux1OPUTsMaskSet',
                                    maskDict.get(str(val)))
            assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux1OPUTsMaskSet',
                                                f'{maskDict.get(str(val))}') is None
            logger.info(f'Выбран трибутарный порт OPU [ OPUkTp{val} ]')
        else:
            logger.info('Добавление ТР через Select')
            atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux1OPUTpSelect', f'{val}')
            assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux1OPUTpSelect',
                                                f'{val}') is None
            logger.info(f'Выбран трибутарный порт OPU [ OPUkTp{val} ]')

        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux1OPUTpPayloadSet', '1')
        assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux1OPUTpPayloadSet', '1') is None
        logger.info(f'Полезная нагрузка для [ OPUkTp{val} ] ODU2')

        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux1OPUTpAdd', '1')
        logger.info(f'Трибутарный порт OPU [ OPUkTp{val} ] добавлен в матрицу')

        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux1OPUkTp{val}ClSrc', f'{val}')
        assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux1OPUkTp{val}ClSrc',
                                            f'{val}') is None
        logger.info(f'Установка источника для Mux1 [ OPUkTp{val} ] завершена')

        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux1OPUkTp{val}ClDestAdd', f'{val}')
        assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux1OPUkTp{val}ClDest',
                                            opukTpDestMux1Dict.get(f'{val}')) is None
        logger.info(f'Добавление направление для Mux1 [ OPUkTp{val} ] завершена')

    @pytest.mark.parametrize('val', [v for v in range(1, 11)])
    @pytest.mark.forward
    def test_setup_mux2(self, atlas_session, val, option_args):
        if option_args['mask'] == '1':
            logger.info('Добавление ТР через MaskSet')
            atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux2OPUTsMaskSet',
                                    maskDict.get(str(val)))
            assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux2OPUTsMaskSet',
                                                f'{maskDict.get(str(val))}') is None
            logger.info(f'Выбран трибутарный порт OPU [ OPUkTp{val} ]')
        else:
            logger.info('Добавление ТР через Select')
            atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux2OPUTpSelect', f'{val}')
            assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux2OPUTpSelect',
                                                f'{val}') is None
            logger.info(f'Выбран трибутарный порт OPU [ OPUkTp{val} ]')

        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux2OPUTpPayloadSet', '1')
        assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux2OPUTpPayloadSet', '1') is None
        logger.info(f'Полезная нагрузка для [ OPUkTp{val + 10} ] ODU2')

        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux2OPUTpAdd', '1')
        logger.info(f'Трибутарный порт OPU [ OPUkTp{val + 10} ] добавлен в матрицу')

        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux2OPUkTp{val}ClSrc', f'{val + 10}')
        assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux2OPUkTp{val}ClSrc',
                                            f'{val + 10}') is None
        logger.info(f'Установка источника для Mux2 [ OPUkTp{val + 10} ] завершена')

        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux2OPUkTp{val}ClDestAdd', f'{val + 10}')
        assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux2OPUkTp{val}ClDest',
                                            opukTpDestMux2Dict.get(f'{val}')) is None
        logger.info(f'Добавление направление для Mux2 [ OPUkTp{val + 10} ] завершена')

    @pytest.mark.parametrize('port, val', [(p, v) for p, v in enumerate(reversed(range(1, 11)), 1)])
    @pytest.mark.reverse
    def test_setup_mux1_wth_offset(self, atlas_session, port, val, option_args):
        if option_args['mask'] == '1':
            logger.info('Добавление ТР через MaskSet')
            atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux1OPUTsMaskSet', maskDict.get(str(port)))
            assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux1OPUTsMaskSet',
                                                f'{maskDict.get(str(port))}') is None
            logger.info(f'Выбран трибутарный порт OPU [ OPUkTp{val} ]')
        else:
            logger.info('Добавление ТР через Select')
            atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux1OPUTpSelect', f'{port}')
            assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux1OPUTpSelect',
                                                f'{port}') is None
            logger.info(f'Выбран трибутарный порт OPU [ OPUkTp{port} ]')

        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux1OPUTpPayloadSet', '1')
        assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux1OPUTpPayloadSet', '1') is None
        logger.info(f'Полезная нагрузка для [ OPUkTp{val + 10} ] ODU2')

        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux1OPUTpAdd', '1')
        logger.info(f'Трибутарный порт OPU [ OPUkTp{val + 10} ] добавлен в матрицу')

        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux1OPUkTp{port}ClSrc', f'{val + 10}')
        assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux1OPUkTp{port}ClSrc',
                                            f'{val + 10}') is None
        logger.info(f'Установка источника для Mux1 [ OPUkTp{val + 10} ] завершена')

        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux1OPUkTp{port}ClDestAdd', f'{val + 10}')
        assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux1OPUkTp{port}ClDest',
                                            opukTpDestMux2Dict.get(f'{val}')) is None
        logger.info(f'Добавление направление для Mux1 [ OPUkTp{val + 10} ] завершена')

    @pytest.mark.parametrize('port, val', [(p, v) for p, v in enumerate(reversed(range(1, 11)), 1)])
    @pytest.mark.reverse
    def test_setup_mux2_wth_offset(self, atlas_session, port, val, option_args):
        if option_args['mask'] == '1':
            logger.info('Добавление ТР через MaskSet')
            atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux2OPUTsMaskSet', maskDict.get(str(port)))
            assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux2OPUTsMaskSet',
                                                f'{maskDict.get(str(port))}') is None
            logger.info(f'Выбран трибутарный порт OPU [ OPUkTp{val} ]')
        else:
            logger.info('Добавление ТР через Select')
            atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux2OPUTpSelect', f'{port}')
            assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux2OPUTpSelect',
                                                f'{port}') is None
            logger.info(f'Выбран трибутарный порт OPU [ OPUkTp{port} ]')

        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux2OPUTpPayloadSet', '1')
        assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux2OPUTpPayloadSet', '1') is None
        logger.info(f'Полезная нагрузка для [ OPUkTp{port} ] ODU2')

        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux2OPUTpAdd', '1')
        logger.info(f'Трибутарный порт OPU [ OPUkTp{port} ] добавлен в матрицу')

        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux2OPUkTp{port}ClSrc', f'{val}')
        assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux2OPUkTp{port}ClSrc',
                                            f'{val}') is None
        logger.info(f'Установка источника для Mux2 [ OPUkTp{val} ] завершена')

        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux2OPUkTp{port}ClDestAdd', f'{val}')
        assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux2OPUkTp{port}ClDest',
                                            opukTpDestMux1Dict.get(f'{val}')) is None
        logger.info(f'Добавление направление для Mux2 [ OPUkTp{val} ] завершена')

    @pytest.mark.parametrize('port, val', [(p, v) for p, v in enumerate(range(4, 14), 1)])
    @pytest.mark.offset3
    def test_setup_mux1_wth_offset3(self, atlas_session, port, val, option_args):
        if option_args['mask'] == '1':
            logger.info('Добавление ТР через MaskSet')
            atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux1OPUTsMaskSet', maskDict.get(str(port)))
            assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux1OPUTsMaskSet',
                                                f'{maskDict.get(str(port))}') is None
            logger.info(f'Выбран трибутарный порт OPU [ OPUkTp{val} ]')
        else:
            logger.info('Добавление ТР через Select')
            atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux1OPUTpSelect', f'{port}')
            assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux1OPUTpSelect',
                                                f'{port}') is None
            logger.info(f'Выбран трибутарный порт OPU [ OPUkTp{port} ]')

        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux1OPUTpPayloadSet', '1')
        assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux1OPUTpPayloadSet', '1') is None
        logger.info(f'Полезная нагрузка для [ OPUkTp{val} ] ODU2')

        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux1OPUTpAdd', '1')
        logger.info(f'Трибутарный порт OPU [ OPUkTp{val} ] добавлен в матрицу')

        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux1OPUkTp{port}ClSrc', f'{val}')
        assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux1OPUkTp{port}ClSrc',
                                            f'{val}') is None
        logger.info(f'Установка источника для Mux1 [ OPUkTp{val} ] завершена')

        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux1OPUkTp{port}ClDestAdd', f'{val}')
        assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux1OPUkTp{port}ClDest',
                                            opukTpDestMux1DictOffset3.get(f'{val}')) is None
        logger.info(f'Добавление направление для Mux1 [ OPUkTp{val} ] завершена')

    @pytest.mark.parametrize('port, val', [(p, v) for p, v in enumerate(range(14, 21), 1)] + [(8, 1), (9, 2), (10, 3)])
    @pytest.mark.offset3
    def test_setup_mux2_wth_offset3(self, atlas_session, port, val, option_args):
        if option_args['mask'] == '1':
            logger.info('Добавление ТР через MaskSet')
            atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux2OPUTsMaskSet', maskDict.get(str(port)))
            assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux2OPUTsMaskSet',
                                                f'{maskDict.get(str(port))}') is None
            logger.info(f'Выбран трибутарный порт OPU [ OPUkTp{val} ]')
        else:
            logger.info('Добавление ТР через Select')
            atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux2OPUTpSelect', f'{port}')
            assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux2OPUTpSelect',
                                                f'{port}') is None
            logger.info(f'Выбран трибутарный порт OPU [ OPUkTp{port} ]')

        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux2OPUTpPayloadSet', '1')
        assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux2OPUTpPayloadSet', '1') is None
        logger.info(f'Полезная нагрузка для [ OPUkTp{port} ] ODU2')

        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux2OPUTpAdd', '1')
        logger.info(f'Трибутарный порт OPU [ OPUkTp{port} ] добавлен в матрицу')

        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux2OPUkTp{port}ClSrc', f'{val}')
        assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux2OPUkTp{port}ClSrc',
                                            f'{val}') is None
        logger.info(f'Установка источника для Mux2 [ OPUkTp{val} ] завершена')

        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux2OPUkTp{port}ClDestAdd', f'{val}')
        assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux2OPUkTp{port}ClDest',
                                            opukTpDestMux2DictOffset3.get(f'{val}')) is None
        logger.info(f'Добавление направление для Mux2 [ OPUkTp{val} ] завершена')

    @pytest.mark.parametrize('port, val', [(i, e) for i, e in enumerate(range(17, 21), 1)] +
                             [(i, e) for i, e in enumerate(range(1, 7), 5)])
    @pytest.mark.offset4
    def test_setup_mux1_wth_offset4(self, atlas_session, port, val, option_args):
        if option_args['mask'] == '1':
            logger.info('Добавление ТР через MaskSet')
            atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux1OPUTsMaskSet', maskDict.get(str(port)))
            assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux1OPUTsMaskSet',
                                                f'{maskDict.get(str(port))}') is None
            logger.info(f'Выбран трибутарный порт OPU [ OPUkTp{val} ]')
        else:
            logger.info('Добавление ТР через Select')
            atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux1OPUTpSelect', f'{port}')
            assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux1OPUTpSelect',
                                                f'{port}') is None
            logger.info(f'Выбран трибутарный порт OPU [ OPUkTp{port} ]')

        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux1OPUTpPayloadSet', '1')
        assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux1OPUTpPayloadSet', '1') is None
        logger.info(f'Полезная нагрузка для [ OPUkTp{val} ] ODU2')

        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux1OPUTpAdd', '1')
        logger.info(f'Трибутарный порт OPU [ OPUkTp{val} ] добавлен в матрицу')

        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux1OPUkTp{port}ClSrc', f'{val}')
        assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux1OPUkTp{port}ClSrc',
                                            f'{val}') is None
        logger.info(f'Установка источника для Mux1 [ OPUkTp{val} ] завершена')

        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux1OPUkTp{port}ClDestAdd', f'{val}')
        assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux1OPUkTp{port}ClDest',
                                            opukTpDestMux1DictOffset4.get(f'{val}')) is None
        logger.info(f'Добавление направление для Mux1 [ OPUkTp{val} ] завершена')

    @pytest.mark.parametrize('port, val', [(i, e) for i, e in enumerate(range(7, 11), 1)] +
                             [(i, e) for i, e in enumerate(range(11, 17), 5)])
    @pytest.mark.offset4
    def test_setup_mux2_wth_offset4(self, atlas_session, port, val, option_args):
        if option_args['mask'] == '1':
            logger.info('Добавление ТР через MaskSet')
            atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux2OPUTsMaskSet', maskDict.get(str(port)))
            assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux2OPUTsMaskSet',
                                                f'{maskDict.get(str(port))}') is None
            logger.info(f'Выбран трибутарный порт OPU [ OPUkTp{val} ]')
        else:
            logger.info('Добавление ТР через Select')
            atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux2OPUTpSelect', f'{port}')
            assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux2OPUTpSelect',
                                                f'{port}') is None
            logger.info(f'Выбран трибутарный порт OPU [ OPUkTp{port} ]')

        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux2OPUTpPayloadSet', '1')
        assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux2OPUTpPayloadSet', '1') is None
        logger.info(f'Полезная нагрузка для [ OPUkTp{port} ] ODU2')

        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux2OPUTpAdd', '1')
        logger.info(f'Трибутарный порт OPU [ OPUkTp{port} ] добавлен в матрицу')

        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux2OPUkTp{port}ClSrc', f'{val}')
        assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux2OPUkTp{port}ClSrc',
                                            f'{val}') is None
        logger.info(f'Установка источника для Mux2 [ OPUkTp{val} ] завершена')

        atlas_session.set_param(f'mjc2_{option_args.get("slot")}_ATPMux2OPUkTp{port}ClDestAdd', f'{val}')
        assert atlas_session.check_response(f'mjc2_{option_args.get("slot")}_ATPMux2OPUkTp{port}ClDest',
                                            opukTpDestMux2DictOffset4.get(f'{val}')) is None
        logger.info(f'Добавление направление для Mux2 [ OPUkTp{val} ] завершена')

    # @pytest.mark.forward
    # @pytest.mark.reverse
    # @pytest.mark.offset3
    # @pytest.mark.offset4
    # def test_check_traffic(self, mts5800):
    #     mts5800.restart_test(1)
    #     sleep(30)
    #     assert mts5800.status_test(1)
