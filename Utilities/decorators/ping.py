import subprocess
from functools import wraps
from time import sleep


def ping(ip: str):
    def _decorator(func):
        @wraps(func)
        def _wrapper(*args, **kwargs):
            time = 300
            while time:
                replay = subprocess.run(f'ping {ip} -c 1', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        encoding='cp866')
                if replay.returncode == 0:
                    return func(*args, **kwargs)
                else:
                    print(f'Узел [ {ip} ] недоступен. Ожидаем ответа')
                    sleep(30)
                    time -= 1

        return _wrapper

    return _decorator
