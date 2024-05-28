from time import sleep
import re
from base.Atlas.atlas import Facade
from Utilities.all import (ConfigReset,
                           AdmStateLn,
                           AdmStateCl,
                           TxLn,
                           TxCl,
                           TypeTrafficCl,
                           LinkCl,)
from EXFO.VIAVI import MTS5800
from Utilities.all import main_source, stm1


def setting_line_client(devcls, slot, line, client):
    """
    Метод переводит административное
    состояние клиента и линии в состояние IS
    """
    t.set_param(AdmStateLn.format(devcls, slot, line), '1')
    sleep(5)
    t.set_param(AdmStateLn.format(devcls, slot, line), '2')
    sleep(5)
    t.set_param(AdmStateCl.format(devcls, slot, client), '1')
    sleep(5)
    t.set_param(AdmStateCl.format(devcls, slot, client), '2')
    sleep(5)
    t.set_param(TxLn.format(devcls, slot, line), '1')
    sleep(5)
    t.set_param(TxCl.format(devcls, slot, client), '1')
    sleep(5)


def get_key(lists, value):
    """
    Метод возвращает номер основного источника ODUk (CL#.Link.W.Set)
    """
    for k, v in lists.items():
        if v == value:
            return str(k)


def BERT_setting():
    """
    Метод подключает к BERTy
    и начинает тест
    """
    mts = MTS5800('192.168.31.237', 8006)
    sleep(10)
    print('Подключение к BERTy прошло успешно')
    check_app(mts._current_app(), mts)
    sleep(30)
    mts.close()


def if_error(mts):
    """
    Метод, который вызывается, если тест провалился.
    Он создает файл под названием results в папке с этим скриптом,
    где будут выведены все параметры
    """
    with open('stm1.txt', 'r') as f:
        parameters = f.readlines()
    for parameter in parameters:
        if re.match('^[%a-zA-Z]+', parameter) is not None:
            command = parameter.split('-')[1].strip()
            with open('results.txt', 'a') as file:
                file.write(f'{parameter.split("-")[0]}: {mts.send_rc(command.encode(),2)}')
    print(f'Результаты теста были сохранены в файл {file}')


def check_app(curapp, mts):
    """
    Метод, который начинает тест:
    закрывает открытое приложение/открывает нужное/запускает тест.
    в зависимости от результата теста:
    если тест не прошел - вызывается метод if_error;
    если тест прошел успешно - выведется сообщение;
    """
    found_app = None
    for app in curapp:
        if bert_port in app:
            found_app = app
            break
    if found_app is not None:
        print('Выбираем приложение, которое было запущено на нашем порту')
        mts._select_app(int(bport))
        sleep(3)
        print('Закрываем приложение, которое было запущено на нашем порту')
        mts._exit()
        sleep(20)
        print('Запускаем наше приложение')
        mts._launch_app(stm1, bport.encode())
        sleep(20)
        print('Выбираем наше приложение')
        mts._select_app(int(bport))
        sleep(3)
        print('Создаем сессию')
        mts._app_session()
        sleep(3)
        print('Включаем лазер')
        mts.simple_laser_ON(int(bport))
        sleep(2)
        print('Запускаем тест')
        mts.simple_restart_test(int(bport))
        sleep(5)
        print('Результаты: ')
        if mts.simple_status_test(int(bport)):
            print('Тест успешно завершен. Выходим с шасси, закрываем сессию с BERTом')
        else:
            print('Тест не прошел')
            if_error(mts)
            sleep(2)
    else:
        print(f'На порту {bport} нет запущенных приложений')
        print('Запускаем наше приложение')
        mts._launch_app(stm1, bport.encode())
        sleep(20)
        print('Выбираем наше приложение')
        mts._select_app(int(bport))
        sleep(3)
        print('Создаем сессию')
        mts._app_session()
        sleep(3)
        print('Включаем лазер')
        mts.simple_laser_ON(int(bport))
        sleep(2)
        print('Запускаем тест')
        mts.simple_restart_test(int(bport))
        sleep('Результаты: ')
        if mts.simple_status_test(int(bport)):
            print('Тест успешно завершен. Выходим с шасси, закрываем сессию с BERTом')
        else:
            print('Тест не прошел')
            if_error(mts)
            sleep(2)


def start_test(devcls, slot, client):
    """
    Метод выставляет тип траффика (STM-1),
    устанавливается основной источник ODUk,
    Подключается к BERT'y
    """
    print(f'Выставляется тип траффика')
    t.set_param(TypeTrafficCl.format(devcls, slot, client), '1')
    sleep(10)
    print(f'Выставляется основной источник ODUk')
    t.set_param(LinkCl.format(devcls, slot, client), get_key(main_source, f'Ln{testing_line}.ODU0.TS1'))
    sleep(10)
    print(f'Подключение к BERTy')
    BERT_setting()


if __name__ == '__main__':
    IP = input('Введите IP шасси: ')  # 192.168.31.199
    t = Facade('s_ap', str(IP))
    sleep(2)
    testing_slot = input('Введите слот в котором находится проверяемое устройство: ')  # 12
    testing_devcls = input('Введите класс проверяемого устройства: ')  # mcbtc-5.0.0
    bport = input('Введите используемый порт на BERT: ')  # 2
    bert_port = str(10) + bport
    testing_line = input('Введите используемую линию: ')  # 1
    testing_client = input('Введите используемого клиента: ')  # 1
    print(f'Сбрасываем параметры на тестируемом устройстве')
    t.set_param(ConfigReset.format(testing_devcls, testing_slot), '1')
    sleep(10)
    print(f'Настраиваем тестируемое устройство')
    setting_line_client(testing_devcls, testing_slot, testing_line, testing_client)
    sleep(2)
    start_test(testing_devcls, testing_slot, testing_client)
    sleep(2)
    t.logout()
