from rdflib import Graph, Literal, URIRef
from rdflib.namespace import SKOS, RDF, XSD

from helper.functions import concept_uri, export_data
import helper.namespaces as ns

def create_status_uri(g):
  status_list = ['In oprichting', 'Actief', 'Niet actief']

  status_concept_scheme, uuid = concept_uri(ns.gift + 'concept-schemes/', 'OrganizationStatusCode')
  g.add((status_concept_scheme, RDF.type, SKOS.ConceptScheme))
  g.add((status_concept_scheme, SKOS.prefLabel, Literal('Organisatie status code')))
  g.add((status_concept_scheme, ns.mu.uuid, Literal(uuid)))

  for status in status_list:
    concept, uuid = concept_uri(ns.gift + 'concepts/', status)
    g.add((concept, RDF.type, SKOS.Concept))
    g.add((concept, SKOS.prefLabel, Literal(status)))
    g.add((concept, SKOS.topConceptOf, status_concept_scheme))
    g.add((concept, SKOS.inScheme, status_concept_scheme))
    g.add((concept, ns.mu.uuid, Literal(uuid)))

def create_bestuursfuncie_ere(g):
  ere_bestuursfuncie_list = ['Voorzitter van het bestuur van de eredienst', 'Voorzitter van het centraal bestuur van de eredienst', 
  'Secretaris van het bestuur van de eredienst', 'Secretaris van het centraal bestuur van de eredienst', 'Penningmeester van het bestuur van de eredienst',
  'Bestuurslid van het bestuur van de eredienst', 'Bestuurslid van het centraal bestuur van de eredienst', 'Bestuurslid (van rechtswege)  van het bestuur van de eredienst',
  'Expert van het centraal bestuur van de eredienst', 'Vertegenwoordiger aangesteld door het representatief orgaan van het centraal bestuur van de eredienst']

  ere_bf_concept_scheme = URIRef(ns.cs + 'BestuursfunctieCode')
  g.add((ere_bf_concept_scheme, RDF.type, SKOS.ConceptScheme))
  g.add((ere_bf_concept_scheme, SKOS.prefLabel, Literal('Bestuursfunctie code')))

  for bfunctie in ere_bestuursfuncie_list:
    concept, uuid = concept_uri(ns.c + 'BestuursfunctieCode/', bfunctie)
    g.add((concept, RDF.type, SKOS.Concept))
    g.add((concept, SKOS.prefLabel, Literal(bfunctie)))
    g.add((concept, SKOS.topConceptOf, ere_bf_concept_scheme))
    g.add((concept, SKOS.inScheme, ere_bf_concept_scheme))
    g.add((concept, ns.mu.uuid, Literal(uuid)))

def create_bestuursorgaan_ere(g):
  bestuursorgaan_classification_code = ['Kerkraad', 'Kathedrale kerkraad', 'Bestuursraad', 'Kerkfabriekraad', 'Comité', 'Centraal kerkbestuur', 'Centraal bestuur']
  
  ere_bo_concept_scheme = URIRef(ns.c + 'BestuursorgaanClassificatieCode')
  g.add((ere_bo_concept_scheme, RDF.type, SKOS.ConceptScheme))
  g.add((ere_bo_concept_scheme, SKOS.prefLabel, Literal('Bestuursfunctie code')))

  for borgaan in bestuursorgaan_classification_code:
    concept, uuid = concept_uri(ns.c + 'BestuursorgaanClassificatieCode/', borgaan)
    g.add((concept, RDF.type, SKOS.Concept))
    g.add((concept, SKOS.prefLabel, Literal(borgaan)))
    g.add((concept, SKOS.topConceptOf, ere_bo_concept_scheme))
    g.add((concept, SKOS.inScheme, ere_bo_concept_scheme))
    g.add((concept, ns.mu.uuid, Literal(uuid)))


def main():
  g = Graph()

  create_status_uri(g)
  
  create_bestuursfuncie_ere(g)

  create_bestuursorgaan_ere(g)

  export_data(g, 'codelist-ere')

  g.serialize('input/codelists/codelist-ere.ttl',format='turtle')

  

