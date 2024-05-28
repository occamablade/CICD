import logging
from dataclasses import dataclass

from time import sleep
from telnetlib import Telnet

from Utilities.decorators.timer import execution_time

logger = logging.getLogger(__name__)


def _parse_answer(str_: bytes) -> str:
    return str(str_).split("\\")[0].strip("b'")


@dataclass
class ExfoSCPICommands:
    _conditions: str = 'LINS{}:SOUR:DATA:TEL:TEST?'  # Тест запущен или нет
    _start_test: str = 'LINS{}:SOUR:DATA:TEL:TEST ON'  # Запустить тест
    _stop_test: str = 'LINS{}:SOUR:DATA:TEL:TEST OFF'  # Остановить тест
    _util: str = 'LINS{}:SENS:DATA:TEL:ETH:PACK:LINE:UTIL? {}'  # Узнать загрузку по TX/RX
    _util_val: float = 0.00000
    _laser_control_all_lines: str = 'LINS{}:OUTP:TEL:LAS {}'  # Выключить все лазеры для линии
    _switch: str = 'LINS{}:SOUR:DATA:TEL:PORT {}'  # Сменить рабочий порт (для 2-х портовых модулей)
    _to_know_port: str = 'LINS{}:SOUR:DATA:TEL:PORT?'  # Узнать какой порт рабочий (для 2-х портовых модулей)
    _test_time: str = 'LINS{}:FETch:DATA:TELecom:TEST:TIME?'  # Узнать время работы теста
    _reset: str = 'LINS{}:SOURce:DATA:TELecom:RESet'  # Перезагрузить тест
    _verdict: str = 'LINS{}:FETC:DATA:TEL:TEST:STAT:VERD?'  # Узнать вердикт по тесту PASS or FAIL
    _testStatus: str = 'LINS{}:FETC:DATA:TEL:TEST:STAT?'  # Узнать статус теста (Inprogress, Completed)
    _tx_frame: str = 'LINS{}:SOUR:DATA:TEL:ETH:FRAM:COUN:TX? FTOT'  # Узнать число фреймов для передачи
    _las_on: str = 'LINS{}:OUTPUT:TEL:LAS ON'  # Включить лазер (сама опция)
    _las_off: str = 'LINS{}:OUTPUT:TEL:LAS OFF'  # Выключить лазер (сама опция)
    _sdt_l: str = 'LINS{}:FETC:DATA:TEL:SDT:LONG?'  # Самый длинный временной интервал
    _sdt_s: str = 'LINS{}:FETC:DATA:TEL:SDT:SHOR?'  # Самый короткий временной интервал
    _sdt_a: str = 'LINS{}:FETC:DATA:TEL:SDT:AVER?'  # Средний временной интервал
    _sdt_t: str = 'LINS{}:FETC:DATA:TEL:SDT:TOT?'  # Общее время
    _sdt_c: str = 'LINS{}:FETC:DATA:TEL:SDT:COUN?'  # Число переключений
    _rfc2544_test: str = 'LINS{}:SOUR:DATA:TEL:TEST:TYPE RFC2544'  # Запустить RFC2544
    _rfc_udef: str = 'LINS{}:SOUR:DATA:TEL:ETH:RFC:FDIS UDEF'  # Выбрать User Define
    _rfc_frame_size: str = 'LINS{}:SOUR:DATA:TEL:ETH:RFC:FSIZ %s, %s'  # Внести размер фреймов для определённого поля
    _rfc_quan: str = 'LINS{}:SOUR:DATA:TEL:ETH:RFC:QUAN {}'  # Внести количество полей
    _ppm_set: str = 'LINS{}:SOUR:DATA:TEL:OPT:PORT:FREQ:OFFS:VAL {}'
    _ppm_get: str = 'LINS{}:SOUR:DATA:TEL:OPT:PORT:FREQ:OFFS:VAL?'
    _ppm_manage: str = 'LINS{}:SOUR:DATA:TEL:OPT:PORT:FREQ:OFFS {}'


