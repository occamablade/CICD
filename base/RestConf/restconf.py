import json
import subprocess
from typing import Union, Any


class RestConf:

    def __init__(self, path: str, node: str) -> None:
        self.path = path
        self.node = node

    def set_restconf(self, cfg=None) -> bytes:

        url_add = f'http://192.168.{self.node}:81/restconf/{self.path}'
        command = "curl -u admin:admin \
                         -H \"Accept: application/yang-data+json\" \
                         -H \"Content-Type: application/json\" \
                         -X POST \
                         -d '{}' \
                         {}".format(cfg, url_add)

        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode:
            raise Exception("Failed to configure EM: {}".format(result.stderr.decode("utf-8")))

        return result.stdout

    def execute_rpc(self, cfg=None) -> tuple[Union[str, Any], Union[str, Any], Union[str, Any]]:

        result = self.set_restconf(cfg)

        error_tag, error_message, error_path = "", "", ""

        if len(result) != 0:
            jsonroot = json.loads(result.decode('utf-8'))

            if "ietf-restconf:errors" in jsonroot:
                if "error" in jsonroot["ietf-restconf:errors"]:
                    for error in jsonroot["ietf-restconf:errors"]["error"]:
                        if error is None:
                            continue
                        if "error-tag" in error:
                            error_tag = error["error-tag"]
                        if "error-message" in error:
                            error_message = error["error-message"]
                        if "error-path" in error:
                            error_path = error["error-path"]

        return error_tag, error_message, error_path


def set_restconf(data: str, url: str, path: str) -> bytes:
    url_path = f'http://{url}:81/restconf/' + path
    command = "curl -u admin:admin \
                     -H \"Accept: application/yang-data+json\" \
                     -H \"Content-Type: application/json\" \
                     -X POST \
                     -d '{}' \
                     {}".format(data, url_path)

    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        raise Exception("Failed to configure EM: {}".format(result.stderr.decode("utf-8")))

    return result.stdout


def execute_rpc(cfg, url, path) -> tuple[Union[str, Any], Union[str, Any], Union[str, Any]]:

    result = set_restconf(data=cfg, url=url, path=path)

    error_tag, error_message, error_path = "", "", ""

    if len(result) != 0:
        jsonroot = json.loads(result.decode('utf-8'))

        if "ietf-restconf:errors" in jsonroot:
            if "error" in jsonroot["ietf-restconf:errors"]:
                for error in jsonroot["ietf-restconf:errors"]["error"]:
                    if error is None:
                        continue
                    if "error-tag" in error:
                        error_tag = error["error-tag"]
                    if "error-message" in error:
                        error_message = error["error-message"]
                    if "error-path" in error:
                        error_path = error["error-path"]

    return error_tag, error_message, error_path
