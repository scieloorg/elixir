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


def list_document_images(source):
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
        html_images = list_document_images(source)
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


def list_path(path):

    try:
        files = os.listdir(path)
        logging.info('Source directory found (%s)' % path)
    except FileNotFoundError:
        logging.error('Source directory not found (%s)' % path)
        raise FileNotFoundError(
            u'Source directory does not exists: %s' % path
        )

    return files


class Article(object):

    def __init__(self, pid, xml, raw_data, source_dir):

        if not is_valid_pid(pid):
            raise ValueError(u'Invalid PID: %s' % pid)

        try:
            os.listdir(source_dir)
            logging.info('Source directory found (%s)' % source_dir)
        except FileNotFoundError:
            logging.error('Source directory not found (%s)' % source_dir)
            raise FileNotFoundError(u'Invalid source directory: %s' % source_dir)

        self.source_dir = source_dir
        self.xml = xml
        self.xylose = raw_data
        self.pid = pid

        logging.info('Issue label for source files is (%s)' % self.issue_label)
        logging.info('Journal acronym for source files is (%s)' % self.journal_acronym)
        logging.info('Content version (%s)' % self.content_version)

    @property
    def list_images(self):

        path = '/'.join(
            [self.source_dir, 'img', self.journal_acronym, self.issue_label]
        )

        #return [x for x in list_path(path) if x in list_document_images('ss')]
        return list_path(path)

    @property
    def list_pdfs(self):

        path = '/'.join(
            [self.source_dir, 'pdf', self.journal_acronym, self.issue_label]
        )

        return [x for x in list_path(path) if self.file_code in x]

    @property
    def list_htmls(self):

        path = '/'.join(
            [self.source_dir, 'html', self.journal_acronym, self.issue_label]
        )

        return [x for x in list_path(path) if self.file_code in x]

    @property
    def list_xmls(self):

        path = '/'.join(
            [self.source_dir, 'xml', self.journal_acronym, self.issue_label]
        )

        return [x for x in list_path(path) if self.file_code in x]

    @property
    def list_documents(self):
        """
        This method retrieve the html's or xml's according to the vesion of the
        given document.
        """

        if self.content_version == 'sps':
            return self.list_xmls
        else:
            return self.list_htmls

    @property
    def journal_acronym(self):
        ja = self.xylose.journal_acronym

        return ja

    @property
    def file_code(self):
        return self.xylose.file_code

    @property
    def content_version(self):
        """
        This method retrieve the version of the document. If the file with
        the document content is an XML SPS, the method will retrieve 'rsps',
        otherwise, if the file is an html the method will retrieve 'legacy'.
        This is checked using the file extension of do path stored into the
        field v702.
        """

        extension = self.xylose.data['article']['v702'][0]['_'].split('.')[-1]

        version = 'legacy'

        if extension == 'xml':
            version = 'sps'

        return version

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

        if self.xylose.issue == 'ahead':
            issue_dir += self.xylose.publication_date[0:4]

        if self.xylose.volume:
            issue_dir += 'v%s' % self.xylose.volume

        if self.xylose.supplement_volume:
            issue_dir += 's%s' % self.xylose.supplement_volume

        if self.xylose.issue:
            issue_dir += 'n%s' % self.xylose.issue

        if self.xylose.supplement_issue:
            issue_dir += 's%s' % self.xylose.supplement_issue

        if self.xylose.document_type == 'press-release':
            issue_dir += 'pr'

        issue_label = issue_dir.lower()

        return issue_label

    def images(self):
        pass

    def pdfs(self):
        pass

    def images_status(self):
        pass

    def build_package(self, deposit_path):
        pass