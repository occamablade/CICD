import json

from base.RestConf.restconf import RestConf


class Cfg23Chs(RestConf):

    def __init__(self):
        self.url_path = 'data/em-config'
        super().__init__(path=self.url_path, node='19.25')

    def config_cl1_slot1(self, duration, period, llf_delay):
        billet_cfg = {
            "interfaces": {
                "interface": [
                    {
                        "aid": 'OPT-1-1-1-0-C1',
                        "administrative-state": "unlocked",
                        "nec-em-optics:optics": {
                            "als-llf-pulse-duration": duration,
                            "als-llf-pulse-period": period,
                            "als-trigger-delay": 0,
                            "llf-trigger-delay": llf_delay

                        }
                    }
                ]
            }
        }

        cfg = json.dumps(billet_cfg)
        self.set_restconf(cfg=cfg)
        print(self.execute_rpc(cfg=cfg))

    def config_cl1_slot3(self, duration, period, llf_delay):
        billet_cfg = {
            "interfaces": {
                "interface": [
                    {
                        "aid": 'OPT-1-1-3-0-C1',
                        "administrative-state": "unlocked",
                        "nec-em-optics:optics": {
                            "als-llf-pulse-duration": duration,
                            "als-llf-pulse-period": period,
                            "als-trigger-delay": 0,
                            "llf-trigger-delay": llf_delay

                        }
                    }
                ]
            }
        }

        cfg = json.dumps(billet_cfg)
        self.set_restconf(cfg=cfg)
        print(self.execute_rpc(cfg=cfg))

