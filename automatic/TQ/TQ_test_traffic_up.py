import logging
import random
from time import sleep
from base.Atlas.atlas import Facade
from Utilities.all import (ConfigReset,
                           SlotNEnable,
                           LnNTxEn,
                           ClNTxEn,
                           ClNDRSet,
                           force_ODU2,
                           traffic_TQ,
                           AdmStateLn,
                           AdmStateCl)
from EXFO.VIAVI import MTS5800
from Utilities.all import stm64, GE_10


console_handler = logging.StreamHandler()

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
                    datefmt='%m.%d.%Y %H:%M:%S',
                    level=logging.INFO)


res = {}
list_uncorrect_test = []


def get_value(lists, key):
    """
    Метод, который возвращает value из словаря по ключу
    """
    for k, v in lists.items():
        if k == key:
            return str(v)


def made_slot_enable():
    """
    Метод, который перезагружает устройство через ЦУ
    и делает сброс значений параметров в дефолт
    """
    logging.info(f'Перезагрузка устройства в слоте {testing_slot}')
    t.set_param(SlotNEnable.format(CU_devcls, CU_slot, testing_slot), '0')
    sleep(20)
    t.set_param(SlotNEnable.format(CU_devcls, CU_slot, testing_slot), '2')
    sleep(60)
    logging.info(f'Сбрасываем параметры на тестируемом устройстве {testing_slot}')
    t.set_param(ConfigReset.format(testing_devcls, testing_slot), '1')
    sleep(20)


def made_ln_tx():
    """
    Метод, который включает передатчики на всех линиях
    """
    for i in range(1, 5):
        logging.info(f'Перевод в OOS-MT линию {i}')
        t.set_param(AdmStateLn.format(testing_devcls, testing_slot, str(i)), '1')
        sleep(3)
        logging.info(f'Включает передатчик на линии {i}')
        t.set_param(LnNTxEn.format(testing_devcls, testing_slot, str(i)), '1')
        sleep(3)


def made_cl_tx(traffic):
    """
    Метод, который включает передатчики на всех клиентах и выставляет трафик
    """
    for port in client_ports:
        logging.info(f'Перевод в OOS-MT клиента {port}')
        t.set_param(AdmStateCl.format(testing_devcls, testing_slot, str(port)), '1')
        sleep(3)
        logging.info(f'Включает передатчик на клиенте {port}')
        t.set_param(ClNTxEn.format(testing_devcls, testing_slot, str(port)), '1')
        sleep(5)
        logging.info(f'Включает трафик {get_value(traffic_TQ , traffic)} на клиенте {port}')
        t.set_param(ClNDRSet.format(testing_devcls, testing_slot, str(port)), str(traffic))
        sleep(5)


def random_comm():
    """
    Метод, который рандомно выставляет коммутации линейных
    и клиентских интерфейсов
    """
    list_shema = []
    list_shema.clear()
    list_variables = [768, 66304, 131840, 197376]
    random1 = random.choice(list_variables)
    logging.info(f'Ln1 - {get_value(force_ODU2, str(random1))}')
    list_variables.remove(random1)
    random2 = random.choice(list_variables)
    logging.info(f'Ln2 - {get_value(force_ODU2, str(random2))}')
    list_variables.remove(random2)
    random3 = random.choice(list_variables)
    logging.info(f'Ln3 - {get_value(force_ODU2, str(random3))}')
    list_variables.remove(random3)
    random4 = random.choice(list_variables)
    logging.info(f'Ln4 - {get_value(force_ODU2, str(random4))}')
    list_variables.remove(random4)
    t.set_param('{}_{}_Ln1.ODU2.Link.Set'.format(testing_devcls, testing_slot), str(random1))
    sleep(3)
    t.set_param('{}_{}_Ln2.ODU2.Link.Set'.format(testing_devcls, testing_slot), str(random2))
    sleep(3)
    t.set_param('{}_{}_Ln3.ODU2.Link.Set'.format(testing_devcls, testing_slot), str(random3))
    sleep(3)
    t.set_param('{}_{}_Ln4.ODU2.Link.Set'.format(testing_devcls, testing_slot), str(random4))
    sleep(3)
    list_variables.append(768)
    list_variables.append(66304)
    list_variables.append(131840)
    list_variables.append(197376)
    list_shema.append(random1)
    list_shema.append(random2)
    list_shema.append(random3)
    list_shema.append(random4)
    return list_shema


