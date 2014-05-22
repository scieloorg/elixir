import unittest
import requests
import os
import json

try:
    from unittest import mock
except ImportError:
    import mock

from elixir import feedstock
from xylose import scielodocument

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

    def test_read_document_invalid_path(self):

        with self.assertRaises(FileNotFoundError):
            html = feedstock.read_html('xxxx')

    def test_list_document_images(self):

        images = feedstock.list_document_images(source_dir+'/html/rsp/v40n6/en_07.htm')

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


class Article(unittest.TestCase):

    def setUp(self):
        raw_data = scielodocument.Article(json.loads(document_json))
        self._article = feedstock.Article(
            'S0034-89102013000400674',
            document_xml,
            raw_data,
            source_dir
            )

    def test_instanciating(self):

        self.assertEqual(self._article.pid, u'S0034-89102013000400674')

    def test_instanciating_invalid_source_dir(self):
        raw_data = scielodocument.Article(json.loads(document_json))

        with self.assertRaises(FileNotFoundError):
            fs = feedstock.Article(
                'S0034-89102013000400674',
                document_xml,
                raw_data,
                'invalid_source_dir'
            )

    def test_instanciating_invalid_pid(self):
        raw_data = scielodocument.Article(json.loads(document_json))

        with self.assertRaises(ValueError):
            fs = feedstock.Article(
                'S003489102013000400674',
                document_xml,
                raw_data,
                '.'
            )

    def test_version(self):

        version = self._article.content_version

        self.assertEqual(version, 'sps')

    def test_version(self):
        self._article.xylose.data['title']['v68'][0]['_'] = 'rsp'
        self._article.xylose.data['article']['v31'][0]['_'] = '40'
        self._article.xylose.data['article']['v32'][0]['_'] = '6'
        self._article.xylose.data['article']['v65'][0]['_'] = '2014'
        self._article.xylose.data['article']['v702'][0]['_'] = '/x/x/y/z/file.htm'
        version = self._article.content_version

        self.assertEqual(version, 'legacy')

    def test_list_images(self):
        self._article.xylose.data['title']['v68'][0]['_'] = 'rsp'
        self._article.xylose.data['article']['v31'][0]['_'] = '40'
        self._article.xylose.data['article']['v32'][0]['_'] = '6'
        self._article.xylose.data['article']['v65'][0]['_'] = '2014'

        images = self._article.list_images

        self.assertEqual(len(images), 121)

    def test_list_images_without_files(self):
        self._article.xylose.data['title']['v68'][0]['_'] = 'rsp'
        self._article.xylose.data['article']['v31'][0]['_'] = '40'
        self._article.xylose.data['article']['v32'][0]['_'] = '7'
        self._article.xylose.data['article']['v65'][0]['_'] = '2014'

        images = self._article.list_images

        self.assertEqual(images, [])

    def test_list_images_invalid_path(self):
        self._article.xylose.data['title']['v68'][0]['_'] = 'rsp'
        self._article.xylose.data['article']['v31'][0]['_'] = 'xx'
        self._article.xylose.data['article']['v32'][0]['_'] = 'xx'
        self._article.xylose.data['article']['v65'][0]['_'] = '2014'
        self._article.xylose.data['article']['v702'][0]['_'] = '/'

        with self.assertRaises(FileNotFoundError):
            images = self._article.list_images

    def test_list_pdfs(self):
        self._article.xylose.data['title']['v68'][0]['_'] = 'rsp'
        self._article.xylose.data['article']['v31'][0]['_'] = '40'
        self._article.xylose.data['article']['v32'][0]['_'] = '6'
        self._article.xylose.data['article']['v65'][0]['_'] = '2014'
        self._article.xylose.data['article']['v702'][0]['_'] = '/x/x/y/z/07.htm'

        images = self._article.list_pdfs

        self.assertEqual(len(images), 2)

    def test_list_pdfs_without_files(self):
        self._article.xylose.data['title']['v68'][0]['_'] = 'rsp'
        self._article.xylose.data['article']['v31'][0]['_'] = '40'
        self._article.xylose.data['article']['v32'][0]['_'] = '7'
        self._article.xylose.data['article']['v65'][0]['_'] = '2014'
        self._article.xylose.data['article']['v702'][0]['_'] = '/x/x/y/z/07.htm'

        images = self._article.list_pdfs

        self.assertEqual(images, [])

    def test_list_pdfs_invalid_path(self):
        self._article.xylose.data['title']['v68'][0]['_'] = 'rsp'
        self._article.xylose.data['article']['v31'][0]['_'] = 'xx'
        self._article.xylose.data['article']['v32'][0]['_'] = 'xx'
        self._article.xylose.data['article']['v65'][0]['_'] = '2014'
        self._article.xylose.data['article']['v702'][0]['_'] = '/x/x/y/z/07.htm'

        with self.assertRaises(FileNotFoundError):
            images = self._article.list_pdfs

    def test_list_htmls(self):
        self._article.xylose.data['title']['v68'][0]['_'] = 'rsp'
        self._article.xylose.data['article']['v31'][0]['_'] = '40'
        self._article.xylose.data['article']['v32'][0]['_'] = '6'
        self._article.xylose.data['article']['v65'][0]['_'] = '2014'
        self._article.xylose.data['article']['v702'][0]['_'] = '/x/x/y/z/07.htm'

        htmls = self._article.list_htmls

        self.assertEqual(len(htmls), 2)

    def test_list_htmls_without_files(self):
        self._article.xylose.data['title']['v68'][0]['_'] = 'rsp'
        self._article.xylose.data['article']['v31'][0]['_'] = '40'
        self._article.xylose.data['article']['v32'][0]['_'] = '7'
        self._article.xylose.data['article']['v65'][0]['_'] = '2014'
        self._article.xylose.data['article']['v702'][0]['_'] = '/x/x/y/z/07.htm'

        htmls = self._article.list_htmls

        self.assertEqual(htmls, [])

    def test_list_htmls_invalid_path(self):
        self._article.xylose.data['title']['v68'][0]['_'] = 'rsp'
        self._article.xylose.data['article']['v31'][0]['_'] = 'xx'
        self._article.xylose.data['article']['v32'][0]['_'] = 'xx'
        self._article.xylose.data['article']['v65'][0]['_'] = '2014'
        self._article.xylose.data['article']['v702'][0]['_'] = '/x/x/y/z/07.htm'

        with self.assertRaises(FileNotFoundError):
            self._article.list_htmls

    def test_list_xmls(self):
        xmls = self._article.list_xmls

        self.assertEqual(xmls[0], '0034-8910-rsp-47-04-0675.xml')

    def test_list_xmls_without_files(self):
        self._article.xylose.data['title']['v68'][0]['_'] = 'rsp'
        self._article.xylose.data['article']['v31'][0]['_'] = '47'
        self._article.xylose.data['article']['v32'][0]['_'] = '1'
        self._article.xylose.data['article']['v65'][0]['_'] = '2014'
        self._article.xylose.data['article']['v702'][0]['_'] = '/x/x/y/z/07.htm'

        xmls = self._article.list_xmls

        self.assertEqual(xmls, [])

    def test_list_xmls_invalid_path(self):
        self._article.xylose.data['title']['v68'][0]['_'] = 'rsp'
        self._article.xylose.data['article']['v31'][0]['_'] = 'xx'
        self._article.xylose.data['article']['v32'][0]['_'] = 'xx'
        self._article.xylose.data['article']['v65'][0]['_'] = '2014'
        self._article.xylose.data['article']['v702'][0]['_'] = '/x/x/y/z/07.htm'

        with self.assertRaises(FileNotFoundError):
            self._article.list_xmls

    def test_file_code(self):

        self.assertEqual(self._article.file_code, u'0034-8910-rsp-47-04-0675')

    def test_pid(self):

        self.assertEqual(self._article.pid, u'S0034-89102013000400674')

    def test_acronym(self):

        self.assertEqual(self._article.journal_acronym, u'rsp')

    def test_issue_label_volume_number(self):
        self._article.xylose.data = {
            'article': {'v31': [{'_': 10}], 'v32': [{'_': 12}], 'v65': [{'_': '2014'}]},
            'title': {},
            'citations': []
        }

        self.assertEqual(self._article.issue_label, u'v10n12')

    def test_issue_label_volume_number_pr(self):
        self._article.xylose.data = {
            'article': {'v31': [{'_': 10}], 'v32': [{'_': 12}], 'v71': [{'_': 'pr'}], 'v65': [{'_': '2014'}]},
            'title': {},
            'citations': []
        }

        self.assertEqual(self._article.issue_label, u'v10n12pr')

    def test_issue_label_volume_suppl_number(self):
        self._article.xylose.data = {
            'article': {'v31': [{'_': 10}], 'v132': [{'_': 12}], 'v65': [{'_': '2014'}]},
            'title': {},
            'citations': []
        }

        self.assertEqual(self._article.issue_label, u'v10s12')

    def test_issue_label_ahead(self):
        self._article.xylose.data = {
            'article': {'v32': [{'_': 'ahead'}], 'v65': [{'_': '2014'}]},
            'title': {},
            'citations': []
        }

        self.assertEqual(self._article.issue_label, u'2014nahead')

    def test_issue_label_ahead(self):
        self._article.xylose.data = {
            'article': {'v32': [{'_': 'ahead'}], 'v65': [{'_': '2014'}], 'v71': [{'_': 'pr'}]},
            'title': {},
            'citations': []
        }

        self.assertEqual(self._article.issue_label, u'2014naheadpr')
