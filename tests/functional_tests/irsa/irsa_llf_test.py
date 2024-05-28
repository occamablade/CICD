import logging


logger = logging.getLogger(__name__)


def test_llf_cne(llf_cne, write_result):
    assert llf_cne, 'Словарь пуст'
    write_result(llf_cne)
