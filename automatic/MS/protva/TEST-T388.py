from time import sleep
import re
import os
import logging
from Utilities.all import (ConfigReset,
                           LnAllAdmStateSet,
                           ClAllAdmStateSet,
                           LnAllTxEn,
                           ClAllTxEn,
                           ClAllDRSet,
                           GE_10,
                           stm64)
from EXFO.VIAVI import MTS5800
from base.Atlas.atlas import Facade

cur_path = os.path.dirname(__file__)
new_path = os.path.relpath('..\\traffics')

console_handler = logging.StreamHandler()

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
                    datefmt='%m.%d.%Y %H:%M:%S',
                    level=logging.INFO)


def setting_device(devcls, slot):
    """
    Метод, который настраивает тестируемое устройство.
    Сбрасывает значения в дефолт.
    Перевод используемых линий и клиентов в режим IS.
    Устанавливает состояние передатчика клиента и линий в режим 'Управление ALS'.
    """
    logging.info('Сброс параметров к значению по умолчанию на тестируемом устройстве')
    t.set_param(ConfigReset.format(devcls, slot), '1')
    sleep(40)
    logging.info('Перевод всех линий в адм.режим IS')
    if t.get_param(LnAllAdmStateSet.format(devcls, slot)) == '0':
        t.set_param(LnAllAdmStateSet.format(devcls, slot), '1')
        sleep(10)
        t.set_param(LnAllAdmStateSet.format(devcls, slot), '2')
        sleep(10)
    elif t.get_param(LnAllAdmStateSet.format(devcls, slot)) == '1':
        t.set_param(LnAllAdmStateSet.format(devcls, slot), '2')
        sleep(10)
    elif t.get_param(LnAllAdmStateSet.format(devcls, slot)) == '2':
        pass
    logging.info('Перевод всех клиентов в адм.режим IS')
    if t.get_param(ClAllAdmStateSet.format(devcls, slot)) == '0':
        t.set_param(ClAllAdmStateSet.format(devcls, slot), '1')
        sleep(10)
        t.set_param(ClAllAdmStateSet.format(devcls, slot), '2')
        sleep(10)
    elif t.get_param(ClAllAdmStateSet.format(devcls, slot)) == '1':
        t.set_param(ClAllAdmStateSet.format(devcls, slot), '2')
        sleep(10)
    elif t.get_param(ClAllAdmStateSet.format(devcls, slot)) == '2':
        pass
    logging.info('Перевод всех линий в состояние "Управляется ALS"')
    if t.get_param(LnAllTxEn.format(devcls, slot)) == '0':
        t.set_param(LnAllTxEn.format(devcls, slot), '1')
        sleep(10)
    elif t.get_param(LnAllTxEn.format(devcls, slot)) == '1':
        pass
    logging.info('Перевод всех клиентов в состояние "Управляется ALS"')
    if t.get_param(ClAllTxEn.format(devcls, slot)) == '0':
        t.set_param(ClAllTxEn.format(devcls, slot), '1')
        sleep(10)
    elif t.get_param(ClAllTxEn.format(devcls, slot)) == '1':
        pass


def setting_bert():
    """
    Метод настраивает BERT для теста.
    На выбранном порте закрывает открытое приложение, если оно есть;
    включает необходимый тест; включает лазер, трафик.
    """
    logging.info(f'Подключение к BERT по адресу [ {ip_bert} ]')
    mts = MTS5800(ip_bert, 8006)
    sleep(10)
    check_app(mts)


