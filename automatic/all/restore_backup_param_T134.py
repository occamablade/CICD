from pprint import pprint
from time import sleep

from base.Atlas.atlas import SessionAPI
from Utilities.all import ConfigReset


before_params = {}
after_params = {}


def compare_dicts(dict_before, dict_after):
    """
    Метод, который сравнивает значения параметров до и после
    Если какое-то значение не восстановилось, то выйдет словарь в виде
    {'Название параметра': ('Что должно быть', 'Что есть по факту')}
    Например: {'EA1.StMode.Set': ('2', '3')}
    """
    if dict_before == dict_after:
        print('Все параметры успешно восстановились')
        return True
    else:
        diff = {k: (v, dict_after[k]) for k, v in dict_before.items() if v != dict_after[k]}
        return diff if diff else True


def separate_params():
    """
    Метод, который производит ребут для нескольких, выбранных пользователем, параметров
    """
    params = input(
        'Введите через запятую параметры для проверки: ')  # Пример: EA1.AdmState.Time.Set,EA1.Gain.Set,EA1.Out.PowerSig.Lim.Set
    list_params = params.split(',')
    print('Значения параметров до ребута')
    for param in list_params:
        print(
            f"Значение параметра {param}: {t.get_param(f'{device_class}_{slot}_{param}')}")  # смотрим значения параметров до ребута бекапа
        sleep(2)
        dev_param = input(f'Введите новое значение для параметра {param}: ')  # вводим новое значение параметра
        t.set_param(f'{device_class}_{slot}_{param}', f'{dev_param}')  # меняем значение
        sleep(3)
        before_params[param] = dev_param
    print('Создается резервная копия устройства')
    t.backup(slot, device_class)  # создаем резервную копию устройства
    sleep(10)
    print('Сбрасываем параметры устройства к значениям по умолчанию и проверяем значения параметров')
    t.set_param(ConfigReset.format(device_class, slot),
                '1')  # сбрасываем параметры устройства к значению по умолчанию
    sleep(15)
    for param in list_params:
        print(
            f"Значение параметра {param}: {t.get_param(f'{device_class}_{slot}_{param}')}")  # проверяем сбросились ли значения
        sleep(2)
    print('Восстанавливаем резервную копию')
    t.get_param_backup_data_unparse(slot, device_class)  # восстанавливаем параметры из резервной копии
    sleep(120)
    print('Проверяем успешно ли прошел ребут бекапа сравнивая значения')
    for param in list_params:
        after_params[param] = t.get_param(f'{device_class}_{slot}_{param}')
        sleep(2)
    pprint(compare_dicts(before_params, after_params))


def all_params():
    """
    Метод, который производит ребут для всех параметров на устройстве
    """
    print('Создается резервная копия устройства')
    t.backup(slot, device_class)  # создаем резервную копию устройства
    sleep(10)
    view = input(f'Выводить все параметры? Введите 1, если да: ')
    all_name = t.get_param_backup_data(slot, device_class).keys()
    if view == '1':
        for param in all_name:
            print(f"Значение параметра {param}: {t.get_param(f'{device_class}_{slot}_{param}')}")
            sleep(2)
            before_params[param] = t.get_param(f'{device_class}_{slot}_{param}')
            sleep(1)
    else:
        for param in all_name:
            before_params[param] = t.get_param(f'{device_class}_{slot}_{param}')
            sleep(1)
    print('Создается резервная копия устройства')
    t.backup(slot, device_class)  # создаем резервную копию устройства
    sleep(20)
    print('Сбрасываем параметры устройства к значениям по умолчанию')
    t.set_param(ConfigReset.format(device_class, slot), '1')  # сбрасываем параметры устройства к значению по умолчанию
    sleep(20)
    print('Восстанавливаем резервную копию')
    t.get_param_backup_data_unparse(slot, device_class)  # восстанавливаем параметры из резервной копии
    sleep(150)
    print('Проверяем успешно ли прошел ребут бекапа сравнивая значения')
    for param in all_name:
        after_params[param] = t.get_param(f'{device_class}_{slot}_{param}')
        sleep(2)
    pprint(compare_dicts(before_params, after_params))


if __name__ == '__main__':
    IP = input('Введите IP шасси: ')  # Пример: 192.168.31.172
    device_class = input('Введите класс устройства: ')  # Пример: emstc1
    slot = input('Введите слот в котором находится устройство: ')  # Пример: 2
    print(f'Подключение к шасси {IP}')
    t = SessionAPI('s_ap', IP)  # Подключаемся к шасси
    sleep(2)
    print('Подключение прошло успешно')
    choice = input('Введите 1 для проверки отдельных параметров; 2 для всех: ')
    if choice == '1':
        separate_params()
    else:
        all_params()
    print('Выходим с шасси')
    t.logout()  # выходим с шасси
