import logging
import warnings
from dataclasses import dataclass

import pyvisa
from pyvisa.errors import VisaIOError
from pyvisa.resources import TCPIPInstrument

from base.Exception import ErrorRemoteConnection

logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore')


@dataclass
class AnritsuMS9740BSCPICommands:
    _idn: str = '*IDN?'  # Индентификатор устройства
    _err: str = 'ERR?'  # Состояние последней команды, 0 - это ок
    _get_cnt: str = 'CNT?'  # Значение центральной частоты
    _set_cnt: str = 'CNT {}'  # Установить новое значение центральной частоты
    _get_span: str = 'SPN?'  # Значение интервала
    _set_span: str = 'SPN {}'  # Установить новое значение интервала
    _get_start_wave: str = 'STA?'  # Получить начало измеряемого диапазона
    _set_start_wave: str = 'STA {}'  # Установить начало измеряемого диапазона
    _get_stop_wave: str = 'STO?'  # Получить конец измеряемого диапазона
    _set_stop_wave: str = 'STO {}'  # Установить конец измеряемого диапазона
    _get_res: str = 'RES?'  # Получить текущее разрешение
    _set_res: str = 'RES {}'  # Установить разрешение
    _get_vbw: str = 'VBW?'  # Получить ширину диапазона
    _set_vbw: str = 'VBW {}'  # Установить ширину диапазона
    _reset: str = '*RST'  # Перезагрузка
    _ssi: str = 'SSI'  # Одиночное сканирование спектра
    _sst: str = 'SST'  # Остановить сканирование спектра
    _srt: str = 'SRT'  # Повторить сканирование спектра
    _cls: str = '*CLS'  # Очистка
    _zone_marker_set: str = 'ZMK WL, {}, {}'  # Устанавливает центральную длину волны маркера зоны и ширину длины волны
    _zone_marker_get: str = 'ZMK? WL'  # Запрашивает центральную длину волны маркера зоны и ширину длины волны
    _analysis_spectrum: str = 'ANA PWR'  # Запускает анализ спектра
    _spectrum_analysis_result: str = 'ANAR?'  # Возвращает результат анализа спектра
    _analysis_spectrum_off: str = 'ANA OFF'  # Закрывает дисплей для спектрального анализа
    _zone_marker_erase: str = 'ZMK ERS'  # Cтирает отображение маркера зоны
    _erase_marker: str = 'EMK'  # Cтирает отображение длины волны, уровня, трассировки и дельта-маркеров


