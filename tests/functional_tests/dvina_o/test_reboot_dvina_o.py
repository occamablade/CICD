import logging
# from itertools import product

import pytest

logger = logging.getLogger(__name__)

DR_SET = {
    '0': '100G',
    '1': '200G',
    '2': '300G',
    '3': '400G'
}
MOD_FMT = {
    '1': 'DP-P-QPSK',
    '2': 'DP-QPSK',
    '3': 'DP-P-16QAM',
    '4': 'DP-16QAM',
    '5': 'DP-32QAM',
    '6': 'DP-64QAM'
}
FEC = {
    '0': '15% SDFEC',
    '1': '27% SDFEC'
}
PHASE = {
    '0': 'Кодирование фазы: Прямое',
    '1': 'Кодирование фазы: Дифференциальное'
}
REG = {
    '1': 'Режим регенератора: ВКЛ',
    '0': 'Режим регенератора: ВЫКЛ',
}
SOP = {
    '1': 'SOP tolerance: ВКЛ',
    '0': 'SOP tolerance: ВЫКЛ'
}

setup_pairs = (
        ('0', '1', '2', '3'), ('1', '2', '3', '4', '5', '6'), ('0', '1'), ('0', '1'),
        ('1', '0'), ('1', '0'), ('0', '64', '128', '255')
    )


