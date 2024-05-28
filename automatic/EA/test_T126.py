import logging
from time import sleep

from base.Atlas.atlas import SessionAPI
from confest import testing_slot, testing_devcls, CU_slot, CU_class, count, IP_shassi


before_params = {}
after_params = {}

console_out = logging.StreamHandler()
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
                    datefmt='%m.%d.%Y %H:%M:%S',
                    level=logging.INFO)

t = SessionAPI('s_ap', IP_shassi)


def compare_dicts(dict_before, dict_after, number_test):
    """
    Метод, который сравнивает значения параметров до и после
    Если какое-то значение не восстановилось, то выйдет словарь в виде
    {'Название параметра': ('Что должно быть', 'Что есть по факту')}
    Например: {'EA1.StMode.Set': ('2', '3')}
    """
    if dict_before == dict_after:
        logging.info('all ok')
        return True
    else:
        diff = {k: (v, dict_after[k]) for k, v in dict_before.items() if v != dict_after[k]}
        print(f'На {number_test}-ом прогоне возникли ошибки')
        return diff if diff else True


def all_params(number_test):
    """
    Метод, который производит ребут для всех параметров на устройстве
    """
    logging.info('Создание рез.копии/заполнение словаря before_params текущими значениями значениями')
    t.backup(testing_slot, testing_devcls)  # создаем резервную копию устройства
    sleep(10)
    all_name = t.get_param_backup_data(testing_slot, testing_devcls).keys()
    for param in all_name:
        before_params[param] = t.get_param(f'{testing_devcls}_{testing_slot}_{param}')  # заполнили словарь по типу 'name_param': 'value_param'
    logging.info(f'{before_params}')
    logging.info('Перезагрузка устройства по питанию')
    t.set_param(f'{CU_class}_{CU_slot}_Slot{testing_slot}Enable', '0')
    sleep(20)
    t.set_param(f'{CU_class}_{CU_slot}_Slot{testing_slot}Enable', '2')
    sleep(60)
    logging.info('Сравнение текущих параметров и параметров к восстановлению')
    for param in all_name:
        after_params[param] = t.get_param(f'{testing_devcls}_{testing_slot}_{param}')
    logging.info(f'{after_params}')
    if before_params == after_params:
        logging.info('ok')
    assert compare_dicts(before_params, after_params, number_test) is True


for i in range(1, count + 1):
    all_params(i)
t.logout()
