from time import sleep

from base.Atlas.atlas import Facade
from Utilities.all import (
    ConfigReset,
    AdmStateEA,
    StModeEA,
    StModeChoises,
    GainEA,
    PowerSigEA,
    OutPowerEA,
)


def get_key(dict, value):
    """
    Метод возвращает номер режима стабилизации
    """
    for k, v in dict.items():
        if v == value:
            return str(k)


def setting_test(devcls, slot, cascade):
    """
    Метод, который устанавливает на тестируемом устройстве
    административное состояние IS, режим стабилизации GAIN.
    """
    print("Сбрасываем в дефолт")
    t.set_param(ConfigReset.format(devcls, slot), "1")
    sleep(10)
    print("Перевод адм.состояние в OOS-MT")
    t.set_param(AdmStateEA.format(devcls, slot, cascade), "1")
    sleep(5)
    print("Перевод адм.состояние в IS")
    t.set_param(AdmStateEA.format(devcls, slot, cascade), "2")
    sleep(5)
    print("Перевод режима стабилизации в Gain")
    t.set_param(StModeEA.format(devcls, slot, cascade), "1")
    sleep(5)


def get_param(devcls, slot, cascade):
    """
    Метод, который переключает режим стабилизации
    и печатает значения параметров PowerSig и Gain
    для каждого режима.
    """
    for i in StModeChoises.values():
        print(f"Устанавливается режим стабилизации {i}")
        t.set_param(StModeEA.format(devcls, slot, cascade), get_key(StModeChoises, i))
        sleep(10)
        if t.get_param(StModeEA.format(devcls, slot, cascade)) == i:
            sleep(3)
            pass
        else:
            print("Переход не прошел")
            t.logout()
        print(f"Значение параметра Out.Power при режиме {i}: {t.get_param(OutPowerEA.format(devcls, slot, cascade))}")
        sleep(3)
        print(f"Значение параметра Out.PowerSig при режиме {i}: {t.get_param(PowerSigEA.format(devcls, slot, cascade))} ")
        sleep(3)
        print(f"Значение параметра Gain при режиме {i}: {t.get_param(GainEA.format(devcls, slot, cascade))}")
        sleep(3)
        print("-" * 15)


if __name__ == "__main__":
    IP = input("Введите IP шасси: ")  # 192.168.31.205
    t = Facade("s_ap", str(IP))
    sleep(2)
    testing_dev = input("Введите класс тестируемого устройства: ")  # emstc-4.0.0
    testing_slot = input("Введите слот тестируемого устройства: ")  # 1
    testing_cascade = input("Введите каскад тестируемого устройства: ")  # 1
    setting_test(testing_dev, testing_slot, testing_cascade)
    sleep(2)
    get_param(testing_dev, testing_slot, testing_cascade)
    sleep(2)
    t.logout()
