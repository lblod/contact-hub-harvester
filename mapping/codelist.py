from rdflib import Graph, Literal, RDF, URIRef
from rdflib.namespace import SKOS, RDF

from helper.functions import concept_uri, export_data
import helper.namespaces as ns

def create_status_uri(g):
  status_list = ['In oprichting', 'Actief', 'Niet actief']

  status_concept_scheme = URIRef(ns.cs + 'OrganisatieStatusCode')
  g.add((status_concept_scheme, RDF.type, SKOS.ConceptScheme))
  g.add((status_concept_scheme, SKOS.prefLabel, Literal('Organisatie status code')))

  for status in status_list:
    concept, _ = concept_uri(status_concept_scheme + '/', status)
    g.add((concept, RDF.type, SKOS.Concept))
    g.add((concept, SKOS.prefLabel, Literal(status)))
    g.add((concept, SKOS.inScheme, status_concept_scheme))
    g.add((concept, SKOS.topConceptOf, status_concept_scheme))
    g.add((status_concept_scheme, SKOS.hasTopConcept, concept))

def create_bestuursfuncie_ere(g):
  ere_bestuursfuncie_list = ['Voorzitter van het bestuur van de eredienst', 'Voorzitter van het centraal bestuur van de eredienst', 
  'Secretaris van het bestuur van de eredienst', 'Secretaris van het centraal bestuur van de eredienst', 'Penningmeester van het bestuur van de eredienst',
  'Bestuurslid van het bestuur van de eredienst', 'Bestuurslid van het centraal bestuur van de eredienst', 'Bestuurslid (van rechtswege)  van het bestuur van de eredienst',
  'Expert van het centraal bestuur van de eredienst', 'Vertegenwoordiger aangesteld door het representatief orgaan van het centraal bestuur van de eredienst']

  ere_bf_concept_scheme = URIRef(ns.cs + 'BestuursfunctieCode')
  g.add((ere_bf_concept_scheme, RDF.type, SKOS.ConceptScheme))
  g.add((ere_bf_concept_scheme, SKOS.prefLabel, Literal('Bestuursfunctie code')))

  for bfunctie in ere_bestuursfuncie_list:
    concept, _ = concept_uri(ere_bf_concept_scheme + '/', bfunctie)
    g.add((concept, RDF.type, SKOS.Concept))
    g.add((concept, SKOS.prefLabel, Literal(bfunctie)))
    g.add((concept, SKOS.inScheme, ere_bf_concept_scheme))
    g.add((concept, SKOS.topConceptOf, ere_bf_concept_scheme))
    g.add((ere_bf_concept_scheme, SKOS.hasTopConcept, concept))

def create_bestuursorgaan_central(g):
  bestuursorgaan_classification_code = ['Centraal kerkbestuur', 'Centraal bestuur']
  
  ere_bo_concept_scheme = URIRef(ns.cs + 'BestuursorgaanClassificatieCode')
  g.add((ere_bo_concept_scheme, RDF.type, SKOS.ConceptScheme))
  g.add((ere_bo_concept_scheme, SKOS.prefLabel, Literal('Bestuursfunctie code')))

  for borgaan in bestuursorgaan_classification_code:
    concept, _ = concept_uri(ere_bo_concept_scheme + '/', borgaan)
    g.add((concept, RDF.type, SKOS.Concept))
    g.add((concept, SKOS.prefLabel, Literal(borgaan)))
    g.add((concept, SKOS.inScheme, ere_bo_concept_scheme))
    g.add((concept, SKOS.topConceptOf, ere_bo_concept_scheme))
    g.add((ere_bo_concept_scheme, SKOS.hasTopConcept, concept))

def create_bestuursorgaan_worship(g):
  bestuursorgaan_classification_code = ['Kerkraad', 'Kathedrale kerkraad', 'Bestuursraad', 'Kerkfabriekraad', 'Comité']
  
  ere_bo_concept_scheme = URIRef(ns.cs + 'BestuursorgaanClassificatieCode')
  g.add((ere_bo_concept_scheme, RDF.type, SKOS.ConceptScheme))
  g.add((ere_bo_concept_scheme, SKOS.prefLabel, Literal('Bestuursfunctie code')))

  for borgaan in bestuursorgaan_classification_code:
    concept, _ = concept_uri(ere_bo_concept_scheme + '/', borgaan)
    g.add((concept, RDF.type, SKOS.Concept))
    g.add((concept, SKOS.prefLabel, Literal(borgaan)))
    g.add((concept, SKOS.inScheme, ere_bo_concept_scheme))
    g.add((concept, SKOS.topConceptOf, ere_bo_concept_scheme))
    g.add((ere_bo_concept_scheme, SKOS.hasTopConcept, concept))


def main():
  g = Graph()

  create_status_uri(g)
  
  create_bestuursfuncie_ere(g)

  create_bestuursorgaan_central(g)

  create_bestuursorgaan_worship(g)

  g.serialize(f'input/codelists/codelist-ere.ttl',format='turtle')
