import pytest
import logging

logger = logging.getLogger(__name__)

lpbk_decode = {
    '1': 'Линия на линию',
    '2': 'Линия на клиентов'
}


@pytest.fixture
def del_lpbk(atlas_session, option_args):
    yield
    atlas_session.del_lpbk(dev=option_args.get("dev_cls"),
                           slot=option_args.get("slot"),
                           port=option_args.get("line_port")
                           )


@pytest.mark.usefixtures('get_sw_data')
class TestLoopback:

    def test_lpbk_ln2ln(self, atlas_session, option_args, del_lpbk):
        atlas_session.ln_lpbk(dev=option_args.get("dev_cls"),
                              slot=option_args.get("slot"),
                              port=option_args.get("line_port"),
                              direction='ln'
                              )
        assert atlas_session.get_param(
            f'{option_args.get("dev_cls")}_{option_args.get("slot")}_ATP1Ln{option_args.get("line_port")}LBModeSet') == '1', \
            ('Loopback не установился. Значение параметра ATP1Ln1LBModeSet ',
             atlas_session.get_param(
                 f'{option_args.get("dev_cls")}_{option_args.get("slot")}_ATP1Ln{option_args.get("line_port")}LBModeSet'))

    def test_lpbk_ln2cl(self, atlas_session, option_args, del_lpbk):
        atlas_session.ln_lpbk(dev=option_args.get("dev_cls"),
                              slot=option_args.get("slot"),
                              port=option_args.get("line_port"),
                              direction='cl'
                              )
        assert atlas_session.get_param(
            f'{option_args.get("dev_cls")}_{option_args.get("slot")}_ATP1Ln{option_args.get("line_port")}LBModeSet') == '2', \
            ('Loopback не установился. Значение параметра ATP1Ln1LBModeSet ',
             atlas_session.get_param(
                 f'{option_args.get("dev_cls")}_{option_args.get("slot")}_ATP1Ln{option_args.get("line_port")}LBModeSet'))
