from time import sleep
import re
import os
import logging
from EXFO.VIAVI import MTS5800
from base.Atlas.atlas import Facade
from Utilities.all import (ConfigReset,
                           LnNAdmStateSet,
                           ClNAdmStateSet,
                           LnNTxEn,
                           ClNTxEn,
                           ClNDRSet,
                           ClNLinkWSet,
                           main_source,
                           stm64,
                           OTU_2,
                           OTU_2e,
                           GE_10)

cur_path = os.path.dirname(__file__)
new_path = os.path.relpath('..\\traffics')

console_handler = logging.StreamHandler()

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
                    datefmt='%m.%d.%Y %H:%M:%S',
                    level=logging.INFO)

clients = ['2', '5', '7', '10']
traffics = ['4', '25', '26', '41']


def get_key(lists, value):
    """
    Метод возвращает номер основного источника ODUk (CL#.Link.W.Set)
    (возвращает ключ словаря)
    """
    for k, v in lists.items():
        if v == value:
            return str(k)


def setting_bert():
    """
    Метод настраивает BERT для теста.
    На выбранном порте закрывает открытое приложение, если оно есть;
    включает необходимый тест; включает лазер, трафик.
    """
    logging.info(f'Подключение к BERT по адресу [ {ip_bert} ]')
    mts = MTS5800(ip_bert, 8006)
    sleep(10)
    pick_traffic(testing_devcls, testing_slot, mts)


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
    for client in clients:
        logging.info(f'Перевод линии {client} в адм.режим IS')
        if t.get_param(LnNAdmStateSet.format(devcls, slot, client)) == '0':
            t.set_param(LnNAdmStateSet.format(devcls, slot, client), '1')
            sleep(5)
            t.set_param(LnNAdmStateSet.format(devcls, slot, client), '2')
            sleep(5)
        elif t.get_param(LnNAdmStateSet.format(devcls, slot, client)) == '1':
            t.set_param(LnNAdmStateSet.format(devcls, slot, client), '2')
            sleep(5)
        elif t.get_param(LnNAdmStateSet.format(devcls, slot, client)) == '2':
            pass
        logging.info(f'Перевод клиента {client} в адм.режим IS')
        if t.get_param(ClNAdmStateSet.format(devcls, slot, client)) == '0':
            t.set_param(ClNAdmStateSet.format(devcls, slot, client), '1')
            sleep(5)
            t.set_param(ClNAdmStateSet.format(devcls, slot, client), '2')
            sleep(5)
        elif t.get_param(ClNAdmStateSet.format(devcls, slot, client)) == '1':
            t.set_param(ClNAdmStateSet.format(devcls, slot, client), '2')
            sleep(5)
        elif t.get_param(ClNAdmStateSet.format(devcls, slot, client)) == '2':
            pass
        logging.info(f'Перевод линии {client} в состояние "Управляется ALS"')
        if t.get_param(LnNTxEn.format(devcls, slot, client)) == '0':
            t.set_param(LnNTxEn.format(devcls, slot, client), '1')
            sleep(10)
        elif t.get_param(LnNTxEn.format(devcls, slot, client)) == '1':
            pass
        logging.info(f'Перевод клиента {client} в состояние "Управляется ALS"')
        if t.get_param(ClNTxEn.format(devcls, slot, client)) == '0':
            t.set_param(ClNTxEn.format(devcls, slot, client), '1')
            sleep(10)
        elif t.get_param(ClNTxEn.format(devcls, slot, client)) == '1':
            pass


