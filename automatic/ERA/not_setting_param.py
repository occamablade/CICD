import logging

from base.Atlas.atlas import Facade
from time import sleep

logger = logging.getLogger(__name__)


def main_test(iteration):
    err_sum = 0
    for i in range(1, iteration + 1):
        logger.info(f'Итерация №{i}')
        logger.info('Перевод HA1.StMode.Set в "Выкл"')
        t.set_param('erstc-9.0.0_6_HA1.StMode.Set', '0')
        sleep(20)
        InPower = t.get_param('erstc-9.0.0_6_HA1.In.Power')
        logger.info(f'Значение параметра HA1.In.Power = {InPower}')
        logger.info('Перевод HA1.StMode.Set в "RAU ON - EDFA Pout"')
        t.set_param('erstc-9.0.0_6_HA1.StMode.Set', '2')
        sleep(20)
        PowerSave = t.get_param('erstc-9.0.0_6_HA1.In.PowerSave')
        logger.info(f'Значение параметра HA1.In.PowerSave = {PowerSave}')
        if InPower != PowerSave:
            err_sum += 1
            print(f'На итерации {i} параметры были разные: '
                  f'\n [ HA1.In.Power = {InPower} ]'
                  f'\n [ HA1.In.PowerSave = {PowerSave} ]')
    print(f'Общее кол-во не установок: {err_sum}')


if __name__ == '__main__':
    IP = '192.168.31.204'  # IP Шасси
    t = Facade('s_ap', str(IP))
    sleep(2)
    count_iteration = 10  # количество итераций
    main_test(count_iteration)
    t.logout()
