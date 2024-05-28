import logging
from time import sleep
# from itertools import product

import pytest
from deepdiff import DeepDiff

logger = logging.getLogger(__name__)


class TestSftThrReset:

    @pytest.mark.parametrize(
        'idx, get_cl_sfp_thr',
        list(enumerate(range(1, 9), 1)),
        indirect=['get_cl_sfp_thr']
    )
    def test_cl_thr_reset(self, atlas_session, get_cl_sfp_thr, idx, option_args):
        logger.warning(f'Сброс порогов QSFP{idx}ThrReset')
        atlas_session.set_param(f'{option_args.get("dev_cls")}_{option_args.get("slot")}_QSFP{idx}ThrReset', '0')
        sleep(10)
        thr_names, values_before, thr_values_before = get_cl_sfp_thr

        read_thr_value = dict(zip(values_before, map(lambda n: atlas_session.get_param(
            f'{option_args.get("dev_cls")}_{option_args.get("slot")}_ATP1Cl{idx}{n}'), thr_names)))

        diff = DeepDiff(thr_values_before, read_thr_value, verbose_level=2)

        assert not diff
