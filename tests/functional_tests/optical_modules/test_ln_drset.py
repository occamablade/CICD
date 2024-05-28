import logging

import pytest

logger = logging.getLogger(__name__)

mjb6 = {
    '0': '100G',
    '1': '200G',
    '15': 'OFF'
}

mjp2 = {
    '100G': '0',
    '200G': '1',
    '300G': '2',
    '400G': '3',
    'OFF': '6'
}


@pytest.mark.usefixtures('get_sw_data')
class TestDRset:

    @pytest.mark.parametrize(
        'drset',
        [
            '0', '1', '15'
        ],
        indirect=['drset']
    )
    def test_drset_for_azov2(self, drset, atlas_session, option_args):
        tr_type = atlas_session.get_param(f'{option_args.get("dev_cls")}_{option_args.get("slot")}_ATP1Ln1DRSet')
        logger.info(f'Тип трафика установлен {mjb6[tr_type]}')
        assert drset
