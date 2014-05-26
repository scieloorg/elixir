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


def get_document_images(document):
    """
    This method retrieve a list of images paths founded into a HTML.

    Keyword arguments:
    document -- could be a valid file path to a HTML document or a string withing an HTML.
    """
    images_regex = re.compile(u'["\'](/img.*?|\\\\img.*?)["\']', re.IGNORECASE)

    try:
        html = read_html(document)
    except FileNotFoundError:
        html = document

    images = images_regex.findall(html)

    fixed_slashs = [x.replace('\\', '/').split('/')[-1] for x in images]

    return fixed_slashs


def check_images_availability(available_images, document_images):

    if isinstance(document_images, list):
        html_images = document_images
    elif isinstance(document_images, str):
        html_images = get_document_images(document_images)
    else:
        raise ValueError('Expected a list of images or a string with an html document, given: %s' % source)

    images_availability = []

    for image in html_images:
        if image in [x.split('/')[-1] for x in available_images]:
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
        self.issue_label = self._issue_label()
        self.journal_acronym = self._journal_acronym()
        self.content_version = self._content_version()
        self.file_code = self._file_code()

    def _journal_acronym(self):
        ja = self.xylose.journal_acronym

        logging.info('Journal acronym for source files is (%s)' % ja)

        return ja

    def _file_code(self):

        logging.info('File code is (%s)' % self.xylose.file_code)

        return self.xylose.file_code

    def _content_version(self):
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

        logging.info('Content version (%s)' % version)

        return version

    def _issue_label(self):
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

        logging.info('Issue label for source files is (%s)' % issue_label)

        return issue_label

    @property
    def list_source_images(self):

        path = '/'.join(
            [self.source_dir, 'img', self.journal_acronym, self.issue_label]
        )

        images = ['/'.join([path, x]) for x in list_path(path)]

        if len(images) == 0:
            logging.info('No source images available for the issue (%s)' % self.issue_label)

        for image in images:
            logging.info('Image (%s) available in source for the issue (%s)' % (image, self.issue_label))

        return images

    @property
    def list_document_images(self):

        doc_images = []
        if self.content_version == 'sps':
            pass
        else:
            for document in self.list_documents:
                doc_images += get_document_images(document)

        if len(doc_images) == 0:
            logging.info('Images not required for (%s)' % (self.pid))

        for image in doc_images:
            logging.info('Image (%s) required for (%s)' % (image, self.pid))

        return doc_images

    @property
    def list_pdfs(self):

        path = '/'.join(
            [self.source_dir, 'pdf', self.journal_acronym, self.issue_label]
        )

        pdfs = ['/'.join([path, x]) for x in list_path(path) if self.file_code in x]

        if len(pdfs) == 0:
            logging.warning('PDF not found for (%s)' % self.pid)

        for pdf in pdfs:
            logging.info('PDF (%s) found for (%s)' % (pdf, self.pid))

        return pdfs

    @property
    def list_htmls(self):

        path = '/'.join(
            [self.source_dir, 'html', self.journal_acronym, self.issue_label]
        )

        htmls = ['/'.join([path, x]) for x in list_path(path) if self.file_code in x]

        if len(htmls) == 0:
            logging.warning('HTML not found for (%s)' % self.pid)

        for html in htmls:
            logging.info('HTML (%s) found for (%s)' % (html, self.pid))

        return htmls

    @property
    def list_xmls(self):

        path = '/'.join(
            [self.source_dir, 'xml', self.journal_acronym, self.issue_label]
        )

        xmls = ['/'.join([path, x]) for x in list_path(path) if self.file_code in x]

        if len(xmls) == 0:
            logging.warning('XML not found for (%s)' % self.pid)

        for xml in xmls:
            logging.info('XML (%s) found for (%s)' % (xml, self.pid))

        return xmls

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
    def images_status(self):
        return check_images_availability(self.list_source_images, self.list_document_images)

    def build_package(self, deposit_path):
        pass