def pick_traffic(devcls, slot, mts):
    """
    Метод, в котором на используемых клиентах
    выставляется необходимый трафик и источник ODUk
    """
    for name_traffic in traffics:
        if name_traffic == '4':
            logging.info('Проверяется трафик STM64')
            for client in clients:
                logging.info(f'Выставляется тип трафика STM64 на клиенте {client}')
                if t.get_param(ClNDRSet.format(devcls, slot, client)) == '4':
                    pass
                else:
                    t.set_param(ClNDRSet.format(devcls, slot, client), '4')
                    sleep(5)
                logging.info(f'Выставляется основной источник ODUk на клиенте {client}')
                if t.get_param(ClNLinkWSet.format(devcls, slot, client)) == get_key(main_source, f'Ln{client}.ODU2'):
                    pass
                else:
                    t.set_param(ClNLinkWSet.format(devcls, slot, client), get_key(main_source, f'Ln{client}.ODU2'))
            check_app(mts, name_traffic)
        elif name_traffic == '25':
            logging.info('Проверяется трафик OTU2')
            for client in clients:
                logging.info(f'Выставляется тип трафика OTU2 на клиенте {client}')
                if t.get_param(ClNDRSet.format(devcls, slot, client)) == '25':
                    pass
                else:
                    t.set_param(ClNDRSet.format(devcls, slot, client), '25')
                    sleep(5)
                logging.info(f'Выставляется основной источник ODUk на клиенте {client}')
                if t.get_param(ClNLinkWSet.format(devcls, slot, client)) == get_key(main_source, f'Ln{client}.ODU2'):
                    pass
                else:
                    t.set_param(ClNLinkWSet.format(devcls, slot, client), get_key(main_source, f'Ln{client}.ODU2'))
            check_app(mts, name_traffic)
        elif name_traffic == '26':
            logging.info('Проверяется трафик OTU2e')
            for client in clients:
                logging.info(f'Выставляется тип трафика OTU2e на клиенте {client}')
                if t.get_param(ClNDRSet.format(devcls, slot, client)) == '26':
                    pass
                else:
                    t.set_param(ClNDRSet.format(devcls, slot, client), '26')
                    sleep(5)
                logging.info(f'Выставляется основной источник ODUk на клиенте {client}')
                if t.get_param(ClNLinkWSet.format(devcls, slot, client)) == get_key(main_source, f'Ln{client}.ODU2e'):
                    pass
                else:
                    t.set_param(ClNLinkWSet.format(devcls, slot, client), get_key(main_source, f'Ln{client}.ODU2e'))
            check_app(mts, name_traffic)
        elif name_traffic == '41':
            logging.info('Проверяется трафик 10GE')
            for client in clients:
                logging.info(f'Выставляется тип трафика 10GE на клиенте {client}')
                if t.get_param(ClNDRSet.format(devcls, slot, client)) == '41':
                    pass
                else:
                    t.set_param(ClNDRSet.format(devcls, slot, client), '41')
                    sleep(5)
                logging.info(f'Выставляется основной источник ODUk на клиенте {client}')
                if t.get_param(ClNLinkWSet.format(devcls, slot, client)) == get_key(main_source, f'Ln{client}.ODU2'):
                    pass
                else:
                    t.set_param(ClNLinkWSet.format(devcls, slot, client), get_key(main_source, f'Ln{client}.ODU2'))
            check_app(mts, name_traffic)


def check_app(mts, name_traffic):
    """
    Метод, который выставляет тип трафика;
    В зависимости от включенных приложенйи на BERTe
    запускает необходимый сценарий
    """
    if name_traffic == '4':
        traffic = stm64
    elif name_traffic == '25':
        traffic = OTU_2
    elif name_traffic == '26':
        traffic = OTU_2e
    elif name_traffic == '41':
        traffic = GE_10
    port = '10' + bert_port
    list_apps = mts._current_app()
    logging.info(f'На BERTe запущены следующие приложения {list_apps}')
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
            sleep(5)
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
        sleep(30)
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
    if traffic.decode() == 'TermOtn107Odu2Bert' or 'TermOtn111Odu2Bert':
        mts.send_command(b':SENSE:OTN:FEC NO')
        sleep(5)
    logging.info(f'Запускаем тест приложения {traffic.decode()}')
    mts.simple_restart_test(int(bert_port))
    sleep(10)
    if mts.simple_status_test(int(bert_port)):
        logging.info(f'Тест трафика {traffic.decode()} прошел успешно')
        pass
    else:
        logging.error(f'В тесте приложения {traffic.decode()} возникли ошибки')
        logging.info(f'Данные по всем параметрам будут выведены в файл [ "{traffic.decode()}_results.txt" ]')
        if_error(mts, traffic.decode())


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