def start_traffic_and_result(i):
    """
    Метод, который запускает трафик на BERTе и смотрит результат
    """
    mts = MTS5800(IP_ber, 8006)

    if which_port_used_ber is not None:
        logging.info(f'Выбираем порт {which_port_used_ber}/создаем сессию/включаем лазер')
        mts._select_app(int(which_port_used_ber))
        sleep(5)
        mts._app_session()
        sleep(5)
        mts.simple_laser_ON(int(which_port_used_ber))
        sleep(2)
        if choice_type_traffic == GE_10:
            logging.info('Включаем траффик')
            mts.send_command(b':SOURCE:MAC:TRAFFIC ON')
            sleep(5)
        logging.info(f'Запускаем тест приложения {choice_type_traffic}')
        mts.simple_restart_test(int(which_port_used_ber))
        sleep(5)
        if mts.simple_status_test(int(which_port_used_ber)):
            logging.info(f'Тест трафика {choice_type_traffic} прошел успешно')
        else:
            result(i, which_port_used_ber)
    else:
        for port in range(1, int(count_used_ber_port) + 1):
            logging.info(f'Выбираем порт {port}/создаем сессию/включаем лазер')
            mts._select_app(int(port))
            sleep(5)
            mts._app_session()
            sleep(5)
            mts.simple_laser_ON(int(port))
            sleep(2)
            if choice_type_traffic == GE_10:
                logging.info('Включаем траффик')
                mts.send_command(b':SOURCE:MAC:TRAFFIC ON')
                sleep(5)
            logging.info(f'Запускаем тест приложения {choice_type_traffic}')
            mts.simple_restart_test(int(port))
            sleep(5)
            if mts.simple_status_test(int(port)):
                logging.info(f'Тест трафика {choice_type_traffic} прошел успешно')
            else:
                result(i, port)


def setting_ber(count, traffic, port_used_ber):
    """
    Метод, который настраивает BERT:
    Подключение/выставление выбранного пользователем типа трафика на порте(-ах)
    """
    mts = MTS5800(IP_ber, 8006)
    sleep(5)
    list_apps = mts._current_app()
    logging.info(f'На BERTe запущены следующие приложения {list_apps}')
    found_port = None
    if count == 1:
        for app in list_apps:
            if '_10' + port_used_ber in app:
                found_port = app
                break
        if found_port is not None:
            if traffic.decode() in found_port:
                pass
            else:
                logging.info(f'Выбираем приложение запущенное на {port_used_ber}ом порту')
                mts._select_app(int(port_used_ber))
                sleep(10)
                logging.info(f'Закрываем приложение запущенное на {port_used_ber}ом порту')
                mts._exit()
                sleep(30)
                logging.info(f'Запускаем приложение {traffic}')
                mts._launch_app(traffic, str(port_used_ber).encode())
                sleep(40)
        else:
            logging.info(f'Создаем приложение {traffic.decode()}')
            mts._launch_app(traffic, str(port_used_ber).encode())
            sleep(40)
    elif count == 2:
        for port in range(1, count + 1):
            logging.info(f'Выбираем приложение запущенное на {port}ом порту')
            mts._select_app(port)
            sleep(10)
            logging.info(f'Закрываем приложение запущенное на {port}ом порту')
            mts._exit()
            sleep(30)
            logging.info(f'Запускаем приложение {traffic}')
            mts._launch_app(traffic, str(port).encode())
            sleep(30)


def main_test(traffic, iteration):
    """
    Метод, который производит сам тест
    """
    for i in range(1, iteration + 1):
        if traffic == b'TermEth10GL2Traffic':
            traffic_choices = ['41', '42']
        elif traffic == b'TermStm64Au3Vc3Bert':
            traffic_choices = ['4']
        traffic_choice = random.choice(traffic_choices)
        logging.info('--------------------')
        logging.info(f'Номер итерации {i}')
        made_slot_enable()  # перезагрузка ЦУ и сброс параметров в дефолт
        made_ln_tx()  # включение состояния передатчика на всех линиях
        random_comm()  # рандомное выставление коммутаций линейных и клиентских портов
        made_cl_tx(traffic_choice)  # включает передатчики и устанавливает тип трафика на всех клиентах
        start_traffic_and_result(i)
    print('Тестируемый трафик: {}'.format(traffic_str))
    print('Циклов в тесте: {}'.format(iteration))
    print('Клиентские порты: {}'.format(client_ports))
    print('Количество неустановок трафика: {}'.format(len(list_uncorrect_test)))
    print(res)