class AnritsuMS9740B(AnritsuMS9740BSCPICommands):

    def __init__(self, ip: str):
        self.__rm: pyvisa.ResourceManager = pyvisa.ResourceManager()
        self.__ip = ip
        self.__instance: TCPIPInstrument | pyvisa.Resource = self.connect()

    def connect(self, timeout: int = 60000) -> TCPIPInstrument | pyvisa.Resource:
        """
        Метод подключения к AnritsuMS9740B по ip-адресу
        :return:
        """
        inst: TCPIPInstrument | pyvisa.Resource = self.__rm.open_resource(f'TCPIP::{self.__ip}::INSTR',
                                                                          write_termination='\n',
                                                                          read_termination='\r\n')
        inst.timeout = timeout  # Задержка ответа
        try:
            response: str = inst.query(self._idn)
            if 'ANRITSU,MS9740B' not in response:
                raise ErrorRemoteConnection(f'Нет соединения с устройством [ {self.__ip} ]')
        except VisaIOError as vIOe:
            print(f'При попытке соединения c [ {self.__ip} ] произошла ошибка - [ {vIOe} ]')
            logger.exception(f'При попытке соединения c [ {self.__ip} ] произошла ошибка - [ {vIOe} ]')

        return inst

    def disconnect(self):
        """
        Метод отключения от устройства
        :return:
        """
        logger.info('Отключение от устройства')
        self.__rm.close()

    def send_command(self, cmd: str, delay: int | float = 0) -> None | str | int:
        """
        Метод отправки команды на устройсво
        :param cmd:
        :param delay:
        :return:
        """
        logger.info(f'Отправка команды {cmd}')
        answer: None | str | int = None
        try:
            if cmd.endswith('?'):
                answer: str = self.__instance.query(cmd, delay=delay)
                error_code: str = self.__instance.query(self._err, delay=delay)
                if error_code != '0':
                    return f'Команда {cmd} не применилась. Код {error_code}'
            else:
                answer: int = self.__instance.write(cmd)
                error_code: str = self.__instance.query(self._err, delay=delay)
                if error_code != '0':
                    return f'Команда {cmd} не применилась. Код {error_code}'
        except VisaIOError as vIOe:
            print(vIOe)

        return answer

    def get_wavelength_center(self) -> float:
        """
        Метод получения центральной длины волны
        :return:
        """
        return float(self.send_command(self._get_cnt))

    def set_wavelength_center(self, wavelength: str) -> int:
        """
        Метод установки центральной длины волны
        :param wavelength:
        :return:
        """
        return self.send_command(self._set_cnt.format(wavelength))

    def get_span(self) -> float:
        """
        Метод получения интервала
        :return:
        """
        return float(self.send_command(self._get_span))

    def set_span(self, span: str) -> int:
        """
        Метод установки интервала
        :param span:
        :return:
        """
        return self.send_command(self._set_span.format(span))

    def get_start_wave(self) -> float:
        """
        Метод получения начала измеряемого диапазона
        :return:
        """
        return float(self.send_command(self._get_start_wave))

    def set_start_wave(self, wavelength: str) -> int:
        """
        Метод установки начала измеряемого диапазона
        :param wavelength: от 600 до 1750
        :return:
        """
        return self.send_command(self._set_start_wave.format(wavelength))

    def get_stop_wave(self) -> float:
        """
        Метод получения конца измеряемого диапазона
        :return:
        """
        return float(self.send_command(self._get_stop_wave))

    def set_stop_wave(self, wavelength: str) -> int:
        """
        Метод установки конца измеряемого диапазона
        :param wavelength: от 600 до 1800
        :return:
        """
        return self.send_command(self._set_stop_wave.format(wavelength))

    def get_resolution(self) -> float:
        """
        Метод для получения текущего разрешения
        :return:
        """
        return float(self.send_command(self._get_res))

    def set_resolution(self, resolution: str) -> int:
        """
        Метод установки разрешения
        :param resolution:  0.03|0.05|0.07|0.1|0.2|0.5|1.0
        :return:
        """
        return self.send_command(self._set_res.format(resolution))

    def get_video_band_width(self) -> str:
        """
        Метод получения диапазона
        :return:
        """
        return self.send_command(self._get_vbw)

    def set_video_band_width(self, vbw: str) -> int:
        """
        Метод установки диапазона
        :param vbw: 10HZ|100HZ|200HZ|1KHZ|2KHZ|10KHZ|100KHZ|1MHZ
        :return:
        """
        return self.send_command(self._set_vbw.format(vbw))

    def reset(self) -> None:
        """
        Метод перезагрузки
        :return:
        """
        self.send_command(self._reset)

    def stop_sweep(self) -> str:
        """
        Метод для остановки
        :return:
        """
        return self.send_command(self._sst)

    def repeat_sweep(self) -> str:
        """
        Метод для повтора
        :return:
        """
        return self.send_command(self._srt)

    def single_sweep(self) -> str:
        """
        Метод одиночного сканирования
        :return:
        """
        self.send_command(self._cls)

        return self.send_command(self._ssi)

    def get_spectrum(self, single_sweep: bool = False) -> tuple[list, list]:
        """
        Метод получения спектра
        :param single_sweep:
        :return:
        """
        if single_sweep:
            self.single_sweep()

        spectrum_data: str = self.send_command('DQA?')
        spectrum_powers: list = list(map(float, spectrum_data.split(',')[0:-1]))
        start_wave: float = self.get_start_wave()
        stop_wave: float = self.get_stop_wave()
        wave_step: float = (stop_wave - start_wave) / (len(spectrum_powers) - 1)
        wavelength: list = [start_wave + wave_step * i for i in range(len(spectrum_powers))]

        return wavelength, spectrum_powers

    def get_spectrum_power(self, single_sweep: bool = False) -> float:
        """
        Метод получения мощности спектра
        :param single_sweep:
        :return:
        """
        center: float = self.get_wavelength_center()
        span: float = self.get_span() - 0.001
        self.send_command(self._zone_marker_set.format(center, span))
        self.send_command(self._analysis_spectrum)

        if single_sweep:
            self.single_sweep()

        str_pwr, str_center_wave = self.send_command(self._spectrum_analysis_result).strip().split(',')

        for command in [self._analysis_spectrum_off, self._zone_marker_erase, self._erase_marker]:
            self.send_command(command)

        return float(str_pwr)


if __name__ == '__main__':
    pass
