import requests
import json
import re
import os

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


class SourceFiles(object):

    def __init__(self, source_dir):

        try:
            os.listdir(source_dir)
        except FileNotFoundError:
            raise FileNotFoundError(u'Invalid source directory: %s' % source_dir)

        self._source_dir = source_dir

    def list_images(self, journal_acronym, issue_label):

        imgs_dir = '/'.join([self._source_dir, 'img/revistas', journal_acronym, issue_label])

        try:
            files = os.listdir(imgs_dir)
        except FileNotFoundError:
            raise FileNotFoundError(u'Image directory does not exists: %s' % imgs_dir)

        return files

    def list_pdfs(self, journal_acronym, issue_label):

        imgs_dir = '/'.join([self._source_dir, 'pdf', journal_acronym, issue_label])

        try:
            files = os.listdir(imgs_dir)
        except FileNotFoundError:
            raise FileNotFoundError(u'PDF directory does not exists: %s' % imgs_dir)

        return files

    def list_htmls(self, journal_acronym, issue_label):

        imgs_dir = '/'.join([self._source_dir, 'translations', journal_acronym, issue_label])

        try:
            files = os.listdir(imgs_dir)
        except FileNotFoundError:
            raise FileNotFoundError(u'HTML directory does not exists: %s' % imgs_dir)

        return files


class MetaData(object):

    def __init__(self, pid, source_dir):

        if not is_valid_pid(pid):
            raise ValueError(u'Invalid PID: %s' % pid)

        self._xml = loadXML(pid)
        self._raw_data = load_rawdata(pid)
        self._pid = pid

    @property
    def xml(self):
        return self._xml

    @property
    def pid(self):
        return self._pid

    @property
    def journal_acronym(self):
        return self._raw_data.journal_acronym

    @property
    def issue_label(self):
        """
        This method retrieve the name of the directory, where the article
        store the static files. The name is returned in compliance with
        the SciELO patterns. Once this pattern is controlled manually in
        the file system, this method maybe not find a related static directory
        for some articles.
        """

        issue_dir = ''

        if self._raw_data.issue == 'ahead':
            issue_dir += self._raw_data.publication_date[0:4]

        if self._raw_data.volume:
            issue_dir += 'v%s' % self._raw_data.volume

        if self._raw_data.supplement_volume:
            issue_dir += 's%s' % self._raw_data.supplement_volume

        if self._raw_data.issue:
            issue_dir += 'n%s' % self._raw_data.issue

        if self._raw_data.supplement_issue:
            issue_dir += 's%s' % self._raw_data.supplement_issue

        if self._raw_data.document_type == 'press-release':
            issue_dir += 'pr'

        return issue_dir.lower()

    @property
    def xylose(self):
        return self._raw_data











