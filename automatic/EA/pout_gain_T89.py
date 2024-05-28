import re
from time import sleep

from base.Atlas.atlas import SessionAPI
from Utilities.all import (ConfigReset, AdmStateEA, AmplifierEA, ChAll, Default, WssAtt, StModeEA,
                           VOAOutPortState, VOAAdmState, VoaChAdmStateSet, StModeSet, EASt1GainWMax, EASt1GainWMin,
                           EAGainWMax, EAGainWMin, VOAAttSetHMax, VOAAttSetHMin, ChAttSetHMax, ChAttSetHMin,
                           VOAPortAttWMax, VOAPortAttWMin, VOAPortAttSet, VOAAttSet, ChAttSet, PowerSigEA, GainSetEA,
                           EAOutPowerSigSetHMax, EAOutPowerSigSetHMin, EAStPoutFWMax, EAStPoutFWMin, EASt1GainSet,
                           EASt1PoutSet, PowerSigSetEA)
import logging

logger = logging.getLogger(__name__)


def average_pout():
    """
    Метод, который возвращает средний POUT усилителя
    """
    if t.get_param(EAOutPowerSigSetHMax.format(testing_devcls, testing_slot, testing_cascade)) != 'Ключ не найден':
        min_pout = t.get_param(EAOutPowerSigSetHMin.format(testing_devcls, testing_slot, testing_cascade))
        max_pout = t.get_param(EAOutPowerSigSetHMax.format(testing_devcls, testing_slot, testing_cascade))
        avg_pout: float = ((float(max_pout) + float(min_pout)) // 2)
    elif t.get_param(EAStPoutFWMax.format(testing_devcls, testing_slot, testing_cascade)) != 'Ключ не найден':
        min_pout = t.get_param(EAStPoutFWMax.format(testing_devcls, testing_slot, testing_cascade))
        max_pout = t.get_param(EAStPoutFWMin.format(testing_devcls, testing_slot, testing_cascade))
        avg_pout: float = ((float(max_pout) + float(min_pout)) // 2)
    return avg_pout


def average_gain():
    """
    Метод, который возвращает средний GAIN усилителя
    """
    if t.get_param(EASt1GainWMax.format(testing_devcls, testing_slot, testing_cascade)) != 'Ключ не найден':
        min_gain = t.get_param(EASt1GainWMin.format(testing_devcls, testing_slot, testing_cascade))
        max_gain = t.get_param(EASt1GainWMax.format(testing_devcls, testing_slot, testing_cascade))
        avg_gain: float = ((float(max_gain) + float(min_gain)) // 2)
    elif t.get_param(EAGainWMax.format(testing_devcls, testing_slot, testing_cascade)) != 'Ключ не найден':
        min_gain = t.get_param(EAGainWMax.format(testing_devcls, testing_slot, testing_cascade))
        max_gain = t.get_param(EAGainWMin.format(testing_devcls, testing_slot, testing_cascade))
        avg_gain: float = ((float(max_gain) + float(min_gain)) // 2)
    return avg_gain


def check_noise(devcls, slot, amount):
    """
    Метод, который настраивает источник шума (усилитель) для работы теста.
    Сбрасывает параметры к значению по умолчанию, затем переводит
    каскад(-ы) в адм.состояние IS.
    """
    print('-'*15)
    print('Сброс параметров в дефолт на источнике шума')
    if t.get_param(ConfigReset.format(devcls, slot)) != 'Ключ не найден':
        sleep(2)
        t.set_param(ConfigReset.format(devcls, slot), '1')
        sleep(15)
    elif t.get_param(Default.format(devcls, slot)) != 'Ключ не найден':
        sleep(2)
        t.set_param(Default.format(devcls, slot), '1')
        sleep(15)
    print('Перевод в IS и Gain источника шума')
    if t.get_param(StModeSet.format(devcls, slot, amount)) != 'Ключ не найден':
        sleep(5)
        t.set_param(StModeSet.format(devcls, slot, amount), '1')
        sleep(10)
    elif t.get_param(AdmStateEA.format(devcls, slot, amount)) != 'Ключ не найден':
        sleep(2)
        for i in range(1, int(amount) + 1):
            t.set_param(AdmStateEA.format(devcls, slot, i), '1')
            sleep(3)
            t.set_param(AdmStateEA.format(devcls, slot, i), '2')
            sleep(3)
            t.set_param(StModeEA.format(devcls, slot, i), '1')
            sleep(3)
            if t.get_param(AmplifierEA.format(devcls, slot, i)) != 'Ключ не найден':
                sleep(2)
                t.set_param(AmplifierEA.format(devcls, slot, i), '1')
                sleep(3)
    print('-' * 15)


def check_roadm(devcls, slot, ch):
    """
    Метод, который настраивает ROADM для работы теста.
    Сбрасывает параметры в дефолт.
    Выставляет состояние портов всех каналов.
    Выставляет значение затухания на всех каналах = 0.
    """
    print('-' * 15)
    print('Сброс параметров в дефолт на ROADMe')
    t.set_param(ConfigReset.format(devcls, slot), '1')
    sleep(10)
    if ch.upper() == 'ADD':
        wss = '2'
    elif re.search(r'ADD\d', ch.upper()):
        wss = ch.replace('ADD', '')
    else:
        return 'Ошибка в параметре WSS.ChAll.State.Set'
    print('Установка состояния портов')
    t.set_param(ChAll.format(devcls, slot), '0')
    sleep(3)
    t.set_param(ChAll.format(devcls, slot), wss)
    sleep(3)
    print('Установка затухания на всех каналах = 0')
    t.set_param(WssAtt.format(devcls, slot), '0')
    sleep(3)
    print('-' * 15)


def check_voa(devcls, slot, port):
    """
    Метод, который настраивает аттеньюатор для работы теста.
    Сбрасывает параметры в дефолт.
    Переводит в IS.
    """
    print('-' * 15)
    print('Сброс параметров в дефолт на аттеньюаторе')
    if t.get_param(Default.format(devcls, slot)) == '0':
        sleep(2)
        logger.info('Сброс настроек')
        t.set_param(Default.format(devcls, slot), '1')
        sleep(3)
        logger.info('Сброс настроек прошел успешно')
    elif t.get_param(ConfigReset.format(devcls, slot)) == '0':
        sleep(2)
        logger.info('Сброс настроек')
        t.set_param(ConfigReset.format(devcls, slot), '1')
        sleep(5)
        logger.info('Сброс настроек прошел успешно')
    print('Установка адм.состояния IS на аттеньюаторе')
    if t.get_param(VOAOutPortState.format(devcls, slot, port)) != 'Ключ не найден':
        sleep(2)
        logger.info('Переведение адм.состояния в режим IS')
        t.set_param(VOAOutPortState.format(devcls, slot, port), '1')
        sleep(3)
        t.set_param(VOAOutPortState.format(devcls, slot, port), '2')
        sleep(3)
        logger.info('Переведение адм.состояния в режим IS прошел успешно')
    elif t.get_param(VOAAdmState.format(devcls, slot, port)) != 'Ключ не найден':
        sleep(2)
        logger.info('Переведение адм.состояния в режим IS')
        t.set_param(VOAAdmState.format(devcls, slot, port), '1')
        sleep(3)
        t.set_param(VOAAdmState.format(devcls, slot, port), '2')
        sleep(3)
        logger.info('Переведение адм.состояния в режим IS прошел успешно')
    elif t.get_param(VoaChAdmStateSet.format(devcls, slot, port)) != 'Ключ не найден':
        sleep(2)
        logger.info('Переведение адм.состояния в режим IS')
        t.set_param(VoaChAdmStateSet.format(devcls, slot, port), '1')
        sleep(3)
        t.set_param(VoaChAdmStateSet.format(devcls, slot, port), '2')
        sleep(3)
        logger.info('Переведение адм.состояния в режим IS прошел успешно')
    print('Установка затухания 0')
    if t.get_param(VOAPortAttSet.format(att_devcls, att_slot, att_port)) != 'Ключ не найден':
        t.set_param(VOAPortAttSet.format(att_devcls, att_slot, att_port), '0')
        sleep(10)
    elif t.get_param(VOAAttSet.format(att_devcls, att_slot, att_port)) != 'Ключ не найден':
        t.set_param(VOAAttSet.format(att_devcls, att_slot, att_port), '0')
        sleep(10)
    elif t.get_param(ChAttSet.format(att_devcls, att_slot, att_port)) != 'Ключ не найден':
        t.set_param(ChAttSet.format(att_devcls, att_slot, att_port), '0')
        sleep(10)
    print('-' * 15)


def check_test(devcls, slot, amount):
    """
    Метод, который настраивает исследуемое устройство для работы теста.
    Сбрасывает параметры в дефолт.
    Переводит в IS.
    Переводит в Gain.
    """
    print('-'*15)
    print('Сброс параметров в дефолт на тестируемом устройстве')
    if t.get_param(ConfigReset.format(devcls, slot)) != 'Ключ не найден':
        sleep(2)
        t.set_param(ConfigReset.format(devcls, slot), '1')
        sleep(15)
    elif t.get_param(Default.format(devcls, slot)) != 'Ключ не найден':
        sleep(2)
        t.set_param(Default.format(devcls, slot), '1')
        sleep(15)
    print('Перевод в IS и Gain тестируемое устройство')
    if t.get_param(StModeSet.format(devcls, slot, amount)) != 'Ключ не найден':
        sleep(2)
        t.set_param(StModeSet.format(devcls, slot, amount), '1')
        sleep(10)
    elif t.get_param(AdmStateEA.format(devcls, slot, amount)) != 'Ключ не найден':
        sleep(2)
        for i in range(1, int(amount) + 1):
            t.set_param(AdmStateEA.format(devcls, slot, i), '1')
            sleep(5)
            t.set_param(AdmStateEA.format(devcls, slot, i), '2')
            sleep(5)
            t.set_param(StModeEA.format(devcls, slot, i), '1')
            sleep(5)
            if t.get_param(AmplifierEA.format(devcls, slot, i)) != 'Ключ не найден':
                sleep(2)
                t.set_param(AmplifierEA.format(devcls, slot, i), '1')
                sleep(5)
    print('-' * 15)


def get_list_att(devcls, slot, port):
    """
    Метод, который создает список со значением затуханий
    """
    print('Создается список со значениями аттеньюации')
    if t.get_param(VOAAttSetHMax.format(devcls, slot, port)) != 'Ключ не найден':
        sleep(2)
        min = t.get_param(VOAAttSetHMin.format(devcls, slot, port))  # минимально допустимое значение аттеньютации
        max = t.get_param(VOAAttSetHMax.format(devcls, slot, port))  # максимально допустимое значение аттеньютации
    elif t.get_param(ChAttSetHMax.format(devcls, slot, port)) != 'Ключ не найден':
        sleep(2)
        min = t.get_param(ChAttSetHMin.format(devcls, slot, port))  # минимально допустимое значение аттеньютации
        max = t.get_param(ChAttSetHMax.format(devcls, slot, port))  # максимально допустимое значение аттеньютации
    elif t.get_param(VOAPortAttWMax.format(devcls, slot, port)) != 'Ключ не найден':
        sleep(2)
        min = t.get_param(VOAPortAttWMin.format(devcls, slot, port))  # минимально допустимое значение аттеньютации
        max = t.get_param(VOAPortAttWMax.format(devcls, slot, port))  # максимально допустимое значение аттеньютации
    list_att = []
    if float(min) == 0:
        for i in range(int(float(max)) - 1):
            list_att.append(i)
    else:
        for i in range(1, int(float(max)) + 1):
            list_att.append(i)
    return list_att


def gain_pout(list_att):
    """
    Метод, который проводит тест и выписывате результаты в отдельный файл
    """
    if t.get_param(VOAPortAttSet.format(att_devcls, att_slot, att_port)) != 'Ключ не найден':
        voa = VOAPortAttSet
    elif t.get_param(VOAAttSet.format(att_devcls, att_slot, att_port)) != 'Ключ не найден':
        voa = VOAAttSet
    elif t.get_param(ChAttSet.format(att_devcls, att_slot, att_port)) != 'Ключ не найден':
        voa = ChAttSet
    if t.get_param(StModeSet.format(testing_devcls, testing_slot, testing_cascade)) != 'Ключ не найден':
        mode = StModeSet
        gain = EASt1GainSet
        pout = EASt1PoutSet
    elif t.get_param(StModeEA.format(testing_devcls, testing_slot, testing_cascade)) != 'Ключ не найден':
        mode = StModeEA
        gain = GainSetEA
        pout = PowerSigSetEA
    for j in range(1, 3):
        t.set_param(mode.format(testing_devcls, testing_slot, testing_cascade), str(j))
        sleep(15)
        if j == 1:
            print('Проверяем режим Gain')
            print('Выставляем среднее значение коэффициента усиления')
            t.set_param(gain.format(testing_devcls, testing_slot, testing_cascade), str(average_gain()))
            sleep(10)
        elif j == 2:
            print('Проверяем режим Pout')
            print('Выставляем среднее значение выходной мощности')
            t.set_param(pout.format(testing_devcls, testing_slot, testing_cascade), str(average_pout()))
            sleep(10)
        for i in list_att:
            att = i
            PowerOut1 = t.get_param(PowerSigEA.format(testing_devcls, testing_slot, testing_cascade))
            t.set_param(voa.format(att_devcls, att_slot, att_port), f'{att + 1}')
            sleep(20)
            PowerOut2 = t.get_param(PowerSigEA.format(testing_devcls, testing_slot, testing_cascade))
            with open('results.txt', 'a')as file:
                file.write('\n---------')
                file.write(f'\nЗначение затухания на аттеньюаторе  равно {att}')
                file.write(f'\nЗначение выходной мощности при значении аттеньюации {att} равно {PowerOut1}')
                file.write(f'\nВыставляем значение затухания на аттеньюаторе {att + 1}')
                if t.get_param(mode.format(testing_devcls, testing_slot, testing_cascade)) == '1':
                    file.write(f'\nПри изменении затухания с {att} до {att + 1}')
                    file.write(f'\nВыходная мощность должна была измениться с {PowerOut1} до {float(PowerOut1) - 1}')
                    file.write(f'\nВыходная мощность равна: {PowerOut2}')
                    file.write(f'\nРазница составляет: {float(PowerOut1) - float(PowerOut2)}')
                elif t.get_param(mode.format(testing_devcls, testing_slot, testing_cascade)) == '2':
                    file.write(f'\nПри изменении затухания с {att} до {att + 1}')
                    file.write(f'\nВыходная мощность должна была остаться неизменной, то есть {PowerOut1}')
                    file.write(f'\nВыходная мощность равна: {PowerOut2}')
                    file.write(f'\nРазница составляет: {float(PowerOut1) - float(PowerOut2)}')


if __name__ == '__main__':
    #  Подключаемся к шасси
    ip = input('Введите IP шасси: ')  # 192.168.31.205
    print(f'Подключаемся к шасси {ip}')
    t = SessionAPI('s_ap', ip)
    sleep(2)
    # введите слот и класс проверяемого устройства
    testing_slot = input('Введите слот в котором находится проверяемое устройство: ')  # 6
    testing_devcls = input('Введите класс проверяемого устройства: ')  # emstc-4.0.2
    testing_cascade = 2  # количество каскадов на исследуемом устройстве
    # введите слот и класс аттеньюатора
    att_slot = input('Введите слот в котором находится аттеньюатор: ')  # 3
    att_devcls = input('Введите класс аттеньюатора: ')  # vtsgs7
    att_port = input('Введите используемый порт на аттеньюаторе')  # 1
    # введите стол и класс ROADM
    roadm_slot = input('Введите слот в котором находится ROADM: ')  # 5
    roadm_devcls = input('Введите класс ROADM: ')  # rmstc5
    roadm_ch = input('Введите параметр через который будут выводится все каналы: ')  # ADD
    # введите стол и класс источника шума
    noise_slot = input('Введите слот в котором находится источник шума: ')  # 4
    noise_devcls = input('Введите класс источника шума: ')  # evs12
    amount_cascade = input('Введите количество каскадов на источнике шума: ')  # 1
    print('Настраиваем источник шума')
    check_noise(noise_devcls, noise_slot, amount_cascade)
    print('Настраиваем ROADM')
    check_roadm(roadm_devcls, roadm_slot, roadm_ch)
    print('Настраиваем аттеньюатор')
    check_voa(att_devcls, att_slot, att_port)
    print('Настраиваем исследуемое устройство')
    check_test(testing_devcls, testing_slot, testing_cascade)
    gain_pout(get_list_att(att_devcls, att_slot, att_port))
    print('Выходим с шасси')
    t.logout()
