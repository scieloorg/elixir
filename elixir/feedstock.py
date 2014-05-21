import requests
import json
import re
import os
import sys
import re
import logging

try:  # Keep compatibility with python 2.7
    from html import unescape
except ImportError:
    from HTMLParser import HTMLParser

from xylose import scielodocument

# --------------
# Py2 compat
# --------------
PY2 = sys.version_info[0] == 2

if PY2:
    html_parser = HTMLParser().unescape
else:
    html_parser = unescape
# --------------


def html_decode(string):

    try:
        string = html_parser(string)
        logging.info('HTML entities replaced')
    except:
        logging.info('Unable to replace the HTML entities')
        return string

    return string


def loadXML(pid):
    url = 'http://192.168.1.162:7000/api/v1/article?code=%s&format=xmlwos' % pid
    try:
        xml = requests.get(
            url,
            timeout=3
        ).text.strip()
        logging.info('XML retrieved from (%s)' % url)
    except:
        logging.error('Timeout opening (%s)' % url)

    return xml


def load_rawdata(pid):
    url = 'http://192.168.1.162:7000/api/v1/article?code=%s' % pid
    try:
        json_data = json.loads(
            requests.get(
                url,
                timeout=3
            ).text.strip()
        )
        logging.info('JSON data retrieved from (%s)' % url)
    except:
        logging.error('Timeout opening (%s)' % 'http://192.168.1.162:7000/api/v1/article?code=%s&format=xmlwos' % pid)

    try:
        rawdata = scielodocument.Article(json_data)
        logging.info('JSON data parsed')
    except:
        logging.error('Unable to parse json retrieved by (%s)' % url)

    return rawdata


def is_valid_pid(pid):
    pid_regex = re.compile("^S[0-9]{4}-[0-9]{3}[0-9xX][0-2][0-9]{3}[0-9]{4}[0-9]{5}$", re.IGNORECASE)

    if pid_regex.search(pid) is None:
        logging.error('Invalid PID (%s)' % pid)
        return False

    logging.info('Valid PID (%s)' % pid)

    return True


def read_html(html_file, replace_entities=False):
    """
    This method retrieve the HTML string of a given HTML file.

    Keyword arguments:
    html_file -- complete path to the HTML file.
    replace_entities -- a boolean to set if the HTML will be retrived replacing the entities or not, default is False.
    """
    images_regex = re.compile(u'<body>(.*?)</body>', re.IGNORECASE)

    try:
        html = open(html_file, 'r').read()
        logging.info('Local HTML file readed (%s)' % html_file)
    except FileNotFoundError:
        logging.error('Unable to read file (%s)' % html_file)
        raise FileNotFoundError(
            u'HTML file does not exists: %s' % html_file
        )

    if not replace_entities:
        return html

    html = html_decode(html)

    return images_regex.findall(html)[0]


def list_html_images(source):
    """
    This method retrieve a list of images paths founded into a HTML.

    Keyword arguments:
    source -- could be a valid file path to a HTML document or a string withing an HTML.
    """
    images_regex = re.compile(u'["\'](/img.*?)["\']', re.IGNORECASE)

    try:
        html = read_html(source)
    except FileNotFoundError:
        html = source

    return images_regex.findall(html)


def check_images_availability(source, available_images):

    if isinstance(source, list):
        html_images = source
    elif isinstance(source, str):
        html_images = list_html_images(source)
    else:
        raise ValueError('Expected a list of images or a string with an html document, given: %s' % source)

    images_availability = []
    for image in html_images:
        if image in available_images:
            logging.info('Image available in the file system (%s)' % image)
            images_availability.append((image, True))
        else:
            logging.warning('Image not available in the file system (%s)' % image)
            images_availability.append((image, False))

    return images_availability


class SourceFiles(object):

    def __init__(self, source_dir):

        try:
            os.listdir(source_dir)
            logging.info('Source directory found (%s)' % source_dir)
        except FileNotFoundError:
            logging.error('Source directory not found (%s)' % source_dir)
            raise FileNotFoundError(u'Invalid source directory: %s' % source_dir)

        self._source_dir = source_dir

    def list_images(self, journal_acronym, issue_label):

        imgs_dir = '/'.join(
            [self._source_dir, 'img', journal_acronym, issue_label]
        )

        try:
            files = os.listdir(imgs_dir)
            logging.info('Images source directory found (%s)' % imgs_dir)
        except FileNotFoundError:
            logging.error('Images source directory not found (%s)' % imgs_dir)
            raise FileNotFoundError(
                u'Image directory does not exists: %s' % imgs_dir
            )

        return files

    def list_pdfs(self, journal_acronym, issue_label):

        pdfs_dir = '/'.join(
            [self._source_dir, 'pdf', journal_acronym, issue_label]
        )

        try:
            files = os.listdir(pdfs_dir)
            logging.info('PDF\'s source directory found (%s)' % pdfs_dir)
        except FileNotFoundError:
            logging.error('PDF\'s source directory not found (%s)' % pdfs_dir)
            raise FileNotFoundError(
                u'PDF directory does not exists: %s' % pdfs_dir
            )

        return files

    def list_htmls(self, journal_acronym, issue_label):

        htmls_dir = '/'.join(
            [self._source_dir, 'html', journal_acronym, issue_label]
        )

        try:
            files = os.listdir(htmls_dir)
            logging.info('PDF\'s source directory found (%s)' % htmls_dir)
        except FileNotFoundError:
            raise FileNotFoundError(
                u'HTML directory does not exists: %s' % htmls_dir
            )
            logging.error('PDF\'s source directory not found (%s)' % htmls_dir)

        return files


class MetaData(object):

    def __init__(self, pid):

        if not is_valid_pid(pid):
            raise ValueError(u'Invalid PID: %s' % pid)

        self._xml = loadXML(pid)
        self._raw_data = load_rawdata(pid)
        self._pid = pid
        logging.info('Issue label  for source files is (%s)' % self.issue_label)
        logging.info('Journal acronym for source files is (%s)' % self.journal_acronym)

    @property
    def xml(self):
        return self._xml

    @property
    def pid(self):
        return self._pid

    @property
    def journal_acronym(self):
        ja = self._raw_data.journal_acronym

        return ja

    @property
    def file_code(self):
        return self._raw_data.file_code

    @property
    def issue_label(self):
        """
        This method retrieve the name of the directory, where the article
        store the static files. The name is returned in compliance with
        the SciELO patterns. Once this pattern is controlled manually in
        the file system, this method maybe not find a related static
        directory for some articles.
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

        issue_label = issue_dir.lower()

        return issue_label

    @property
    def xylose(self):
        return self._raw_data


class Article(object):
    def __init__(self, pid, source_dir):
        self.metadata = MetaData(pid)
        self.sourcefiles = SourceFiles(source_dir)