def check_app(mts):
    """
    Метод, который выставляет тип трафика;
    В зависимости от включенных приложенйи на BERTe
    запускает необходимый сценарий
    """
    list_traffic = [GE_10, stm64]
    port = '10' + bert_port
    for traffic in list_traffic:
        list_apps = mts._current_app()
        logging.info(f'На BERTe запущены следующие приложения {list_apps}')
        if traffic == GE_10:
            logging.info('Выставление типа трафика на всех клиентах 10GE')
            if t.get_param(ClAllDRSet.format(testing_devcls, testing_slot)) == '255' or '4':
                t.set_param(ClAllDRSet.format(testing_devcls, testing_slot), '41')
                sleep(10)
            elif t.get_param(ClAllDRSet.format(testing_devcls, testing_slot)) == '41':
                pass
        elif traffic == stm64:
            logging.info('Выставление типа трафика на всех клиентах stm64')
            if t.get_param(ClAllDRSet.format(testing_devcls, testing_slot)) == '255' or '41':
                t.set_param(ClAllDRSet.format(testing_devcls, testing_slot), '4')
                sleep(10)
            elif t.get_param(ClAllDRSet.format(testing_devcls, testing_slot)) == '4':
                pass
        logging.info(f'Проверяется трафик {traffic.decode()}')
        found_app = None
        for app in list_apps:
            if port in app:
                found_app = app
                break
        if found_app is not None:
            if traffic.decode() in found_app:
                main_test(traffic, mts)
            else:
                logging.info(f'Выбираем приложение {found_app}')
                mts._select_app(int(bert_port))
                sleep(10)
                logging.info(f'Закрываем приложение {found_app}')
                mts._exit()
                sleep(30)
                logging.info(f'Запускаем приложение {traffic.decode()}')
                mts._launch_app(traffic, bert_port.encode())
                sleep(30)
                main_test(traffic, mts)
        else:
            logging.info(f'Создаем приложение {traffic.decode()}')
            mts._launch_app(traffic, bert_port.encode())
            sleep(40)
            main_test(traffic, mts)


def main_test(traffic, mts):
    """
    Метод, где выполняются команды BERTa
    универсальные для всех типов траффиков
    (Выбор приложения; создание и запуск сессии;включение лазера и
    трафика, если необходимо; запуск теста; вывод результатов)
    """
    logging.info(f'Выбираем приложение {traffic.decode()}')
    mts._select_app(int(bert_port))
    sleep(5)
    logging.info(f'Создаем сессию с приложением {traffic.decode()}')
    mts._app_session()
    sleep(5)
    logging.info(f'Включаем лазер на приложение {traffic.decode()} ')
    mts.simple_laser_ON(int(bert_port))
    sleep(2)
    if traffic.decode() == 'TermEth10GL2Traffic':
        logging.info(f'Включаем траффик на приложение {traffic.decode()} ')
        mts.send_command(b':SOURCE:MAC:TRAFFIC ON')
        sleep(5)
    logging.info(f'Запускаем тест приложения {traffic.decode()}')
    mts.simple_restart_test(int(bert_port))
    sleep(5)
    if mts.simple_status_test(int(bert_port)):
        logging.info(f'Тест трафика {traffic.decode()} прошел успешно')
        pass
    else:
        logging.error(f'В тесте приложения {traffic.decode()} возникли ошибки')
        logging.info(f'Данные по всем параметрам будут выведены в файл [ "{traffic.decode()}_results.txt" ]')
        if_error(mts, traffic.decode())


def if_error(mts, traffic):
    """
    Метод, который вызывается, если тест провалился.
    Он создает файл под названием results в папке с этим скриптом,
    где будут выведены все параметры
    """
    with open(f'{new_path}\\{traffic}.txt', 'r') as f:
        parameters = f.readlines()
    for parameter in parameters:
        if re.match(r'\[[%a-zA-Z]+', parameter) is not None:
            command = parameter.split('-')[1].strip()
            with open(f'{traffic}_results.txt', 'a') as file:
                file.write(f'{parameter.split("-")[0]}: {mts.simple_send_rc(command.encode())}\n')


if __name__ == '__main__':
    ip_shassi = input('Введите IP шасси: ')  # 192.168.31.196
    ip_bert = input('Введите IP berta: ')  # 192.168.31.237
    testing_slot = input('Введите слот, в котором находится тестируемое устройство: ')  # 4
    testing_devcls = input('Введите класс тестируемого устройства: ')  # tertc-7.3.0
    bert_port = input('Введите порт, который будет использоваться на BERTe: ')  # 2
    t = Facade('s_ap', ip_shassi)
    sleep(5)
    setting_device(testing_devcls, testing_slot)
    setting_bert()
    t.logout()
