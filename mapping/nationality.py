from rdflib import Graph, URIRef, Namespace, Literal
from rdflib.namespace import SKOS, RDFS, RDF
from helper.functions import export_data, concept_uri
import helper.namespaces as ns

def main():
  graph = Graph()
  graph.parse('output/20210830182209-codelist-nationality-complete.ttl')

  query = """
            SELECT ?concept ?label ?adjective
            WHERE { 
              ?concept a euvoc:Country; skos:prefLabel ?label; skos-xl:altLabel [ a skos-xl:Label; rdfs:label ?adjective; 
              dct:type <http://publications.europa.eu/resource/authority/label-type/ADJECTIVE> ]
              FILTER(lang(?label) = 'nl') 
              FILTER(lang(?adjective) = 'nl')
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

  nationality_graph = Graph()

  if qres.bindings:
    for row in qres:
      nationality_concept = URIRef(f'{row.concept}')
      _, nationality_uuid = concept_uri(ns.euvoc.Country, f'{row.concept}')
      nationality_graph.add((nationality_concept, RDF.type, ns.euvoc.Country))
      nationality_graph.add((nationality_concept, ns.mu.uuid, Literal(nationality_uuid)))
      nationality_graph.add((nationality_concept, SKOS.prefLabel, Literal(f'{row.label}')))
      nationality_graph.add((nationality_concept, RDFS.label, Literal(f'{row.adjective}')))

  export_data(nationality_graph, 'codelist-nationality')

