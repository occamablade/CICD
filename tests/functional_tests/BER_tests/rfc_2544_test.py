
class TestRfc2544:

    def test_rfc2544(self, exfoftb):
        assert exfoftb.rfc2544(9, (8, 9600), (9, 16000))
