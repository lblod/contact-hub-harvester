from rdflib import URIRef, Namespace
from helper.functions import concept_uri 

org = Namespace('http://www.w3.org/ns/org#')
locn = Namespace('http://www.w3.org/ns/locn#')
dc_terms= Namespace('http://purl.org/dc/terms/')
schema = Namespace('http://schema.org/')
regorg = Namespace('http://www.w3.org/ns/regorg#')
person = Namespace('http://www.w3.org/ns/person#')
vcard = Namespace('http://www.w3.org/2006/vcard/ns#')
dbpedia = Namespace('http://dbpedia.org/ontology/')
adms = Namespace('http://www.w3.org/ns/adms#')
euro = Namespace('http://data.europa.eu/m8g/')

organisatie = Namespace('http://data.vlaanderen.be/ns/organisatie#')
persoon = Namespace('http://data.vlaanderen.be/ns/persoon#')
adres = Namespace('http://data.vlaanderen.be/ns/adres#')
generiek = Namespace('http://data.vlaanderen.be/ns/generiek#')
mandaat = Namespace('http://data.vlaanderen.be/ns/mandaat#')
besluit = Namespace('http://data.vlaanderen.be/ns/besluit#')
lblodlg = Namespace('https://data.lblod.info/vocabularies/leidinggevenden/')
ere = Namespace('http://data.lblod.info/vocabularies/erediensten/')
mu = Namespace('http://mu.semte.ch/vocabularies/core/')

#lblod = Namespace('http://contacthub-dev.lblod.info/id/')
lblod = Namespace('http://contacthub-qa.lblod.info/id/')
#lblod = Namespace('http://data.lblod.info/id/')

cs = Namespace('http://data.vlaanderen.be/id/conceptscheme/')
c = Namespace('http://data.vlaanderen.be/id/concepts/')

functionaris_status = {
  "Waarnemend": URIRef("https://data.vlaanderen.be/id/concept/MandatarisStatusCode/e1ca6edd-55e1-4288-92a5-53f4cf71946a"),
  "Effectief": URIRef("https://data.vlaanderen.be/id/concept/MandatarisStatusCode/21063a5b-912c-4241-841c-cc7fb3c73e75")
}