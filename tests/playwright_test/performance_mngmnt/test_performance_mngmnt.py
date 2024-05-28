import logging


logger = logging.getLogger(__name__)


class TestPerformanceMngmnt:

    def test_setup(self, setup_perf_mngmnt):
        pass

    def test_all_sensors_on_board_t1021(self, all_sensors_on_board_t1021):
        results = all_sensors_on_board_t1021
        for port in results:
            logger.info(f'result for port: {port["port_name"]}  port_tx: {port["port_tx_enable1"]}  output_power1: {port["output_power1"]}')
            logger.info(f'result for port: {port["port_name"]}  port_tx: {port["port_tx_enable2"]}  output_power2: {port["output_power2"]}')
            if port['port_tx_enable1'] == 'false':
                if port['pump_current1'] != 'N/A':
                    assert port['pump_current1'] == 0, \
                        f"At port {port['port_name']} pump-current isn't 0 while port_tx_enable is 'off'"
                assert port['output_power1'] < -20, \
                    f"At port {port['port_name']} output_power={port['output_power1']} while port_tx_enable is 'off'"
            if port['port_tx_enable1'] == 'true':
                if port['pump_current1'] != 'N/A':
                    assert port['pump_current1'] > 15, \
                        f"At port {port['port_name']} pump-current={port['pump-current1']} while port_tx_enable is 'on'"
                assert port['output_power1'] > -20, \
                    f"At port {port['port_name']} output_power={port['output_power1']} while port_tx_enable is 'on'"
            if port['port_tx_enable2'] == 'false':
                if port['pump_current1'] != 'N/A':
                    assert port['pump_current2'] == 0, \
                        f"At port {port['port_name']} pump-current isn't 0 while port_tx_enable is 'off'"
                assert port['output_power2'] < -20, \
                    f"At port {port['port_name']} output_power={port['output_power2']} while port_tx_enable is 'off'"
            if port['port_tx_enable2'] == 'true':
                if port['pump_current1'] != 'N/A':
                    assert port['pump_current2'] > 15, \
                        f"At port {port['port_name']} pump-current={port['pump-current2']} while port_tx_enable is 'on'"
                assert port['output_power2'] > -20, \
                    f"At port {port['port_name']} output_power={port['output_power2']} while port_tx_enable is 'on'"
        logger.info(f'test_all_sensors_on_board_t1021 PASSED')

    def test_teardown(self, teardown_perf_mngmnt):
        pass

    # def tmp(self, tmp1):
    #     pass