class Exfo(ExfoSCPICommands):
    """Описывает несколько методов для EXFO"""

    def __init__(self, exfo_ip: str, module: int) -> None:
        """
        :param exfo_ip: IP адрес EXFO BER тестера
        :param module: номер модуля
        """
        super().__init__()
        self.tn = Telnet()
        self.exfo_ip = exfo_ip
        self.module = module - 1
        self._connection_to_exfo()

    def _connection_to_exfo(self) -> None:
        try:
            logger.info(f'Идёт подключение к [ {self.exfo_ip} ]')
            self.tn.open(self.exfo_ip, port=5024)
            sleep(5)
            self.tn.read_until(b'READY> ', timeout=1)
        except EOFError as error:
            logger.exception(f"{error}, {self.exfo_ip} сетевое соединение не удалось")

    def close(self) -> None:
        logger.info(f'Отключение от [ {self.exfo_ip} ]')
        self.tn.close()

    def _wait_exfo_answer(self, example_str: str, func=None) -> None:
        """
        TODO
        :param example_str: Пример ожидаемой строки, с которой нужно сравниться
        :param func: Принимает функцию. Т.к. не всегда нужно делать запрос на обновление, а нужно ждать время
        :return:
        """
        counter = 200
        if func is not None:
            while counter:
                func()
                val = _parse_answer(self.tn.read_until(b'READY> ', timeout=1)).strip()
                if val == example_str:
                    break
                counter -= 1
                sleep(3)
                logger.info(f'Ожидание ответа. Обратный отсчёт [ {counter} ]')
            else:
                raise TimeoutError
        else:
            while counter:
                v = _parse_answer(self.tn.read_until(b'READY> ', timeout=1)).strip()
                if v == example_str:
                    break
                counter -= 1
                sleep(3)
                logger.info(f'Ожидание ответа. Обратный отсчёт [ {counter} ]')
            else:
                raise TimeoutError

    def condition(self) -> None:
        try:
            self.tn.read_until(b'READY> ', timeout=5)
            self.tn.write(self._conditions.format(self.module).encode() + b'\n')
            if _parse_answer(self.tn.read_until('READY> '.encode(), timeout=1)) == "1":
                print(f"Тест на модуле {self.module + 1} запущен")
            else:
                print(f"Тест на модуле {self.module + 1} не запущен")
        except (EOFError, OSError) as err:
            logger.exception(f'При запросе состояния теста произошла ошибка [ {err} ]')

    def start_test_for_module(self) -> None:
        try:
            self.tn.write(self._start_test.format(self.module).encode() + b'\n')
            logger.info('Тест запущен')
        except OSError as err:
            logger.exception(f'При запуске теста произошла ошибка [ {err} ]')

    def stop_test_for_module(self) -> None:
        try:
            self.tn.write(self._stop_test.format(self.module).encode() + b'\n')
            logger.info('Тест остановлен')
        except OSError as err:
            logger.exception(f'При остановке теста произошла ошибка [ {err} ]')

    def utilization(self, direction: str) -> bool:
        """
        :param direction: Направление, передача или приём, принимает RX или TX
        :return:
        """
        try:
            self.tn.read_until(b'READY> ', timeout=5)
            self.tn.write(self._util.format(self.module, direction).encode() + b'\n')
            status = _parse_answer(self.tn.read_until(b'READY> ', timeout=1))
            if float(status) > self._util_val:
                return True
            return False
        except (EOFError, OSError) as err:
            logger.exception(f'При проверки utilization произошла проблема [ {err} ]')

    def on_off_laser_alllanes(self, param: str) -> None:
        """
        :param param: Принимает ON или OFF
        :return:
        """
        try:
            self.tn.write(self._laser_control_all_lines.format(self.module, param).encode() + b'\n')
        except EOFError as err:
            logger.exception(f'При вкл/выкл лазера произошла ошибка [ {err} ]')

    def switch_port(self, port: str) -> None:
        """
        :param port: Принимает FIRST для первого порта, SECOND для второго порта
        :return:
        """
        try:
            self.tn.read_until(b'READY> ', timeout=5)
            self.tn.write(self._switch.format(self.module, port).encode() + b'\n')
            self.tn.read_until(b'READY> ', timeout=5)
            self.tn.write(self._to_know_port.format(self.module).encode() + b'\n')
            status = _parse_answer(self.tn.read_until(b'READY> ', timeout=1))
            logger.info(f'Активный порт [ {status} ]')
        except (EOFError, OSError) as err:
            logger.exception(f'При вкл/выкл лазера произошла ошибка [ {err} ]')

    def time_test(self) -> None:
        try:
            self.tn.read_until(b'READY> ', timeout=5)
            self.tn.write(self._test_time.format(self.module).encode() + b'\n')
            time_to_test = _parse_answer(self.tn.read_until(b'READY> ', timeout=1))
            print(f"Время работы теста: {time_to_test}")
        except (EOFError, OSError) as err:
            logger.exception(f'При запросе времени работы теста произошла ошибка [ {err} ]')

    def reset_test_for_module(self) -> None:
        try:
            self.tn.read_until(b'READY> ', timeout=1)
            self.tn.write(self._reset.format(self.module).encode() + b'\n')
            self.tn.read_until(b'READY> ', timeout=1)
            logger.info("Тест перезапущен")
        except (EOFError, OSError) as err:
            logger.exception(f'При перезапуске теста произошла ошибка [ {err} ]')

    def status(self) -> bool:
        try:
            self.tn.read_until(b'READY> ', timeout=1)
            self.tn.write(self._verdict.format(self.module).encode() + b'\n')
            status = _parse_answer(self.tn.read_until(b'READY> ', timeout=1))
            if status == "PASS":
                return True
            else:
                return False
        except (EOFError, OSError) as err:
            logger.exception(f'При запросе статуса теста произошла ошибка [ {err} ]')

    def _test_status(self) -> None:
        try:
            sleep(3)
            self.tn.read_until(b'READY> ', timeout=5)
            self.tn.write(self._testStatus.format(self.module).encode() + b'\n')
        except (EOFError, OSError) as err:
            logger.exception(f'При запросе статуса теста произошла ошибка [ {err} ]')

    def tx_frame_stat(self) -> str:
        try:
            self.tn.read_until(b'READY> ', timeout=5)
            self.tn.write(self._tx_frame.format(self.module).encode() + b'\n')
            status = _parse_answer(self.tn.read_until(b'READY> ', timeout=1))
            return status
        except (EOFError, OSError) as err:
            logger.exception(f'При запуске теста произошла ошибка [ {err} ]')

    def laser_on(self) -> None:
        try:
            self.tn.write(self._las_on.format(self.module).encode() + b'\n')
            logger.info('Лазер включен')
        except OSError as err:
            logger.exception(f'При включении лазера произошла ошибка [ {err} ]')

    def laser_off(self) -> None:
        try:
            self.tn.write(self._las_off.format(self.module).encode() + b'\n')
            logger.info('Лазер выключен')
        except OSError as err:
            logger.exception(f'При выключении лазера произошла ошибка [ {err} ]')

    def sdt_long(self) -> str:
        try:
            self.tn.read_until(b'READY> ', timeout=5)
            self.tn.write(self._sdt_l.format(self.module).encode() + b'\n')
            value = _parse_answer(self.tn.read_until(b'READY> ', timeout=1))
            return value
        except (EOFError, OSError) as err:
            logger.exception(f'При работе с SDT произошла ошибка [ {err} ]')

    def sdt_shor(self) -> str:
        try:
            self.tn.read_until(b'READY> ', timeout=5)
            self.tn.write(self._sdt_s.format(self.module).encode() + b'\n')
            value = _parse_answer(self.tn.read_until(b'READY> ', timeout=1))
            return value
        except (EOFError, OSError) as err:
            logger.exception(f'При работе с SDT произошла ошибка [ {err} ]')

    def sdt_aver(self) -> str:
        try:
            self.tn.read_until(b'READY> ', timeout=5)
            self.tn.write(self._sdt_a.format(self.module).encode() + b'\n')
            value = _parse_answer(self.tn.read_until(b'READY> ', timeout=1))
            return value
        except (EOFError, OSError) as err:
            logger.exception(f'При работе с SDT произошла ошибка [ {err} ]')

    def sdt_total(self) -> str:
        try:
            self.tn.read_until(b'READY> ', timeout=5)
            self.tn.write(self._sdt_t.format(self.module).encode() + b'\n')
            value = _parse_answer(self.tn.read_until(b'READY> ', timeout=1))
            return value
        except (EOFError, OSError) as err:
            logger.exception(f'При работе с SDT произошла ошибка [ {err} ]')

    def sdt_count(self) -> str:
        try:
            self.tn.read_until(b'READY> ', timeout=5)
            self.tn.write(self._sdt_c.format(self.module).encode() + b'\n')
            value = _parse_answer(self.tn.read_until(b'READY> ', timeout=1))
            return value
        except (EOFError, OSError) as err:
            logger.exception(f'При работе с SDT произошла ошибка [ {err} ]')

    @execution_time
    def rfc2544(self, quan: int, *args: tuple[int, int]) -> bool:
        """
        RFC 2544 тест
        :param quan: Колличество байтовых полей для установки фреймов
        :param args: Пара номер поля и размер фрейма, принимет tuple
        :return:
        """
        commands = [self._rfc2544_test, self._rfc_udef]
        frame_size = [self._rfc_frame_size] * len(args)
        try:
            self.stop_test_for_module()
            logger.info('Включение RFC 2544')
            for command in commands:
                _parse_answer(self.tn.read_until(b'READY> ', timeout=1))
                self.tn.write(command.format(self.module).encode() + b'\n')
                self._wait_exfo_answer('Command executed successfully.')
            logger.info('Тест RFC2544 включен. "Frame Distribution" установлен "User Define"')

            _parse_answer(self.tn.read_until(b'READY> ', timeout=1))
            self.tn.write(self._rfc_quan.format(self.module, quan).encode() + b'\n')
            self._wait_exfo_answer('Command executed successfully.')
            logger.info(f'Quantity равно [ {quan} ]')

            format_command = list(map(lambda x, y: x.format(self.module) % tuple(y), frame_size, args))
            for fc in format_command:
                _parse_answer(self.tn.read_until(b'READY> ', timeout=1))
                self.tn.write(fc.encode() + b'\n')
                self._wait_exfo_answer('Command executed successfully.')
                logger.info(f'Номер байтового поля и размер фреймов (байты) {fc.split()[-2::]}')

            self.start_test_for_module()
            self._wait_exfo_answer('"Completed"', func=self._test_status)
            logger.info('Тест завершился. Просьба сохранить и забрать отчёт!!!')
        except (EOFError, OSError, TimeoutError) as err:
            logger.exception(f'При включении RFC 2544 произошла ошибка [ {err} ]')
            return False
        return True

    def get_ppm(self) -> float:
        try:
            self.tn.read_until(b'READY> ', timeout=1)
            self.tn.write(self._ppm_get.format(self.module).encode() + b'\n')
            ppm_now = _parse_answer(self.tn.read_until(b'READY> ', timeout=1))
            return float(ppm_now)
        except (EOFError, OSError) as err:
            logger.exception(err)

    def set_ppm(self, ppm: str):
        try:
            _parse_answer(self.tn.read_until(b'READY> ', timeout=1))
            logger.info(f'Установка PPM - [ {ppm} ]')
            self.tn.write(self._ppm_set.format(self.module, ppm).encode() + b'\n')
            self._wait_exfo_answer('Command executed successfully.')
            logger.info(f'PPM установлен - [ {self.get_ppm()} ]')
        except (EOFError, OSError, TimeoutError) as err:
            logger.exception(err)

    def manage_offset(self, val: str) -> None:
        try:
            self.tn.write(self._ppm_manage.format(self.module, val).encode() + b'\n')
        except OSError as err:
            logger.exception(err)
