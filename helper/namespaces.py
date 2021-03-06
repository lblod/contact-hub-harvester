from rdflib import URIRef, Namespace
from helper.functions import concept_uri 

org = Namespace('http://www.w3.org/ns/org#')
locn = Namespace('http://www.w3.org/ns/locn#')
schema = Namespace('http://schema.org/')
rov = Namespace('http://www.w3.org/ns/regorg#')
person = Namespace('http://www.w3.org/ns/person#')
vcard = Namespace('http://www.w3.org/2006/vcard/ns#')
dbpedia = Namespace('http://dbpedia.org/ontology/')
adms = Namespace('http://www.w3.org/ns/adms#')
euro = Namespace('http://data.europa.eu/m8g/')
prov = Namespace('http://www.w3.org/ns/prov#')
owl = Namespace('http://www.w3.org/2002/07/owl#')
euvoc = Namespace("http://publications.europa.eu/ontology/euvoc#")

organisatie = Namespace('https://data.vlaanderen.be/ns/organisatie#')
persoon = Namespace('http://data.vlaanderen.be/ns/persoon#')
adres = Namespace('https://data.vlaanderen.be/ns/adres#')
generiek = Namespace('https://data.vlaanderen.be/ns/generiek#')
mandaat = Namespace('http://data.vlaanderen.be/ns/mandaat#')
besluit = Namespace('http://data.vlaanderen.be/ns/besluit#')
lblodlg = Namespace('https://data.lblod.info/vocabularies/leidinggevenden/')
ere = Namespace('http://data.lblod.info/vocabularies/erediensten/')
ch = Namespace('http://data.lblod.info/vocabularies/contacthub/')
mu = Namespace('http://mu.semte.ch/vocabularies/core/')
ext = Namespace('http://mu.semte.ch/vocabularies/ext/')

cs = Namespace('http://data.vlaanderen.be/id/conceptscheme/')
c = Namespace('http://data.vlaanderen.be/id/concept/')
gift = Namespace('http://lblod.data.gift/')
gift_v = Namespace('http://lblod.data.gift/vocabularies/organisatie/')

mandataris_status = {
  "Effectief": URIRef("http://data.vlaanderen.be/id/concept/MandatarisStatusCode/21063a5b-912c-4241-841c-cc7fb3c73e75")
}

namespace_dict = {
  'dev': Namespace('http://contacthub-dev.lblod.info/id/'),
  'qa': Namespace('http://contacthub-qa.lblod.info/id/'),
  'local': Namespace('http://data.lblod.info/id/')
}

def get_namespace(mode):
  return namespace_dict[mode]