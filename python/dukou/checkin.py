import logging

def config_log(file_path: str, logger_name: str):
    """config log output, contains handler, formatter etc."""
    log_file = Path(file_path).expanduser()
    mkdir_log_directory(log_file)
    touch_log_file(log_file)

    logger = logging.getLogger(logger_name)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format_str = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(format_str, date_format_str)
    file_handler.setFormatter(formatter)

    logger.setLevel(logging.DEBUG)

import logging
from pathlib import Path


def mkdir_log_directory(log_file: Path) -> bool:
    log_directory = Path(log_file.parent)
    if not log_directory.exists():
        log_directory.mkdir(parents=True)

    return True


def touch_log_file(log_file: Path) -> bool:
    if not log_file.exists():
        log_file.touch()

    return True




import logging
import sys

import requests
from requests.exceptions import RequestException


class DukouSpider:
    """dukou vpn daily checkin"""

    header = {
        "origin": "https://dukou.dev",
        "referer": "https://dukou.dev/user/login?redirect=%2F",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    }

    # proxies = {
    #     "http": "http://127.0.0.1:7890",
    #     "https": "http://127.0.0.1:7890",
    # }

    def __init__(self, email: str, passwd: str):
        self.payload = {"email": email, "passwd": passwd}
        self.login_url = "https://dukou.dev/api/token"
        self.checkin_url = "https://dukou.dev/api/user/checkin"
        self.logger = logging.getLogger("dukou.spider")

    def get_access_token(self) -> str:
        """get access token"""
        try:
            resp = requests.post(
                self.login_url,
                data=self.payload,
                headers=self.header,
                # proxies=self.proxies,
            )
        except RequestException as exception:
            self.logger.error(
                "An http error occured, the program quit abnormally: %s", exception
            )
            sys.exit(1)

        content = resp.json()
        # login falied
        if content["ret"] != 1:
            self.logger.error("login falied, msg: %s", content["msg"])
            sys.exit(1)

        self.logger.info("login successful: %s", content)
        return content["token"]

    def checkin(self):
        try:
            resp = requests.get(
                self.checkin_url, headers=self.header, 
            )
        except RequestException as exception:
            self.logger.error(
                "An http error occured, the program quit abnormally: %s", exception
            )
            sys.exit(1)

        # 接口请求失败的情况下，状态码是正常的，却没有响应体
        if len(resp.content) == 0:
            self.logger.error("checkin falied, please check access-token header")

        self.logger.info("checkin successful, msg: %s", resp.json())

    def run(self):
        token = self.get_access_token()
        self.header["access-token"] = token
        self.logger.info("http headers: %s", self.header)
        self.checkin()


import logging
import sys
from typing import Dict

import yaml


class YAMLReader:
    """Read account config from YAML file"""

    def __init__(self, config_file: str):
        self.config_file = config_file
        self.logger = logging.getLogger("dukou.reader")

    def get_file_content(self) -> str:
        """Read file content"""
        self.logger.info("read config file [%s]", self.config_file)
        with open(
            self.config_file,
            "r",
            encoding="utf-8",
        ) as file:
            content = file.read()

        if len(content) == 0:
            self.logger.error("config file error, there is nothing data")
            sys.exit(1)
        return content

    def _schema_validation(self, content: dict):
        """Schema Validation, config file format must be like this
        account:
            -
                email: example@github.com
                passwd: your_passwd
        """
        if not content["account"]:
            self.logger.error("config format error please check it")
            sys.exit(1)

        for account in content["account"]:
            if not (account["email"] and account["passwd"]):
                self.logger.error("maybe you forgot to fill email or passwd")
                sys.exit(1)

    def read_config(self) -> Dict[str, str]:
        """Parse the YAML document to the corresponding Python object"""
        file_content = self.get_file_content()
        yaml_content = yaml.safe_load(file_content)
        self._schema_validation(yaml_content)

        return yaml_content["account"]
    




def main():
    logger = logging.getLogger("dukou.main")
    logger.info("==========开始每日签到==========")
    reader = YAMLReader("config.yaml")
    account_data = reader.read_config()
    index = 1
    for account in account_data:
        logger.info("==========签到第 %s 个账号==========", index)
        dukou = DukouSpider(account["email"], account["passwd"])
        dukou.run()
        index += 1
    logger.info("==========签到完成==========")


if __name__ == "__main__":
    config_log("~/.logs/dukou/dukou.log", "dukou")
    main()