class TestReboot:

    @pytest.mark.parametrize(
        'drSet',
        [
            '0', '1', '2', '3'
        ]
    )
    def test_drSet_reboot(self, atlas_session, option_args, drSet, backup_diff):
        mcu_sw = atlas_session.get_param(f'mjp2_{option_args["slot"]}_SwNumber')
        logger.warning(f'Версия ВПО платы - [ {mcu_sw} ]')
        logger.warning(f'{DR_SET[drSet]}')

        atlas_session.set_param(f'mjp2_{option_args["slot"]}_ATP1Ln1DRSet', drSet)
        assert atlas_session.check_response(f'mjp2_{option_args["slot"]}_ATP1Ln1DRSet', drSet) is None

        assert not backup_diff, f'После перезагрузки слотового устройства параметры не совпадают: [ {backup_diff} ]'

    @pytest.mark.parametrize(
        'modFmt',
        [
            '1', '2', '3', '4', '5', '6'
        ]
    )
    def test_modFmt_reboot(self, atlas_session, option_args, modFmt, backup_diff):
        mcu_sw = atlas_session.get_param(f'mjp2_{option_args["slot"]}_SwNumber')
        logger.warning(f'Версия ВПО платы - [ {mcu_sw} ]')
        logger.warning(f'{DR_SET[modFmt]}')

        atlas_session.set_param(f'mjp2_{option_args["slot"]}_ATP1Ln1ModFmt', modFmt)
        assert atlas_session.check_response(f'mjp2_{option_args["slot"]}_ATP1Ln1ModFmt', modFmt) is None

        assert not backup_diff, f'После перезагрузки слотового устройства параметры не совпадают: [ {backup_diff} ]'

    @pytest.mark.parametrize(
        'fec',
        [
            '0', '1'
        ]
    )
    def test_fec_reboot(self, atlas_session, option_args, fec, backup_diff):
        mcu_sw = atlas_session.get_param(f'mjp2_{option_args["slot"]}_SwNumber')
        logger.warning(f'Версия ВПО платы - [ {mcu_sw} ]')
        logger.warning(f'{DR_SET[fec]}')

        atlas_session.set_param(f'mjp2_{option_args["slot"]}_ATP1Ln1FECSet', fec)
        assert atlas_session.check_response(f'mjp2_{option_args["slot"]}_ATP1Ln1FECSet', fec) is None

        assert not backup_diff, f'После перезагрузки слотового устройства параметры не совпадают: [ {backup_diff} ]'

    @pytest.mark.parametrize(
        'phaseEnc',
        [
            '0', '1'
        ]
    )
    def test_phaseEnc_reboot(self, atlas_session, option_args, phaseEnc, backup_diff):
        mcu_sw = atlas_session.get_param(f'mjp2_{option_args["slot"]}_SwNumber')
        logger.warning(f'Версия ВПО платы - [ {mcu_sw} ]')
        logger.warning(f'{DR_SET[phaseEnc]}')

        atlas_session.set_param(f'mjp2_{option_args["slot"]}_ATP1Ln1PhaseEncoding', phaseEnc)
        assert atlas_session.check_response(f'mjp2_{option_args["slot"]}_ATP1Ln1PhaseEncoding', phaseEnc) is None

        assert not backup_diff, f'После перезагрузки слотового устройства параметры не совпадают: [ {backup_diff} ]'

    @pytest.mark.parametrize(
        'regMode',
        [
            '0', '1'
        ]
    )
    def test_regMode_reboot(self, atlas_session, option_args, regMode, backup_diff):
        mcu_sw = atlas_session.get_param(f'mjp2_{option_args["slot"]}_SwNumber')
        logger.warning(f'Версия ВПО платы - [ {mcu_sw} ]')
        logger.warning(f'{DR_SET[regMode]}')

        atlas_session.set_param(f'mjp2_{option_args["slot"]}_ATP1LnRegenMode', regMode)
        assert atlas_session.check_response(f'mjp2_{option_args["slot"]}_ATP1LnRegenMode', regMode) is None

        assert not backup_diff, f'После перезагрузки слотового устройства параметры не совпадают: [ {backup_diff} ]'

    @pytest.mark.parametrize(
        'sopTol',
        [
            '0', '1'
        ]
    )
    def test_sopTol_reboot(self, atlas_session, option_args, sopTol, backup_diff):
        mcu_sw = atlas_session.get_param(f'mjp2_{option_args["slot"]}_SwNumber')
        logger.warning(f'Версия ВПО платы - [ {mcu_sw} ]')
        logger.warning(f'{DR_SET[sopTol]}')

        atlas_session.set_param(f'mjp2_{option_args["slot"]}_ATP1Ln1SetSopTol', sopTol)
        assert atlas_session.check_response(f'mjp2_{option_args["slot"]}_ATP1Ln1SetSopTol', sopTol) is None

        assert not backup_diff, f'После перезагрузки слотового устройства параметры не совпадают: [ {backup_diff} ]'

    @pytest.mark.parametrize(
        'bichmStep',
        [
            '0', '1'
        ]
    )
    def test_bichmStep_reboot(self, atlas_session, option_args, bichmStep, backup_diff):
        mcu_sw = atlas_session.get_param(f'mjp2_{option_args["slot"]}_SwNumber')
        logger.warning(f'Версия ВПО платы - [ {mcu_sw} ]')
        logger.warning(f'{DR_SET[bichmStep]}')

        atlas_session.set_param(f'mjp2_{option_args["slot"]}_ATP1Ln1BICHMStepSet', bichmStep)
        assert atlas_session.check_response(f'mjp2_{option_args["slot"]}_ATP1Ln1BICHMStepSet', bichmStep) is None

        assert not backup_diff, f'После перезагрузки слотового устройства параметры не совпадают: [ {backup_diff} ]'

    @pytest.mark.parametrize(
        'trigDel, pulseWidth, pulseInt',
        [
            ('500', '2000', '7000')
        ]
    )
    def test_ln_als_reboot(self,
                           atlas_session,
                           option_args,
                           trigDel,
                           pulseWidth,
                           pulseInt,
                           backup_diff
                           ):
        mcu_sw = atlas_session.get_param(f'mjp2_{option_args["slot"]}_SwNumber')
        logger.warning(f'Версия ВПО платы - [ {mcu_sw} ]')

        atlas_session.set_param(f'mjp2_{option_args["slot"]}_ATP1Ln1ALSClTriggerDelay', trigDel)
        assert atlas_session.check_response(f'mjp2_{option_args["slot"]}_ATP1Ln1ALSClTriggerDelay', trigDel) is None

        atlas_session.set_param(f'mjp2_{option_args["slot"]}_ATP1Ln1ALSPulseWidth', pulseWidth)
        assert atlas_session.check_response(f'mjp2_{option_args["slot"]}_ATP1Ln1ALSPulseWidth', pulseWidth) is None

        atlas_session.set_param(f'mjp2_{option_args["slot"]}_ATP1Ln1ALSPulseInterval', pulseInt)
        assert atlas_session.check_response(f'mjp2_{option_args["slot"]}_ATP1Ln1ALSPulseInterval', pulseInt) is None

        assert not backup_diff, f'После перезагрузки слотового устройства параметры не совпадают: [ {backup_diff} ]'

    @pytest.mark.parametrize(
        'trigDel, pulseWidth, pulseInt',
        [
            ('500', '2000', '7000')
        ]
    )
    def test_cl_als_reboot(self,
                           atlas_session,
                           option_args,
                           trigDel,
                           pulseWidth,
                           pulseInt,
                           backup_diff
                           ):
        mcu_sw = atlas_session.get_param(f'mjp2_{option_args["slot"]}_SwNumber')
        logger.warning(f'Версия ВПО платы - [ {mcu_sw} ]')

        atlas_session.set_param(f'mjp2_{option_args["slot"]}_ATP1Cl1LLFTriggerDelay', trigDel)
        assert atlas_session.check_response(f'mjp2_{option_args["slot"]}_ATP1Cl1LLFTriggerDelay', trigDel) is None

        atlas_session.set_param(f'mjp2_{option_args["slot"]}_ATP1Cl1ALSPulseWidth', pulseWidth)
        assert atlas_session.check_response(f'mjp2_{option_args["slot"]}_ATP1Cl1ALSPulseWidth', pulseWidth) is None

        atlas_session.set_param(f'mjp2_{option_args["slot"]}_ATP1Cl1ALSPulseInterval', pulseInt)
        assert atlas_session.check_response(f'mjp2_{option_args["slot"]}_ATP1Cl1ALSPulseInterval', pulseInt) is None

        assert not backup_diff, f'После перезагрузки слотового устройства параметры не совпадают: [ {backup_diff} ]'
