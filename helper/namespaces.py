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

organisatie = Namespace('http://data.vlaanderen.be/ns/organisatie#')
persoon = Namespace('http://data.vlaanderen.be/ns/persoon#')
adres = Namespace('http://data.vlaanderen.be/ns/adres#')
generiek = Namespace('http://data.vlaanderen.be/ns/generiek#')
mandaat = Namespace('http://data.vlaanderen.be/ns/mandaat#')
besluit = Namespace('http://data.vlaanderen.be/ns/besluit#')
lblodlg = Namespace('https://data.lblod.info/vocabularies/leidinggevenden')
mu = Namespace('http://mu.semte.ch/vocabularies/core/')

#lblod = Namespace('http://contacthub-dev.lblod.info/id/')
lblod = Namespace('http://contacthub-qa.lblod.info/id/')
os = Namespace('https://data.vlaanderen.be/id/concept/OrganisatieStatus/')
oc = Namespace('https://data.vlaanderen.be/id/concept/OrganisatieClassificatie/')


# Predefined concepts:
bestuurseenheid_classification_code = {
  "eredienst": URIRef("http://data.vlaanderen.be/id/concept/BestuurseenheidClassificatieCode/66ec74fd-8cfc-4e16-99c6-350b35012e86"),
  "centraal": URIRef("http://data.vlaanderen.be/id/concept/BestuurseenheidClassificatieCode/f9cac08a-13c1-49da-9bcb-f650b0604054")
}

bestursfunctie_code = {
  "Algemeen Directeur": URIRef("https://data.vlaanderen.be/id/concept/BestuursfunctieCode/39e08271-68db-4282-897f-5cba88c71862"),
  "Financieel Directeur": URIRef("https://data.vlaanderen.be/id/concept/BestuursfunctieCode/6d4cf4dd-2080-4752-8733-d02a036b2df0"),
  "Adjunct Financieel Directeur": URIRef("https://data.vlaanderen.be/id/concept/BestuursfunctieCode/3200ffc1-bb72-4235-a81c-64aa578b0789"),
  "Adjunct Algemeen Directeur": URIRef("https://data.vlaanderen.be/id/concept/BestuursfunctieCode/f7b4e17b-6f4e-48e7-a558-bce61669f59a"),
  "Voorzitter": URIRef("http://data.vlaanderen.be/id/concept/BestuursfunctieCode/a38959ecec530654de15ab06c5b1f276"),
  "Secretaris": URIRef("http://data.vlaanderen.be/id/concept/BestuursFunctieCode/f960d7b1488d049a982b23251025d9f6"),
  "Penningmeester": URIRef("http://data.vlaanderen.be/id/concept/BestuursFunctieCode/c456aedca0643d3e71919f16ac181da8"),
  "Lid": URIRef("http://data.vlaanderen.be/id/concept/BestuursfunctieCode/")
}

functionaris_status = {
  "Waarnemend": URIRef("https://data.vlaanderen.be/id/concept/MandatarisStatusCode/e1ca6edd-55e1-4288-92a5-53f4cf71946a"),
  "Effectief": URIRef("https://data.vlaanderen.be/id/concept/MandatarisStatusCode/21063a5b-912c-4241-841c-cc7fb3c73e75")
}