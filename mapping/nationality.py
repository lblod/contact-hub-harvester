from rdflib import Graph, URIRef
from rdflib.namespace import SKOS, RDFS
from helper.functions import export_data

def main():
  graph = Graph()

  #nationalities.parse('input/countries-skos-ap-act.rdf')

  graph.parse('output/20210830182209-codelist-nationality.ttl')

  query = """
            SELECT ?concept 
            WHERE { 
              ?concept a euvoc:Country; skos:prefLabel ?label; skos-xl:altLabel [ a skos-xl:Label; rdfs:label ?adjective; 
              dct:type <http://publications.europa.eu/resource/authority/label-type/ADJECTIVE> ]
              FILTER(lang(?label) = "nl" || lang(?adjective) = "nl")
            }
          """

  namespaces = { 
    "euvoc": URIRef("http://publications.europa.eu/ontology/euvoc#"),
    "skos": SKOS,
    "skos-xl": URIRef("http://www.w3.org/2008/05/skos-xl#"),
    "rdfs": RDFS,
    "dct": URIRef("http://purl.org/dc/terms/") 
  }

  qres = graph.query(query, initNs = namespaces)

  if qres.bindings:
    concept = qres.bindings[0]['concept']

  export_data(g, 'codelist-nationality-cleansed')

