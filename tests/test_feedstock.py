import unittest
import requests
import os
import json
import io
import zipfile
from lxml import etree

try:
    from unittest import mock
except ImportError:
    import mock

from elixir import feedstock, utils
from xylose import scielodocument

document_xml = document_json = source_dir = None


def setupModule():
    global document_xml, document_json, source_dir

    with open(os.path.dirname(__file__) + '/fixtures/document.xml', 'r') as fp:
        document_xml = fp.read().strip()

    with open(os.path.dirname(__file__) + '/fixtures/document.json', 'r') as fp:
        document_json = fp.read().strip()

    source_dir = os.path.dirname(__file__) + '/files'


class FeedStockTests(unittest.TestCase):

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
            html = feedstock.read_file('xxxx')

    def test_html_regex_1(self):

        html = '<html><body> <p>blaus</p> <i>picles</i> Testando</body></html>'

        self.assertEqual(
            feedstock.html_regex.findall(html)[0],
            u' <p>blaus</p> <i>picles</i> Testando'
        )

    def test_html_regex_2(self):

        html = '<html><body bg="#123456"> <p>blaus</p> <i>picles</i> Testando</body></html>'

        self.assertEqual(
            feedstock.html_regex.findall(html)[0],
            u' <p>blaus</p> <i>picles</i> Testando'
        )

    def test_html_regex_2(self):

        html = '<html><body bg="#123456">\n<p>blaus</p> <i>picles</i> Testando</body></html>'

        self.assertEqual(
            feedstock.html_regex.findall(html)[0],
            u'\n<p>blaus</p> <i>picles</i> Testando'
        )

    def test_read_document_valid_path(self):

        html = feedstock.read_file(source_dir+'/html/rsp/v40n6/pt_07.htm', encoding='iso-8859-1', replace_entities=True, version='legacy')

        self.assertEqual(html[:20], '<p align="right"><fo')

    def test_get_xml_document_images_with_real_xml(self):
        images = feedstock.get_xml_document_images(source_dir+'/xml/rsp/v47n4/0034-8910-rsp-47-04-0740.xml')        

        self.assertTrue(u'0034-8910-rsp-47-04-0740-gf01.jpg' in images)
        self.assertEqual(2, len(images))

    def test_get_xml_document_images(self):
        xml = u"""<!DOCTYPE article PUBLIC "-//NLM//DTD Journal Publishing DTD v3.0 20080202//EN" "journalpublishing3.dtd">
                 <article xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:mml="http://www.w3.org/1998/Math/MathML"
                    dtd-version="3.0" article-type="research-article" xml:lang="pt">
                    <front></front>
                    <body>
                        <sec>
                            <p>
                                <graphic xlink:href="0034-8910-rsp-47-04-0740-gf01"/>
                                <graphic xlink:href="0034-8910-rsp-47-04-0740-gf02"/>
                            </p>
                            <p>
                                <inline-graphic xlink:href="0034-8910-rsp-47-04-0740-gf03"/>
                                <inline-graphic xlink:href="0034-8910-rsp-47-04-0740-gf04.png"/>
                            </p>
                        </sec>
                    </body>
                </article>
            """

        with io.StringIO() as f:
            f.write(xml)
            f.seek(0)
            images = feedstock.get_xml_document_images(f)

        self.assertTrue(u'0034-8910-rsp-47-04-0740-gf01.jpg' in images)
        self.assertTrue(u'0034-8910-rsp-47-04-0740-gf02.jpg' in images)
        self.assertTrue(u'0034-8910-rsp-47-04-0740-gf03.jpg' in images)
        self.assertTrue(u'0034-8910-rsp-47-04-0740-gf04.png' in images)
        self.assertEqual(4, len(images))

    def test_get_xml_document_midias(self):
        xml = """<!DOCTYPE article PUBLIC "-//NLM//DTD Journal Publishing DTD v3.0 20080202//EN" "journalpublishing3.dtd">
                 <article xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:mml="http://www.w3.org/1998/Math/MathML"
                    dtd-version="3.0" article-type="research-article" xml:lang="pt">
                    <front></front>
                    <body>
                        <sec>
                            <p>
                                <midia xlink:href="0034-8910-rsp-47-04-0740-gf01.mp4"/>
                                <midia xlink:href="0034-8910-rsp-47-04-0740-gf02.mov"/>
                            </p>
                            <p>
                                <midia xlink:href="0034-8910-rsp-47-04-0740-gf03.mp3"/>
                            </p>
                        </sec>
                    </body>
                </article>
            """

        with io.StringIO() as f:
            f.write(xml)
            f.seek(0)
            images = feedstock.get_xml_document_midias(f)

        self.assertTrue(u'0034-8910-rsp-47-04-0740-gf01.mp4' in images)
        self.assertTrue(u'0034-8910-rsp-47-04-0740-gf02.mov' in images)
        self.assertTrue(u'0034-8910-rsp-47-04-0740-gf03.mp3' in images)
        self.assertEqual(3, len(images))

    def test_get_document_images(self):

        images = feedstock.get_document_images(source_dir+'/html/rsp/v40n6/en_07.htm')

        self.assertTrue(u'e07f1.gif' in images)

    def test_get_document_images_from_html(self):

        html = """
            <html>
                <img src="/img/revistas/rsp/01.gif" />
                <img src="/img/revistas/rsp/02.jpg" />
                <a href="/img/revistas/rsp/03.gif">Blaus</a>
                <a href="\img/revistas/rsp/04.gif">Picles</a>
            </html>
        """
        images = feedstock.get_document_images(html)

        self.assertEqual(['01.gif', '02.jpg', '03.gif', '04.gif'], images)

    def test_get_document_midias_from_html(self):

        html = """
            <html>
                <a href="/brocolis/revistas/rsp/01.mp3">Blaus</a>
                <a href="\\blaus/revistas/rsp/02.mov">Picles</a>
                <a href="\midia/revistas/rsp/03.mpeg">Blaus</a>
                <a href="\picles/revistas/rsp/04.avi">Picles</a>
                <a href="\img/revistas/rsp/05.PPT">Blaus</a>
                <a href="\\videos/revistas/rsp/06.mp4">Picles</a>
                <a href="07.doc">Picles</a>
                <a href="08.exe">Picles</a>
                <a href="http://www.blaus.picles\picles/revistas/rsp/09.avi">Picles</a>
            </html>
        """
        images = feedstock.get_document_midias(html)

        self.assertEqual([
            '/brocolis/revistas/rsp/01.mp3',
            '/blaus/revistas/rsp/02.mov',
            '/midia/revistas/rsp/03.mpeg',
            '/picles/revistas/rsp/04.avi',
            '/img/revistas/rsp/05.ppt',
            '/videos/revistas/rsp/06.mp4',
            '07.doc',
            'http://www.blaus.picles/picles/revistas/rsp/09.avi'
        ], images)

    def test_get_document_images_crazy_slashes_1(self):

        images = feedstock.get_document_images('<img src="/img\html/rsp/v40n6/teste.gif" />')

        self.assertTrue(u'teste.gif' in images)

    def test_get_document_images_crazy_slashes_2(self):

        images = feedstock.get_document_images('<img src="\img\html/rsp/v40n6/teste.gif" />')

        self.assertTrue(u'teste.gif' in images)

    def test_check_images_availability(self):

        html_images = ['a', 'b', 'c']

        file_system_images = ['b', 'c', 'd', 'e']

        result = feedstock.check_images_availability(file_system_images, html_images)

        self.assertEqual([('a', False), ('b', True), ('c', True)], result)

    def test_check_images_availability_with_a_html(self):

        html = """
            <html>
                <img src="/img/revistas/rsp/01.gif" />
                <img src='/IMG/revistas/rsp/02.jpg' />
                <a href="\IMG/revistas/rsp/03.GIF">Blaus</a>
                <a href='\img/revistas/rsp/04.gif'>Picles</a>
            </html>
        """

        file_system_images = [
            '/img/revistas/rsp/01.gif',
            '/img/revistas/rsp/02.jpg',
            '/img/revistas/rsp/03.gif',
            '/img/revistas/rsp/05.gif',
            '/img/revistas/rsp/06.gif'
        ]

        result = feedstock.check_images_availability(file_system_images, html)

        expected = [
            ('01.gif', True),
            ('02.jpg', True),
            ('03.gif', True),
            ('04.gif', False),
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

    def test_rsps_xml_sps_mode(self):
        rsps_xml = self._article.rsps_xml

        self.assertEqual(rsps_xml.name, '0034-8910-rsp-47-04-0675')

    @unittest.skip
    def test_rsps_xml_legacy_mode(self):
        json_data = json.loads(document_json)
        json_data['title']['v68'][0]['_'] = 'rsp'
        json_data['article']['v31'][0]['_'] = '40'
        json_data['article']['v32'][0]['_'] = '6'
        json_data['article']['v65'][0]['_'] = '2006'
        json_data['article']['v702'][0]['_'] = '/x/x/y/z/07.htm'

        raw_data = scielodocument.Article(json_data)

        article = feedstock.Article(
            'S0034-89102006000700007',
            document_xml,
            raw_data,
            source_dir
        )

        self.assertEqual(article.rsps_xml.name, '07')
        self.assertEqual(article.rsps_xml.read()[:20], '<p align="right"><fo')

    def test_get_body_from_files(self):
        json_data = json.loads(document_json)
        json_data['title']['v68'][0]['_'] = 'rsp'
        json_data['article']['v31'][0]['_'] = '40'
        json_data['article']['v32'][0]['_'] = '6'
        json_data['article']['v65'][0]['_'] = '2006'
        json_data['article']['v702'][0]['_'] = '/x/x/y/z/07.htm'

        raw_data = scielodocument.Article(json_data)

        article = feedstock.Article(
            'S0034-89102006000700007',
            document_xml,
            raw_data,
            source_dir
        )

        htmls = article._get_body_from_files
        self.assertTrue('en_07.htm' in htmls.keys())
        self.assertTrue('pt_07.htm' in htmls.keys())
        self.assertEqual(htmls['en_07.htm']['content'][:20], '<p align="right"><fo')
        self.assertEqual(len(htmls['en_07.htm']['files']), 2)
        self.assertEqual(len(htmls['pt_07.htm']['files']), 1)

    def test_xml_sps_with_legacy_data(self):
        json_data = json.loads(document_json)
        json_data['title']['v68'][0]['_'] = 'rsp'
        json_data['article']['v31'][0]['_'] = '40'
        json_data['article']['v32'][0]['_'] = '6'
        json_data['article']['v65'][0]['_'] = '2006'
        json_data['article']['v702'][0]['_'] = '/x/x/y/z/07.htm'

        raw_data = scielodocument.Article(json_data)

        article = feedstock.Article(
            'S0034-89102006000700007',
            document_xml,
            raw_data,
            source_dir
        )

        xml = article.xml_sps_with_legacy_data

        translations = xml.findall('.//sub-article')
        self.assertEqual(len(translations), 2)

    def test_version_xml(self):

        version = self._article._content_version()

        self.assertEqual(version, 'sps')

    def test_version_html(self):
        json_data = json.loads(document_json)
        json_data['title']['v68'][0]['_'] = 'rsp'
        json_data['article']['v31'][0]['_'] = '40'
        json_data['article']['v32'][0]['_'] = '6'
        json_data['article']['v65'][0]['_'] = '2006'
        json_data['article']['v702'][0]['_'] = '/x/x/y/z/07.htm'

        raw_data = scielodocument.Article(json_data)

        article = feedstock.Article(
            'S0034-89102006000700007',
            document_xml,
            raw_data,
            source_dir
        )

        self.assertEqual(article._content_version(), 'legacy')

    def test_list_images_legacy_mode(self):
        json_data = json.loads(document_json)
        json_data['title']['v68'][0]['_'] = 'rsp'
        json_data['article']['v31'][0]['_'] = '40'
        json_data['article']['v32'][0]['_'] = '6'
        json_data['article']['v65'][0]['_'] = '2006'
        json_data['article']['v702'][0]['_'] = '/x/x/y/z/07.htm'

        raw_data = scielodocument.Article(json_data)

        article = feedstock.Article(
            'S0034-89102006000700007',
            document_xml,
            raw_data,
            source_dir
        )

        images = article.list_document_images

        self.assertEqual(len(images), 14)

    def test_list_images_without_files(self):
        json_data = json.loads(document_json)
        json_data['title']['v68'][0]['_'] = 'rsp'
        json_data['article']['v31'][0]['_'] = '40'
        json_data['article']['v32'][0]['_'] = '7'
        json_data['article']['v65'][0]['_'] = '2006'
        json_data['article']['v702'][0]['_'] = '/x/x/y/z/07.htm'

        raw_data = scielodocument.Article(json_data)

        article = feedstock.Article(
            'S0034-89102006000700007',
            document_xml,
            raw_data,
            source_dir
        )

        images = article.list_document_images

        self.assertEqual(images, [])

    def test_list_images_invalid_path(self):
        json_data = json.loads(document_json)
        json_data['title']['v68'][0]['_'] = 'rsp'
        json_data['article']['v31'][0]['_'] = 'xx'
        json_data['article']['v32'][0]['_'] = 'xx'
        json_data['article']['v65'][0]['_'] = '2014'
        json_data['article']['v702'][0]['_'] = 'invalid'

        raw_data = scielodocument.Article(json_data)

        article = feedstock.Article(
            'S0034-89102013000400674',
            document_xml,
            raw_data,
            source_dir
        )

        with self.assertRaises(FileNotFoundError):
            article.list_document_images

    def test_list_pdfs(self):
        json_data = json.loads(document_json)
        json_data['title']['v68'][0]['_'] = 'rsp'
        json_data['article']['v31'][0]['_'] = '40'
        json_data['article']['v32'][0]['_'] = '6'
        json_data['article']['v65'][0]['_'] = '2006'
        json_data['article']['v702'][0]['_'] = '/x/x/y/z/07.htm'

        raw_data = scielodocument.Article(json_data)

        article = feedstock.Article(
            'S0034-89102006000700007',
            document_xml,
            raw_data,
            source_dir
        )

        pdfs = article.list_pdfs

        self.assertEqual(len(pdfs), 2)

    def test_list_pdfs_without_files(self):
        json_data = json.loads(document_json)
        json_data['title']['v68'][0]['_'] = 'rsp'
        json_data['article']['v31'][0]['_'] = '40'
        json_data['article']['v32'][0]['_'] = '7'
        json_data['article']['v65'][0]['_'] = '2006'
        json_data['article']['v702'][0]['_'] = '/x/x/y/z/07.htm'

        raw_data = scielodocument.Article(json_data)

        article = feedstock.Article(
            'S0034-89102006000700007',
            document_xml,
            raw_data,
            source_dir
        )

        pdfs = article.list_pdfs

        self.assertEqual(pdfs, [])

    def test_list_pdfs_invalid_path(self):
        json_data = json.loads(document_json)
        json_data['title']['v68'][0]['_'] = 'rsp'
        json_data['article']['v31'][0]['_'] = 'xx'
        json_data['article']['v32'][0]['_'] = 'xx'
        json_data['article']['v65'][0]['_'] = '2006'
        json_data['article']['v702'][0]['_'] = '/x/x/y/z/07.htm'

        raw_data = scielodocument.Article(json_data)

        article = feedstock.Article(
            'S0034-89102006000700007',
            document_xml,
            raw_data,
            source_dir
        )

        with self.assertRaises(FileNotFoundError):
            article.list_pdfs

    def test_list_htmls(self):
        json_data = json.loads(document_json)
        json_data['title']['v68'][0]['_'] = 'rsp'
        json_data['article']['v31'][0]['_'] = '40'
        json_data['article']['v32'][0]['_'] = '6'
        json_data['article']['v65'][0]['_'] = '2006'
        json_data['article']['v702'][0]['_'] = '/x/x/y/z/07.htm'

        raw_data = scielodocument.Article(json_data)

        article = feedstock.Article(
            'S0034-89102006000700007',
            document_xml,
            raw_data,
            source_dir
        )

        htmls = article.list_htmls

        self.assertEqual(len(htmls), 3)

    def test_list_htmls_without_files(self):
        json_data = json.loads(document_json)
        json_data['title']['v68'][0]['_'] = 'rsp'
        json_data['article']['v31'][0]['_'] = '40'
        json_data['article']['v32'][0]['_'] = '7'
        json_data['article']['v65'][0]['_'] = '2006'
        json_data['article']['v702'][0]['_'] = '/x/x/y/z/07.htm'

        raw_data = scielodocument.Article(json_data)

        article = feedstock.Article(
            'S0034-89102006001000007',
            document_xml,
            raw_data,
            source_dir
        )

        htmls = article.list_htmls

        self.assertEqual(htmls, [])

    def test_list_htmls_invalid_path(self):
        json_data = json.loads(document_json)
        json_data['title']['v68'][0]['_'] = 'rsp'
        json_data['article']['v31'][0]['_'] = 'xx'
        json_data['article']['v32'][0]['_'] = 'xx'
        json_data['article']['v65'][0]['_'] = '2014'
        json_data['article']['v702'][0]['_'] = '/x/x/y/z/07.htm'

        raw_data = scielodocument.Article(json_data)

        article = feedstock.Article(
            'S0034-89102013000400674',
            document_xml,
            raw_data,
            source_dir
        )

        with self.assertRaises(FileNotFoundError):
            article.list_htmls

    def test_list_images_sps_mode(self):
        json_data = json.loads(document_json)
        json_data['title']['v68'][0]['_'] = 'rsp'
        json_data['article']['v31'][0]['_'] = '47'
        json_data['article']['v32'][0]['_'] = '4'
        json_data['article']['v65'][0]['_'] = '2014'

        raw_data = scielodocument.Article(json_data)

        article = feedstock.Article(
            'S0034-89102013000400674',
            document_xml,
            raw_data,
            source_dir
        )

        images = article.list_document_images

        self.assertTrue('0034-8910-rsp-47-04-0675-gf01.jpg', images)
        self.assertTrue('0034-8910-rsp-47-04-0675-gf01-en.jpg', images)
        self.assertEqual(len(images), 2)

    def test_list_xmls(self):
        xmls = self._article.list_xmls

        self.assertTrue('0034-8910-rsp-47-04-0675.xml' in xmls[0])

    def test_list_xmls_without_files(self):
        json_data = json.loads(document_json)
        json_data['title']['v68'][0]['_'] = 'rsp'
        json_data['article']['v31'][0]['_'] = '47'
        json_data['article']['v32'][0]['_'] = '1'
        json_data['article']['v65'][0]['_'] = '2014'
        json_data['article']['v702'][0]['_'] = '/x/x/y/z/07.htm'

        raw_data = scielodocument.Article(json_data)

        article = feedstock.Article(
            'S0034-89102013000400674',
            document_xml,
            raw_data,
            source_dir
        )

        xmls = article.list_xmls

        self.assertEqual(xmls, [])

    def test_list_xmls_invalid_path(self):
        json_data = json.loads(document_json)
        json_data['title']['v68'][0]['_'] = 'rsp'
        json_data['article']['v31'][0]['_'] = 'xx'
        json_data['article']['v32'][0]['_'] = 'xx'
        json_data['article']['v65'][0]['_'] = '2014'
        json_data['article']['v702'][0]['_'] = '/x/x/y/z/07.htm'

        raw_data = scielodocument.Article(json_data)

        article = feedstock.Article(
            'S0034-89102013000400674',
            document_xml,
            raw_data,
            source_dir
        )

        with self.assertRaises(FileNotFoundError):
            article.list_xmls

    def test_pid(self):

        self.assertEqual(self._article.pid, u'S0034-89102013000400674')

    def test_scielo_issn(self):

        self.assertEqual(self._article._journal_issn(), u'0034-8910')

    def test_file_code(self):

        self.assertEqual(self._article._file_code(), u'0034-8910-rsp-47-04-0675')

    def test_acronym(self):

        self.assertEqual(self._article._journal_acronym(), u'rsp')

    def test_issue_label_volume_number(self):
        self._article.xylose.data = {
            'article': {'v31': [{'_': 10}], 'v32': [{'_': 12}], 'v65': [{'_': '2014'}]},
            'title': {},
            'citations': []
        }

        self.assertEqual(self._article._issue_label(), u'v10n12')

    def test_issue_label_volume_number_pr(self):
        self._article.xylose.data = {
            'article': {'v31': [{'_': 10}], 'v32': [{'_': 12}], 'v71': [{'_': 'pr'}], 'v65': [{'_': '2014'}]},
            'title': {},
            'citations': []
        }

        self.assertEqual(self._article._issue_label(), u'v10n12pr')

    def test_issue_label_volume_suppl_number(self):
        self._article.xylose.data = {
            'article': {'v31': [{'_': 10}], 'v132': [{'_': 12}], 'v65': [{'_': '2014'}]},
            'title': {},
            'citations': []
        }

        self.assertEqual(self._article._issue_label(), u'v10s12')

    def test_issue_label_ahead(self):
        self._article.xylose.data = {
            'article': {'v32': [{'_': 'ahead'}], 'v65': [{'_': '2014'}]},
            'title': {},
            'citations': []
        }

        self.assertEqual(self._article._issue_label(), u'2014nahead')

    def test_issue_label_ahead(self):
        self._article.xylose.data = {
            'article': {'v32': [{'_': 'ahead'}], 'v65': [{'_': '2014'}], 'v71': [{'_': 'pr'}]},
            'title': {},
            'citations': []
        }

        self.assertEqual(self._article._issue_label(), u'2014naheadpr')
