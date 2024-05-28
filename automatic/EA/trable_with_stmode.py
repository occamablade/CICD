from time import sleep
import logging

from EXFO.anritsu import AnritsuMS9740B
from Utilities.all import ConfigReset, ChAll, WssAtt, StModeEA, AmplifierEA, GainSetEA, AdmStateEA, EAOutPowerSig, \
    StMode
from base.Atlas.atlas import SessionAPI


console_handler = logging.StreamHandler()

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
                    datefmt='%m.%d.%Y %H:%M:%S',
                    level=logging.INFO)


def get_value(dict, key):
    """
    Метод возвращает номер режима стабилизации
    """
    for k, v in dict.items():
        if k == key:
            return str(v)


def setting_roadm():
    """
    Метод настройки ROADMa
    """
    logging.info('Настройка ROADM')
    t.set_param(ConfigReset.format(roadm_devcls, roadm_slot), "1")  # сброс в дефолт
    sleep(15)
    t.set_param(ChAll.format(roadm_devcls, roadm_slot), "2")  # перевод всех каналов в ADD
    sleep(5)
    t.set_param(WssAtt.format(roadm_devcls, roadm_slot), "0")  # затухание на всех каналах 0
    sleep(5)
    for i in range(21, 61):
        t.set_param(f'{roadm_devcls}_{roadm_slot}_WSS.Ch{i}e.State.Set', "0")  # перевод канала в блок
        sleep(1)


def setting_noise():
    """
    Метод настройки источника шума (усилитель)
    """
    logging.info('Настройка источника шума')
    t.set_param(ConfigReset.format(noise_devcls, noise_slot), "1")  # сброс в дефолт
    sleep(15)
    t.set_param(StModeEA.format(noise_devcls, noise_slot, '1'), "1")  # включение режима gain
    sleep(5)
    t.set_param(AmplifierEA.format(noise_devcls, noise_slot, '1'), "1")  # включение усилителя
    sleep(10)
    t.set_param(GainSetEA.format(noise_devcls, noise_slot, '1'), "24")  # выставление коэф-та усиления 24
    sleep(5)


def setting_voa():
    """
    Метод настройки аттеньюатора
    """
    logging.info('Настройка аттеньюатора')
    t.set_param(ConfigReset.format(voa_devcls, voa_slot), "1")  # сброс в дефолт
    sleep(15)
    t.set_param(f'{voa_devcls}_{voa_slot}_VOA{voa_port}.AdmState.Set', "1")  # установка адм.состояния OOS-MT на используемом порте
    sleep(5)
    t.set_param(f'{voa_devcls}_{voa_slot}_VOA{voa_port}.Att.Set', "0")  # установка затухания на используемом порте 0
    sleep(5)


def setting_test_device():
    """
    Метод настройки исследуемого устройства
    """
    logging.info('Настройка тестируемого устройства')
    t.set_param(ConfigReset.format(testing_devcls, testing_slot), "1")  # сброс в дефолт
    sleep(15)
    t.set_param(AdmStateEA.format(testing_devcls, testing_slot, testing_cascade), "1")  # установка адм.состояния OOS-MT
    sleep(5)
    t.set_param(StModeEA.format(testing_devcls, testing_slot, testing_cascade), "1")  # включение режима gain
    sleep(5)


def start_test():
    """
    Начало теста
    """
    logging.info('Начало теста')
    v.send_command('SSI')
    sleep(3)
    if (t.get_param(EAOutPowerSig.format(testing_devcls, testing_slot, testing_cascade)) != '-50.0' and
            v.get_spectrum_power() != -999.99):
        #  трафик идет
        t.set_param(AdmStateEA.format(testing_devcls, testing_slot, testing_cascade),
                    "0")  # установка адм.состояния OOS
        sleep(10)
        v.send_command('SSI')
        sleep(3)
        if (t.get_param(EAOutPowerSig.format(testing_devcls, testing_slot, testing_cascade)) is None and
                v.get_spectrum_power() == -999.99):
            # трафик не идет
            t.set_param(AdmStateEA.format(testing_devcls, testing_slot, testing_cascade),
                        "1")  # установка адм.состояния OOS-МТ
            sleep(10)
            stmode = get_value(StMode, t.get_param(StModeEA.format(testing_devcls, testing_slot, testing_cascade)))
            if stmode != 'Выкл':
                # режим стабилизации не перешел в режим Выкл, проверяем что трафик не идет
                v.send_command('SSI')
                sleep(3)
                if (t.get_param(EAOutPowerSig.format(testing_devcls, testing_slot, testing_cascade)) == '-50.0' and
                        v.get_spectrum_power() == -999.99):
                    print(f'При переключение режимов на устройстве в порядке OOS-MT -> OOS -> OOS-MT:'
                          f'в параметре StMode отображается {stmode} вместо "Выкл"')


if __name__ == '__main__':
    IP_anritsu = '192.168.31.184'  # IP osa
    v = AnritsuMS9740B(ip=IP_anritsu)
    IP_shassi = '192.168.31.205'  # IP шасси
    testing_devcls = 'evstc-4.1.0'  # класс тестируемого устройства
    testing_slot = '2'  # слот тестируемого устройства
    testing_cascade = '1'  # какой каскад усилителя тестируется
    roadm_devcls = 'rmstc5'  # класс ROADMa
    roadm_slot = '5'  # слот ROADMa
    roadm_wss = 'ADD'  # куда приходит трафик с источника шума
    voa_devcls = 'vtutc-16.2.0'  # класс аттеньюатора
    voa_slot = '3'  # слот аттеньюатора
    voa_port = '1'  # какой порт используется на аттеньюаторе
    noise_devcls = 'evstc3'  # класс источника шума (усилитель)
    noise_slot = '1'  # слот источника шума (усилитель)
    t = SessionAPI('s_ap', IP_shassi)
    sleep(5)
    setting_roadm()
    setting_noise()
    setting_voa()
    setting_test_device()
    start_test()
    t.logout()
