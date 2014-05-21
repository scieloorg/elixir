import unittest
import requests
import os

try:
    from unittest import mock
except ImportError:
    import mock

from elixir import feedstock

document_xml = document_json = source_dir = None


def setupModule():
    global document_xml, document_json, source_dir

    with open(os.path.dirname(__file__) + '/fixtures/document.xml', 'r') as fp:
        document_xml = fp.read().strip()

    with open(os.path.dirname(__file__) + '/fixtures/document.json', 'r') as fp:
        document_json = fp.read().strip()

    source_dir = os.path.dirname(__file__) + '/files'


class ElixirTests(unittest.TestCase):

    def test_loadXML(self):

        with unittest.mock.patch('requests.get'):
            rqts = requests.get(u'ANY URL')
            rqts.text = document_xml
            fs = feedstock.loadXML(u'S0034-89102013000400674')

        self.assertEqual(fs[0:20], u'<articles dtd-versio')

    def test_load_rawdata(self):

        with unittest.mock.patch('requests.get'):
            rqts = requests.get(u'ANY URL')
            rqts.text = document_json
            fs = feedstock.load_rawdata(u'S0034-89102013000400674')

        self.assertEqual(
            fs.original_title(),
            u'Avaliacao da confiabilidade e validade do Indice de Qualidade da Dieta Revisado'
        )

    def test_is_valid_pid(self):

        self.assertTrue(feedstock.is_valid_pid(u'S0034-89102013000400674'))

    def test_is_valid_pid_with_invalid_data(self):

        self.assertFalse(feedstock.is_valid_pid(u'S003489102013000400674'))

    def test_read_html_invalid_path(self):

        with self.assertRaises(FileNotFoundError):
            html = feedstock.read_html('xxxx')

    def test_list_html_images(self):

        images = feedstock.list_html_images(source_dir+'/html/rsp/v40n6/en_07.htm')

        self.assertTrue(u'/img/revistas/rsp/v40n6/e07f1.gif' in images)

    def test_check_images_availability(self):

        html_images = ['a', 'b', 'c']

        file_system_images = ['b', 'c', 'd', 'e']

        result = feedstock.check_images_availability(html_images, file_system_images)

        expected = [('a', False), ('b', True), ('c', True)]

        self.assertEqual(expected, result)

    def test_check_images_availability_with_a_html(self):

        html = """
            <html>
                <img src="/img/revistas/rsp/01.gif" />
                <img src="/img/revistas/rsp/02.jpg" />
                <a href="/img/revistas/rsp/03.gif">Blaus</a>
                <a href="/img/revistas/rsp/04.gif">Picles</a>
            </html>
        """

        file_system_images = [
            '/img/revistas/rsp/01.gif',
            '/img/revistas/rsp/02.jpg',
            '/img/revistas/rsp/03.gif',
            '/img/revistas/rsp/05.gif',
            '/img/revistas/rsp/06.gif'
        ]

        result = feedstock.check_images_availability(html, file_system_images)

        expected = [
            ('/img/revistas/rsp/01.gif', True),
            ('/img/revistas/rsp/02.jpg', True),
            ('/img/revistas/rsp/03.gif', True),
            ('/img/revistas/rsp/04.gif', False),
        ]

        self.assertEqual(expected, result)


class SourceFiles(unittest.TestCase):

    def setUp(self):
        self._source_files = feedstock.SourceFiles(source_dir)

    def test_instanciating(self):

        self.assertTrue(isinstance(self._source_files, feedstock.SourceFiles))

    def test_instanciating_invalid_source_dir(self):

        with self.assertRaises(FileNotFoundError):
            fs = feedstock.SourceFiles('invalid_source_dir')

    def test_list_images(self):
        images = self._source_files.list_images('rsp', 'v40n6')

        self.assertEqual(len(images), 121)

    def test_list_images_without_files(self):
        images = self._source_files.list_images('rsp', 'v40n7')

        self.assertEqual(images, [])

    def test_list_images_invalid_path(self):

        with self.assertRaises(FileNotFoundError):
            images = self._source_files.list_images('rsp', 'xxxx')

    def test_list_pdfs(self):
        images = self._source_files.list_pdfs('rsp', 'v40n6')

        self.assertEqual(len(images), 36)

    def test_list_pdfs_without_files(self):
        images = self._source_files.list_pdfs('rsp', 'v40n7')

        self.assertEqual(images, [])

    def test_list_pdfs_invalid_path(self):

        with self.assertRaises(FileNotFoundError):
            images = self._source_files.list_pdfs('rsp', 'xxxx')

    def test_list_htmls(self):
        images = self._source_files.list_htmls('rsp', 'v40n6')

        self.assertEqual(len(images), 13)

    def test_list_htmls_without_files(self):
        images = self._source_files.list_htmls('rsp', 'v40n7')

        self.assertEqual(images, [])

    def test_list_htmls_invalid_path(self):

        with self.assertRaises(FileNotFoundError):
            htmls = self._source_files.list_htmls('rsp', 'xxxx')


class MetaDataTests(unittest.TestCase):

    def setUp(self):

        with unittest.mock.patch('requests.get'):
            rqts = requests.get(u'ANY URL')
            rqts.text = document_xml
            rqts = requests.get(u'ANY URL')
            rqts.text = document_json
            fs = feedstock.MetaData(u'S0034-89102013000400674')

        self._fs = fs

    def test_instanciating(self):

        self.assertEqual(self._fs._pid, u'S0034-89102013000400674')

    def test_instanciating_invalid_pid(self):

        with self.assertRaises(ValueError):
            fs = feedstock.MetaData(u'S003489102013000400674')

    def test_file_code(self):

        self.assertEqual(self._fs.file_code, u'0034-8910-rsp-47-04-0675')

    def test_pid(self):

        self.assertEqual(self._fs.pid, u'S0034-89102013000400674')

    def test_acronym(self):

        self.assertEqual(self._fs.journal_acronym, u'rsp')

    def test_issue_label_volume_number(self):
        self._fs._raw_data.data = {
            'article': {'v31': [{'_': 10}], 'v32': [{'_': 12}], 'v65': [{'_': '2014'}]},
            'title': {},
            'citations': []
        }

        self.assertEqual(self._fs.issue_label, u'v10n12')

    def test_issue_label_volume_number_pr(self):
        self._fs._raw_data.data = {
            'article': {'v31': [{'_': 10}], 'v32': [{'_': 12}], 'v71': [{'_': 'pr'}], 'v65': [{'_': '2014'}]},
            'title': {},
            'citations': []
        }

        self.assertEqual(self._fs.issue_label, u'v10n12pr')

    def test_issue_label_volume_suppl_number(self):
        self._fs._raw_data.data = {
            'article': {'v31': [{'_': 10}], 'v132': [{'_': 12}], 'v65': [{'_': '2014'}]},
            'title': {},
            'citations': []
        }

        self.assertEqual(self._fs.issue_label, u'v10s12')

    def test_issue_label_ahead(self):
        self._fs._raw_data.data = {
            'article': {'v32': [{'_': 'ahead'}], 'v65': [{'_': '2014'}]},
            'title': {},
            'citations': []
        }

        self.assertEqual(self._fs.issue_label, u'2014nahead')

    def test_issue_label_ahead(self):
        self._fs._raw_data.data = {
            'article': {'v32': [{'_': 'ahead'}], 'v65': [{'_': '2014'}], 'v71': [{'_': 'pr'}]},
            'title': {},
            'citations': []
        }

        self.assertEqual(self._fs.issue_label, u'2014naheadpr')
