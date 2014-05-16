import unittest
import requests
import os

try:
    from unittest import mock
except ImportError:
    import mock

from elixir import feedstock

document_xml = document_json = None


def setupModule():
    global document_xml, document_json

    with open(os.path.dirname(__file__) + '/fixtures/document.xml', 'r') as fp:
        document_xml = fp.read().strip()

    with open(os.path.dirname(__file__) + '/fixtures/document.json', 'r') as  fp:
        document_json = fp.read().strip()


class ElixirTests(unittest.TestCase):

    def test_loadXML(self):

        with unittest.mock.patch('requests.get'):
            rqts = requests.get('ANY URL')
            rqts.text = document_xml
            fs = feedstock.loadXML('S0034-89102013000400674')

        self.assertEqual(fs[0:20], '<articles dtd-versio')

    def test_load_rawdata(self):

        with unittest.mock.patch('requests.get'):
            rqts = requests.get('ANY URL')
            rqts.text = document_json
            fs = feedstock.load_rawdata('S0034-89102013000400674')

        self.assertEqual(
            fs.original_title(),
            u'Avaliacao da confiabilidade e validade do Indice de Qualidade da Dieta Revisado'
        )
