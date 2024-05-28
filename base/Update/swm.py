import json
from typing import Union
import logging
from dataclasses import dataclass

from urllib.request import urlopen

from base.RestConf.restconf import execute_rpc
from Utilities.all import PASSW, USER
from base.Update.board_update import GetFirmwaresFromProdsDirectory, GetFirmwaresFromBuildDirectory

logger = logging.getLogger(__name__)


@dataclass
class SWMPath:
    _download_bundle_file: str = 'operations/swm-download-bundle-file'
    _download_package_file: str = 'operations/swm-download-package-file'
    _install_bundle: str = 'operations/swm-install-bundle'
    _activate_bundle: str = 'operations/swm-activate-bundle'
    _confirm_bundle: str = 'operations/swm-confirm-bundle'
    _remove_bundle: str = 'operations/swm-remove-bundle-file'
    _remove_package: str = 'operations/swm-remove-package-file'
    _cold_reboot: str = 'operations/swm-cold-reboot-device'
    _warm_reboot: str = 'operations/swm-hot-reboot-device'


class SWM(SWMPath):

    def __init__(self, node_ip: str):
        self.__ip = node_ip
        self.__path: None | str = None

    def download_bundle_file(self, uri) -> tuple[str, str, str]:
        self.__path: str = self._download_bundle_file
        billet_cfg: dict = {
            "input": {
                "uri": uri,
                "login": USER,
                "password": PASSW
            }
        }
        logger.info(f'Отправка бандла на ноду [ {self.__ip} ]')
        rpc_data: str = json.dumps(billet_cfg)
        return execute_rpc(cfg=rpc_data, url=self.__ip, path=self.__path)

    def download_package_file(self, uri) -> tuple[str, str, str]:
        self.__path: str = self._download_package_file
        billet_cfg: dict = {
            "input": {
                "uri": uri,
                "login": USER,
                "password": PASSW
            }
        }
        logger.info(f'Отправка пакета на ноду [ {self.__ip} ]')
        rpc_data: str = json.dumps(billet_cfg)
        return execute_rpc(cfg=rpc_data, url=self.__ip, path=self.__path)

    def install_bundle_with_cfm(self, name) -> tuple[str, str, str]:
        self.__path: str = self._install_bundle
        billet_cfg: dict = {
            "input": {
                "name": name,
                "type": "with-cfm"
            }
        }
        logger.info(f'Установка бандла [ {name} ] на ноду [ {self.__ip} ]')
        rpc_data: str = json.dumps(billet_cfg)
        return execute_rpc(cfg=rpc_data, url=self.__ip, path=self.__path)

    def activate_bundle(self, name) -> tuple[str, str, str]:
        self.__path: str = self._activate_bundle
        billet_cfg: dict = {
            "input": {
                "name": name
            }
        }
        logger.info(f'Активация бандла [ {name} ] на ноде [ {self.__ip} ]')
        rpc_data: str = json.dumps(billet_cfg)
        return execute_rpc(cfg=rpc_data, url=self.__ip, path=self.__path)

    def confirm_bundle(self, name) -> tuple[str, str, str]:
        self.__path: str = self._confirm_bundle
        billet_cfg: dict = {
            "input": {
                "name": name
            }
        }
        logger.info(f'Подтверждение бандла [ {name} ] на ноде [ {self.__ip} ]')
        rpc_data: str = json.dumps(billet_cfg)
        return execute_rpc(cfg=rpc_data, url=self.__ip, path=self.__path)

    def remove_bundle_file(self, name) -> tuple[str, str, str]:
        self.__path: str = self._remove_bundle
        billet_cfg: dict = {
            "input": {
                "name": name
            }
        }
        logger.info(f'Удаление бандла [ {name} ] на ноде [ {self.__ip} ]')
        rpc_data: str = json.dumps(billet_cfg)
        return execute_rpc(cfg=rpc_data, url=self.__ip, path=self.__path)

    def remove_package_file(self, name) -> tuple[str, str, str]:
        self.__path: str = self._remove_package
        billet_cfg: dict = {
            "input": {
                "name": name
            }
        }
        logger.info(f'Удаление пакета [ {name} ] на ноде [ {self.__ip} ]')
        rpc_data: str = json.dumps(billet_cfg)
        return execute_rpc(cfg=rpc_data, url=self.__ip, path=self.__path)

    def cold_reboot(self, name) -> tuple[str, str, str]:
        self.__path: str = self._cold_reboot
        billet_cfg = {
            "input": {
                "object-class": "EmCpk",
                "object": name
            }
        }
        logger.info(f'Cold reboot платы [ {name} ] на ноде [ {self.__ip} ]')
        rpc_data: str = json.dumps(billet_cfg)
        return execute_rpc(cfg=rpc_data, url=self.__ip, path=self.__path)

    def warm_reboot(self, name) -> tuple[str, str, str]:
        self.__path: str = self._warm_reboot
        billet_cfg = {
            "input": {
                "object-class": "EmCpk",
                "object": name
            }
        }
        logger.info(f'Warm reboot платы [ {name} ] на ноде [ {self.__ip} ]')
        rpc_data: str = json.dumps(billet_cfg)
        return execute_rpc(cfg=rpc_data, url=self.__ip, path=self.__path)


class Repository:

    def __init__(self, chs: str) -> None:
        """

        :param chs: Последние два октета от ip адреса через точку
        """
        self.chs = chs

    def _get_content(self, dir_: str) -> dict:
        url = f'http://192.168.{self.chs}:81/restconf/data/swm/repository/{dir_}'
        contents = urlopen(url).read()
        contents_json = json.loads(contents)
        return contents_json

    def repo_packages(self) -> Union[tuple, None]:
        contents_json = self._get_content('packages')
        pkg = tuple(map(lambda d: d['name'], contents_json['nec-swm:packages']['package']))
        if not pkg:
            return None
        return pkg

    def repo_bundle(self) -> Union[tuple, None]:
        contents_json = self._get_content('bundles')
        bndl = tuple(map(lambda d: d['name'], contents_json['nec-swm:bundles']['bundle']))
        if not bndl:
            return None
        return bndl

    def bundle_status(self, name: str) -> Union[str, None]:
        contents_json = self._get_content('bundles')
        st = tuple(
            map(lambda s: s['status'], filter(lambda d: d['name'] == name, contents_json['nec-swm:bundles']['bundle'])))
        if not st:
            return None
        return st[0]
