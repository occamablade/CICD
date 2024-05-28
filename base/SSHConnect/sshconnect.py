import os
import time
import pathlib

import paramiko
from paramiko import SSHClient


class SshConn:

    def __init__(self, server: str, user: str, password: str, port=22) -> None:

        self.__server = server
        self.__user = user
        self.__password = password
        self.__port = port
        self.client = self._ssh_connect()

    def _ssh_connect(self) -> SSHClient:
        cl = paramiko.SSHClient()
        cl.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        start = time.time()
        timed = 0
        while timed < 300:
            try:
                cl.connect(self.__server, self.__port, self.__user, self.__password)
                break
            except paramiko.ssh_exception.NoValidConnectionsError:
                timed = time.time() - start
            except Exception as er:
                print(er)
                timed = time.time() - start
        else:
            raise paramiko.SSHException(f'Не удалось открыть {self.__server}:{self.__port}')

        return cl

    def logout(self) -> None:
        if self.client:
            self.client.close()

    def command(self, cmd: str) -> str:

        stdin, stdout, stderr = self.client.exec_command(cmd)

        out = stdout.read().decode(errors='backslashreplace').strip()
        # errors = stderr.read().decode().strip()
        # if errors:
        #     raise Exception(f'Ошибка {errors}')

        return out

    def get_file(self, remote_path: str, local_path: str) -> None:

        file_name = remote_path.split('/')[-1]
        file_path = os.path.join(os.getcwd(), local_path)
        pathlib.Path(file_path).mkdir(parents=True, exist_ok=True)
        sftp_client = self.client.open_sftp()
        try:
            sftp_client.get(remote_path, f'{file_path}/{file_name}')
        except Exception as e:
            err = f'Ошибка при получении файла {remote_path}: {e}'
            print(err)
            raise e
        finally:
            sftp_client.close()
