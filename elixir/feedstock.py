import requests
import json
import re

from xylose.scielodocument import Article


def loadXML(pid):
    xml = requests.get(
        'http://192.168.1.162:7000/api/v1/article?code=%s&format=xmlwos' % pid,
        timeout=3
    ).text.strip()

    return xml


def load_rawdata(pid):

    json_data = json.loads(
        requests.get(
            'http://192.168.1.162:7000/api/v1/article?code=%s' % pid,
            timeout=3
        ).text.strip()
    )

    rawdata = Article(json_data)

    return rawdata


def is_valid_pid(pid):
    pid_regex = re.compile("^S[0-9]{4}-[0-9]{3}[0-9xX][0-2][0-9]{3}[0-9]{4}[0-9]{5}$")

    if pid_regex.search(pid) is None:
        return False

    return True


class FeedStock(object):

    def __init__(self, pid, source_dir):

        if not is_valid_pid:
            raise ValueError('Invalid PID: %' % pid)

        self._xml = loadXML(pid)
        self._raw_data = load_rawdata(pid)
        self._pid = pid
        self._source_dir = source_dir