def result(i, port):
    """
    Метод, который при провале теста заполняет словарь со схемой подключения
    и суммирует количество неудачных тестов
    """
    if choice_type_traffic == GE_10:
        if count_used_ber_port == '2':
            res[f'i={i}, порт {str(port)}'] = (
                f'Тип трафика: {get_value(traffic_TQ, str(t.get_param("{}_{}_Cl{}.DR.Set".format(testing_devcls, testing_slot, client_port_1))))}. '
                f'Cl{client_port_1} - {get_value(force_ODU2, str(t.get_param("{}_{}_Cl{}.Link.W.Set".format(testing_devcls, testing_slot, client_port_1))))}, '
                f'Cl{client_port_2} - {get_value(force_ODU2, str(t.get_param("{}_{}_Cl{}.Link.W.Set".format(testing_devcls, testing_slot, client_port_2))))}')
        elif count_used_ber_port == '1':
            res[f'i={i}, порт {str(port)}'] = (
                f'Тип трафика: {get_value(traffic_TQ, str(t.get_param("{}_{}_Cl{}.DR.Set".format(testing_devcls, testing_slot, client_port_1))))}. '
                f'Cl{client_port_1} - {get_value(force_ODU2, str(t.get_param("{}_{}_Cl{}.Link.W.Set".format(testing_devcls, testing_slot, client_port_1))))}')
    else:
        if count_used_ber_port == '2':
            res[f'i={i}, порт {str(port)}'] = (
                f'Cl{client_port_1} - {get_value(force_ODU2, str(t.get_param("{}_{}_Cl{}.Link.W.Set".format(testing_devcls, testing_slot, client_port_1))))}, '
                f'Cl{client_port_2} - {get_value(force_ODU2, str(t.get_param("{}_{}_Cl{}.Link.W.Set".format(testing_devcls, testing_slot, client_port_2))))}')
        elif count_used_ber_port == '1':
            res[f'i={i}, порт {str(port)}'] = (
                f'Cl{client_port_1} - {get_value(force_ODU2, str(t.get_param("{}_{}_Cl{}.Link.W.Set".format(testing_devcls, testing_slot, client_port_1))))}')
    if f'i={i}, порт 1' and f'i={i}, порт 2' in res.keys():
        if 'None' in res.get(f'i={i}, порт 1') and 'None' in res.get(f'i={i}, порт 2'):
            input('На обоих портах не прошел тест. Тест приостановлен. Для продолжения введите любой символ: ')
    list_uncorrect_test.append(i)


if __name__ == '__main__':
    IP = '192.168.31.205'  # IP Шасси
    IP_ber = '192.168.31.237'  # IP BERTa
    t = Facade('s_ap', str(IP))
    sleep(2)

    which_port_used_ber = None
    client_port_1 = None
    client_port_2 = None
    client_ports = []

    count_used_ber_port = '1'  # сколько используется BER-портов (от 1 до 2)

    if count_used_ber_port == '1':
        which_port_used_ber = '2'  # Какой порт используется на BERTe?
        client_port_1 = '3'  # В какой порт направлен трафик из используемого порта BERTa?
        client_ports.append(client_port_1)

    elif count_used_ber_port == '2':
        client_port_1 = '2'  # В какой порт направлен трафик из 1го порта BERTa?
        client_ports.append(client_port_1)
        client_port_2 = '3'  # В какой порт направлен трафик из 2го порта BERTa?
        client_ports.append(client_port_2)

    choice_type_traffic = '10GE'  # Какой трафик будет тестироваться (10GE или STM-64)
    traffic_str = choice_type_traffic
    if choice_type_traffic == '10GE':
        choice_type_traffic = GE_10
    elif choice_type_traffic == 'STM-64':
        choice_type_traffic = stm64

    count_iter = 5  # сколько будет повторений теста

    setting_ber(int(count_used_ber_port), choice_type_traffic, which_port_used_ber)
    testing_slot = '11'  # слот, в котором находится тестируемое устройство
    testing_devcls = 'sut-1.0.0'  # класс тестируемого устройства
    CU_devcls = 'dnepr2'  # класс ЦУ
    CU_slot = '14'  # слот, в котором находится ЦУ (писать только число, без ".CU")
    main_test(choice_type_traffic, count_iter)
    t.logout()
