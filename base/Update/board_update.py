import json
# import re
import logging
from abc import ABC, abstractmethod

import requests
# import fnmatch as fm

# from swm import SWM
from Utilities.all import (
    BOARD_REPO_URL, CU_REPO_URL, DOWNLOAD_PATH_WTH_VERSION,
    DOWNLOAD_PATH_WTHT_VERSION, DOWNLOAD_PATH_FOR_CU_FIRMWARE
)

logger = logging.getLogger(__name__)


class GetFirmwaresFromDirectory(ABC):

    @abstractmethod
    def _firmwares_folder(self, folder: None | str = None) -> dict:
        pass

    @abstractmethod
    def get_device_firmwares(self, device_name: str, folder: str, fw: str = None) -> tuple[IndexError, str]:
        pass

    @abstractmethod
    def _download_firmwares_from_server(self, dv_n: str, cne_fldr: str, fws_version: list,
                                        vers: str | None = None) -> None:
        pass


class GetFirmwaresFromProdsDirectory(GetFirmwaresFromDirectory):

    def __init__(self, download: bool = False):
        self.__fw_url: str = BOARD_REPO_URL
        self.__download = download

    def _firmwares_folder(self, folder: None = None) -> dict:
        """
        Метод собирающий имена прошивок из папки 'firmwares'
        :return:
        """
        response: requests.Response = requests.get(url=self.__fw_url)
        json_pack: list = json.loads(response.text)

        for idx, elem in enumerate(json_pack):
            if elem['name'] == 'firmwares':
                return json_pack[idx]

    def get_device_firmwares(self, device_name: str, folder: str, fw: str = None) -> tuple[IndexError, str] | list:
        """
        Метод находит и сохраняет прошивку
        :param device_name: имя устройства на сервере прошивок, например (Dvina-O, Birysa, Irsa и т.д.)
        :param folder: папка cne
        :param fw: папка с версией прошивки (если он есть), например (0.9.4.cne, 0.9.4.cne-rc1)
        :return:
        """
        all_contents: list | None = self._firmwares_folder().get('contents')
        current_device: list = list(filter(lambda el: el['name'] == device_name, all_contents))[0]['contents']
        output_data: dict = {
            'device_name': device_name,
            'folder': folder,
            'fws': []
        }

        if fw:
            output_data['fw_version'] = fw
        else:
            output_data['fw_version'] = None

        try:
            current_folder: list = list(filter(lambda fldr: fldr['name'] == folder, current_device))[0]['contents']
        except IndexError as IE:
            return IE, f'Папка {folder} для устройства {device_name} в репозитории {self.__fw_url} не найдена'

        for obj in current_folder:
            if obj['type'] == 'file':
                output_data['fws'].append(obj['name'])
            elif obj['type'] == 'folder':
                current_firmwares: list = list(filter(lambda fws: fws['name'] == fw, current_folder))[0]['contents']
                for firmware in current_firmwares:
                    output_data['fws'].append(firmware['name'])
                break

        q = self._download_firmwares_from_server(dv_n=output_data['device_name'], cne_fldr=output_data['folder'],
                                                 fws_version=output_data['fws'], vers=output_data['fw_version'])

        return q

    def _download_firmwares_from_server(self, dv_n: str, cne_fldr: str, fws_version: list,
                                        vers: str | None = None) -> None | list:
        """
        Метод загружает прошивки в текущую директорию
        :param dv_n: имя устройства
        :param cne_fldr: папка cne или другая
        :param fws_version: список версий прошивок
        :param vers: версия прошивки (если он есть), например (0.9.4.cne, 0.9.4.cne-rc1)
        :return:
        """
        fws_link_list: list = []

        for fw_version in fws_version:
            if vers:
                fws_link_list.append(DOWNLOAD_PATH_WTH_VERSION.format(dv_n, cne_fldr, vers, fw_version))
            else:
                fws_link_list.append(DOWNLOAD_PATH_WTHT_VERSION.format(dv_n, cne_fldr, fw_version))

        if self.__download:
            for idx, fws_link in enumerate(fws_link_list):
                r = requests.get(url=fws_link)

                with open(f'{fws_version[idx]}', 'wb') as file:
                    file.write(r.content)

        return fws_link_list


class GetFirmwaresFromBuildDirectory(GetFirmwaresFromDirectory):

    def __init__(self, download: bool = False):
        self.__fw_url = CU_REPO_URL
        self.__download = download

    def _firmwares_folder(self, folder: str = None) -> dict:
        """
        Метод собирающий имена прошивок из указанной папки, например (latest_master_dn3m, latest_master_dn3)
        :param folder: имя папки, например (latest_master_dn3m, latest_master_dn3)
        :return:
        """
        response: requests.Response = requests.get(url=self.__fw_url)
        json_pack: list = json.loads(response.text)

        for idx, elem in enumerate(json_pack):
            if elem['name'] == folder:
                return json_pack[idx]

    def get_device_firmwares(self, name: str, folder: str, fw: str = None) -> tuple[IndexError, str]:
        """
        Метод находит и сохраняет прошивку
        :param name: zip или bin
        :param folder: имя папки, например (latest_master_dn3m, latest_master_dn3)
        :param fw: в данном классе не используется
        :return:
        """
        all_contents: list | None = self._firmwares_folder(folder=folder).get('contents')
        current_packages: list = list(filter(lambda el: el['name'] == name, all_contents))[0]['contents']
        output_data: dict = {
            'name': name,
            'folder': folder,
            'fws': None
        }

        try:
            current_folder: list = [pack['name'] for pack in current_packages if not pack['name'].startswith('u-boot')]
        except IndexError as IE:
            return IE, f'Папка {folder} для устройства {name} в репозитории {self.__fw_url} не найдена'
        output_data['fws'] = current_folder

        self._download_firmwares_from_server(fldr=output_data['folder'], name=output_data['name'],
                                             fws_version=output_data['fws'])

    def _download_firmwares_from_server(self, name: str, fldr: str, fws_version: list,
                                        vers: str | None = None) -> None | list:
        """
        Метод загружает прошивки в текущую директорию
        :param name: zip или bin
        :param fldr: имя папки, например (latest_master_dn3m, latest_master_dn3)
        :param fws_version: список прошивок
        :param vers:
        :return:
        """
        fws_link_list: list = []

        for fw_version in fws_version:
            fws_link_list.append(DOWNLOAD_PATH_FOR_CU_FIRMWARE.format(fldr, name, fw_version))

        if self.__download:
            for idx, fws_link in enumerate(fws_link_list):
                r = requests.get(url=fws_link)

                with open(f'{fws_version[idx]}', 'wb') as file:
                    file.write(r.content)

        return fws_link_list
