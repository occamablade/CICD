import json
import logging
from typing import Union

from urllib.request import urlopen

from Utilities.all import FM

logger = logging.getLogger(__name__)


class FaultMngr:

    def __init__(self, node: str) -> None:
        """

        :param node: Последние два октета от ip адреса через точку
        """
        self.node = node
        self._data = self._get_content()

    def _get_content(self) -> dict:
        url = FM.format(self.node)
        contents = urlopen(url).read()
        contents_json = json.loads(contents)
        return contents_json

    def get_alarm(self, aid: str, alarm: str) -> Union[str, None]:
        """

        :param alarm: Название аварии/дефекта
        :param aid: AID объекта на котором проводится поиск аварии/дефекта
        :return:
        """
        lst = self._data['nec-fm:conditions']['condition']
        logger.info('Поиск аварии')
        tup_ = tuple(filter(lambda a: a['probable-cause'] == f'nec-fm:{alarm}',
                            filter(lambda x: x['object'] == aid, lst)))
        if not tup_:
            return None
        return tup_[0]['probable-cause'].split(':')[-1]
