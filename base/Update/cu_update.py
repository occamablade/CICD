from json import JSONDecodeError
import json
import re
import logging

import requests
import fnmatch as fm

from swm import SWM
from Utilities.all import CU_REPO_URL, CU_URI

logger = logging.getLogger(__name__)


class GetCUPackages(SWM):

    def __init__(self, url: str, sw_name: str, nd: str) -> None:

        """
        Забирает только пакеты для блока CU
        :param url: всегда этот url http://192.168.29.110:8000/api/getPackages/
        :param sw_name: название набора прошивок для cu:
        1) Если нужен последний актуальный мастер, то значение latest_master
        2) Если нужен последний актуальный sa, то значение latest_customer_sa
        3) На этом сайте хранятся пакеты для cu за последние 8 дней, включая сегодняшний. Формат записи выглядит так:
        18112022_master или 18112022_customer_sa
        """
        self.url = url
        self.sw_name = sw_name
        self._cu_fw = self._get_list_packages()
        super().__init__(chs=nd)

    def _get_list_packages(self) -> list:

        try:
            packages_res = requests.get(url=self.url)
            json_pack = json.loads(packages_res.text)
            pack = dict(zip(json_pack[::2], json_pack[
                                            1::2]))  # Создаётся словарь, где ключом будет каждый второй элемент в списке json_pack начиная с 0, а значением будет список пакетов, как bin так и zip
            return pack[self.sw_name][3]
        except (JSONDecodeError, requests.exceptions.ConnectionError) as e:
            logger.exception(f'Что-то пошло не так: {e}')

    def _pkg(self) -> list:
        bundle_name = tuple(filter(lambda b: fm.fnmatch(b, '*bundle*'), self._cu_fw))
        packages_list = [x for x in self._get_list_packages() if x not in bundle_name]
        return packages_list

    def _bndl(self) -> tuple:
        bundle_name = tuple(filter(lambda b: fm.fnmatch(b, '*bundle*'), self._cu_fw))
        return bundle_name

    def upload_bundle_on_node(self) -> tuple:
        bundle_name = self._bndl()
        remade_name_pack = re.sub(r'\.', 'point', *bundle_name)
        bundle_uri = f'{CU_URI}{self.sw_name}slashzipslash{remade_name_pack}/getPackages'
        return self.download_bundle_file(bundle_uri)

    def upload_package_on_node(self) -> None:
        for pkg in self._pkg():
            remade_name_pack = re.sub(r'\.', 'point', pkg)
            self.download_package_file(f'{CU_URI}{self.sw_name}slashzipslash{remade_name_pack}/getPackages')

    def install_bundle(self) -> None:
        bundle_name = list(filter(lambda b: fm.fnmatch(b, '*bundle*'), self._cu_fw))
        bundle_name_wtht_zip = bundle_name[0].strip('.zip')
        self.install_bundle_with_cfm(bundle_name_wtht_zip)

    def activate_bundle_on_node(self) -> None:
        bundle_name = list(filter(lambda b: fm.fnmatch(b, '*bundle*'), self._cu_fw))
        bundle_name_wtht_zip = bundle_name[0].strip('.zip')
        self.activate_bundle(bundle_name_wtht_zip)

    def remove_bundle_from_node(self) -> None:
        bundle_name = list(filter(lambda b: fm.fnmatch(b, '*bundle*'), self._cu_fw))
        bundle_name_wtht_zip = bundle_name[0].strip('.zip')
        self.remove_bundle_file(bundle_name_wtht_zip)

    def confirmation(self) -> None:
        bundle_name = list(filter(lambda b: fm.fnmatch(b, '*bundle*'), self._cu_fw))
        bundle_name_wtht_zip = bundle_name[0].strip('.zip')
        self.confirm_bundle(bundle_name_wtht_zip)
