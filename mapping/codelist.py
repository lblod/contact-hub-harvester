from rdflib import Graph, Literal, RDF, URIRef
from rdflib.namespace import SKOS, RDF

from helper.functions import concept_uri, export_data
import helper.namespaces as ns

def create_status_uri(g):
  status_list = ['In oprichting', 'Actief', 'Niet actief']

  status_concept_scheme = URIRef(ns.os)
  g.add((status_concept_scheme, RDF.type, SKOS.ConceptScheme))
  g.add((status_concept_scheme, SKOS.prefLabel, Literal('Organisatie status code')))

  for status in status_list:
    concept, _ = concept_uri(status_concept_scheme, status)
    g.add((concept, RDF.type, SKOS.Concept))
    g.add((concept, SKOS.prefLabel, Literal(status, lang='nl')))
    g.add((concept, SKOS.inScheme, status_concept_scheme))
    g.add((concept, SKOS.topConceptOf, status_concept_scheme))
    g.add((status_concept_scheme, SKOS.hasTopConcept, concept))


def create_bestuursfuncie_ere(g):
  ere_bestuursfuncie_list = ['Voorzitter van het bestuur van de eredienst', 'Voorzitter van het centraal bestuur van de eredienst', 
  'Secretaris van het bestuur van de eredienst', 'Secretaris van het centraal bestuur van de eredienst', 'Penningmeester van het bestuur van de eredienst',
  'Bestuurslid van het bestuur van de eredienst', 'Bestuurslid van het centraal bestuur van de eredienst', 'Bestuurslid (van rechtswege)  van het bestuur van de eredienst',
  'Expert van het centraal bestuur van de eredienst', 'Vertegenwoordiger aangesteld door het representatief orgaan van het centraal bestuur van de eredienst']

  ere_bf_concept_scheme = URIRef(ns.bf)
  g.add((ere_bf_concept_scheme, RDF.type, SKOS.ConceptScheme))
  g.add((ere_bf_concept_scheme, SKOS.prefLabel, Literal('Bestuurseenheid classificatie code')))

  for bfunctie in ere_bestuursfuncie_list:
    concept, _ = concept_uri(ere_bf_concept_scheme, bfunctie)
    g.add((concept, RDF.type, SKOS.Concept))
    g.add((concept, SKOS.prefLabel, Literal(bfunctie, lang='nl')))
    g.add((concept, SKOS.inScheme, ere_bf_concept_scheme))
    g.add((concept, SKOS.topConceptOf, ere_bf_concept_scheme))
    g.add((ere_bf_concept_scheme, SKOS.hasTopConcept, concept))

def main():
  g = Graph()

  create_status_uri(g)
  g.serialize(f'output/codelist.ttl',format='turtle')
  create_bestuursfuncie_ere(g)

  export_data(g, 'codelist')

