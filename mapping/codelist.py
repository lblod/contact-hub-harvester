from rdflib import Graph, Literal, URIRef
from rdflib.namespace import SKOS, RDF

from helper.functions import concept_uri, export_data
import helper.namespaces as ns

def create_status_uri(g):
  status_list = ['In oprichting', 'Actief', 'Niet Actief']
  status_concept_scheme, uuid = concept_uri(ns.gift + 'concept-schemes/', 'OrganizationStatusCode')
  g.add((status_concept_scheme, RDF.type, SKOS.ConceptScheme))
  g.add((status_concept_scheme, SKOS.prefLabel, Literal('Organisatie status code')))
  g.add((status_concept_scheme, ns.mu.uuid, Literal(uuid)))

  for status in status_list:
    concept, uuid = concept_uri(ns.gift + 'concepts/', status)
    g.add((concept, RDF.type, SKOS.Concept))
    g.add((concept, RDF.type, ns.gift_v.OrganisatieStatusCode))
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
    g.add((concept, RDF.type, ns.gift_v.BestuursfunctieCode))
    g.add((concept, SKOS.prefLabel, Literal(bfunctie)))
    g.add((concept, SKOS.topConceptOf, ere_bf_concept_scheme))
    g.add((concept, SKOS.inScheme, ere_bf_concept_scheme))
    g.add((concept, ns.mu.uuid, Literal(uuid)))

def create_bestuursorgaan_ere(g):
  bestuursorgaan_classification_code = ['Kerkraad', 'Kathedrale kerkraad', 'Bestuursraad', 'Kerkfabriekraad', 'Comité', 'Centraal kerkbestuur', 
                                        'Centraal bestuur']
  
  ere_bo_concept_scheme = URIRef(ns.c + 'BestuursorgaanClassificatieCode')
  g.add((ere_bo_concept_scheme, RDF.type, SKOS.ConceptScheme))
  g.add((ere_bo_concept_scheme, SKOS.prefLabel, Literal('Bestuursorgaan classificatie code')))

  for borgaan in bestuursorgaan_classification_code:
    concept, uuid = concept_uri(ns.c + 'BestuursorgaanClassificatieCode/', borgaan)
    g.add((concept, RDF.type, SKOS.Concept))
    g.add((concept, RDF.type, ns.gift_v.BestuursorgaanClassificatieCode))
    g.add((concept, SKOS.prefLabel, Literal(borgaan)))
    g.add((concept, SKOS.topConceptOf, ere_bo_concept_scheme))
    g.add((concept, SKOS.inScheme, ere_bo_concept_scheme))
    g.add((concept, ns.mu.uuid, Literal(uuid)))

def create_type_ere(g):
  type_list = ['Islamitisch', 'Orthodox', 'Protestants', 'Rooms-Katholiek', 'Anglicaans', 'Israëlitisch']

  ere_te_concept_scheme, ere_te_uuid = concept_uri(ns.gift + 'concept-schemes/', 'TypeEredienst')
  g.add((ere_te_concept_scheme, RDF.type, SKOS.ConceptScheme))
  g.add((ere_te_concept_scheme, SKOS.prefLabel, Literal('Type eredienst')))
  g.add((ere_te_concept_scheme, ns.mu.uuid, Literal(ere_te_uuid)))

  for type_ere in type_list:
    concept, uuid = concept_uri(ns.gift + 'concepts/', type_ere)
    g.add((concept, RDF.type, SKOS.Concept))
    g.add((concept, RDF.type, ns.gift_v.TypeEredienst))
    g.add((concept, SKOS.prefLabel, Literal(type_ere)))
    g.add((concept, SKOS.topConceptOf, ere_te_concept_scheme))
    g.add((concept, SKOS.inScheme, ere_te_concept_scheme))
    g.add((concept, ns.mu.uuid, Literal(uuid)))

def create_type_helft(g):
  type_helft_list = ['Kleine helft', 'Grote helft']

  ere_th_concept_scheme, ere_th_uuid = concept_uri(ns.gift + 'concept-schemes/', 'HelftVerkiezing')
  g.add((ere_th_concept_scheme, RDF.type, SKOS.ConceptScheme))
  g.add((ere_th_concept_scheme, SKOS.prefLabel, Literal('Helft verkiezing')))
  g.add((ere_th_concept_scheme, ns.mu.uuid, Literal(ere_th_uuid)))

  for type_helft in type_helft_list:
    concept, uuid = concept_uri(ns.gift + 'concepts/', type_helft)
    g.add((concept, RDF.type, SKOS.Concept))
    g.add((concept, RDF.type, ns.gift_v.HelftVerkiezing))
    g.add((concept, SKOS.prefLabel, Literal(type_helft)))
    g.add((concept, SKOS.topConceptOf, ere_th_concept_scheme))
    g.add((concept, SKOS.inScheme, ere_th_concept_scheme))
    g.add((concept, ns.mu.uuid, Literal(uuid)))
                                                          

def create_change_event_ere(g):
  change_event_type_list = ['Erkenning aangevraagd', 'Erkenning toegekend', 'Erkenning niet toegekend', 'Samenvoeging', 
                            'Wijziging Gebiedsomschrijving', 'Naamswijziging', 'Erkenning opgeheven', 'Onder sanctieregime',
                            'Opschorting Erkenning']

  change_event_concept_scheme, uuid = concept_uri(ns.gift + 'concept-schemes/', 'Veranderingsgebeurtenis')
  g.add((change_event_concept_scheme, RDF.type, SKOS.ConceptScheme))
  g.add((change_event_concept_scheme, SKOS.prefLabel, Literal('Veranderingsgebeurtenis types')))
  g.add((change_event_concept_scheme, ns.mu.uuid, Literal(uuid)))

  for change_event in change_event_type_list:
    concept, uuid = concept_uri(ns.gift + 'concepts/', change_event)
    g.add((concept, RDF.type, SKOS.Concept))
    g.add((concept, RDF.type, ns.gift_v.Veranderingsgebeurtenis))
    g.add((concept, SKOS.prefLabel, Literal(change_event)))
    g.add((concept, SKOS.topConceptOf, change_event_concept_scheme))
    g.add((concept, SKOS.inScheme, change_event_concept_scheme))
    g.add((concept, ns.mu.uuid, Literal(uuid)))


def main():
  g = Graph()

  create_status_uri(g)

  create_change_event_ere(g)
  
  create_bestuursfuncie_ere(g)

  create_bestuursorgaan_ere(g)

  create_type_ere(g)

  create_type_helft(g)

  export_data(g, 'codelist-ere')

  g.serialize('input/codelists/codelist-ere.ttl',format='turtle')

  

