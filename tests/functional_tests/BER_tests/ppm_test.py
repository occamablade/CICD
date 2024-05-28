import pytest


class TestPPM:

    @pytest.mark.parametrize('ppm', ['100', '-100'], indirect=['ppm'])
    def test_ppm(self, exfoftb, ppm):
        assert exfoftb.status()
