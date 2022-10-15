import os
import re
from os.path import basename
import shutil
from rdflib import Graph, URIRef
from sickle import Sickle
import argparse

parser = argparse.ArgumentParser(description="Parse entities")
parser.add_argument('-e', '--entity',  nargs='+', help="Enter entity name") #
group = parser.add_mutually_exclusive_group()
group.add_argument('-de', '--default', action='store_true', help="Collect all default entities")

args = parser.parse_args()

baseUrl = 'https://www.collectienederland.nl/api/oai-pmh/?verb=ListRecords&metadataPrefix=edm-strict&set='

entities = ['mauritshuis',
            'museum-de-fundatie']

# entities = ['mauritshuis',
#         'museum-de-fundatie',
#         'catharijneconvent',
#         'stedelijk-museum-schiedam',
#         'van-abbe-museum',
#         'museum-belvedere',
#         'rijksakademie',
#         'moderne-kunst-museum-deventer']

shutil.rmtree("./xml-integrated/", ignore_errors=True)
os.makedirs("./xml-integrated/", exist_ok=True)

shutil.rmtree("./collected/" , ignore_errors=True)

shutil.rmtree("./converted/", ignore_errors=True)
os.makedirs("./converted/", exist_ok=True)


def read_files(_entities):
    for entity in _entities:
        sickle = Sickle(baseUrl + entity)
        records = sickle.ListRecords()
        fullPath = "./xml-integrated/" + entity
        i = 0
        for record in records:
            with open(fullPath + '.xml', 'ab+') as fp:
                fp.write(record.raw.encode('utf8'))
            i = i + 1
        print(entity + " found records: " + str(i))

        parse_xml(fullPath + '.xml')


def parse_xml(xml_path):
    try:
        content = open(xml_path, 'r', encoding='utf8').read()
        rdfXML = re.findall('<rdf:RDF.*?</rdf:RDF>', content, re.DOTALL)
        dir_name = os.path.splitext(basename(xml_path))[0]
        print("Converting " + dir_name)

        shutil.rmtree("./collected/" + dir_name, ignore_errors=True)
        os.makedirs("./collected/" + dir_name, exist_ok=True)

        for idx, p in enumerate(rdfXML):
            f = open("./collected/" + dir_name + "/rdf" + str(idx + 1) + ".xml", "w+", encoding='utf8')
            if f.write(p):
                f.close()
                process_rdf("./collected/" + dir_name + "/rdf" + str(idx + 1) + ".xml", dir_name)

    except Exception as e:
        print(str(e))


def process_rdf(path, dir_name):
    try:
        g = Graph()
        g.parse(path, format("xml"), encoding='utf8')
        _path = f'./converted/{dir_name}.ttl'
        turtleFile = g.serialize(format='turtle', encoding='utf-8')
        with open(_path, "ab+") as myfile:
            myfile.write(turtleFile)
            myfile.close()
    except Exception as e:
        print(str(e))


if __name__ == '__main__' or args.default:
    read_files(entities)
elif args.entity:
    read_files(args.entity)
