import requests
import json

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


class FeedStock(object):

    def __init__(self, pid, source_dir):
        self._xml = loadXML(pid)
        self._raw_data = load_rawdata(pid)
        self._pid = pid
