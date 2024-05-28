import json
import logging

from requests import Session
import xmltodict

from Utilities.all import URL_NMS, LOGIN_NMS, PASSWD_NMS


logger = logging.getLogger(__name__)


class APISession(Session):

    def __init__(self):
        Session.__init__(self)
        self.headers.update({
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36(KHTML, like Gecko) '
                          'Chrome/119.0.0.0 Safari/537.36'
        })
        self.url = URL_NMS
        self.passwd = PASSWD_NMS
        self.login = LOGIN_NMS
        self.init_auth()

    def init_auth(self):

        logger.warning(f'Login на [ {self.url.split("/")[-2]} ]')
        payload = {
            'login': self.login,
            'pass': self.passwd,
            'cmd': 'webauth'
        }

        content = self.request('POST', self.url, json=payload)
        assert content.status_code == 200, f'Status code: {content.status_code}\n\t\t Body: {content.text}'
        json_body = json.loads(content.text)
        assert json_body['error'] == 'OK'
        self.headers.update({'Cookie': content.headers['Set-Cookie']})

    def disconnect(self):

        payload = {'cmd': 'logout'}
        self.request('POST', self.url, json=payload)
        logger.warning(f'Logout с [ {self.url.split("/")[-2]} ]')


class Backup(APISession):

    def get_backup(self, node_id: str, backup_name: str) -> dict:

        payload = {
            'cmd': 'downloadBackup',
            'node_id': node_id,
            'backupname': backup_name
        }

        content = self.request('POST', self.url, json=payload)
        json_body = json.loads(content.text)

        assert json_body['error'] == "OK"
        logger.warning(f'Backup [ {backup_name} ] сохранён')

        return xmltodict.parse(json_body['data'])

    def create_backup(self, node_id: str, backup_name: str) -> None:

        payload = {
            'cmd': 'backupConfigNode',
            'node_id': node_id,
            'backupname': backup_name
        }

        content = self.request('POST', self.url, json=payload)
        json_body = json.loads(content.text)

        assert json_body['error'] == "OK"
        logger.warning(f'Backup [ {backup_name} ] создан')

    def delete_backup(self, node_id: str, backup_id: str):
        # TODO сделать функцию по получению id для backup
        payload = {
            'cmd': 'backupConfigNode',
            'node_id': node_id,
            'id': backup_id
        }

        content = self.request('POST', self.url, json=payload)
        json_body = json.loads(content.text)

        assert json_body['error'] == "OK"
        logger.warning(f'Backup [ {backup_id} ] удален')


class CreateTrail(APISession):

    def create_client_trail(self):
        pass
