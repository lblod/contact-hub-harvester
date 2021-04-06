from rdflib import URIRef, Namespace
from helper.functions import concept_uri 

org = Namespace('http://www.w3.org/ns/org#')
locn = Namespace('http://www.w3.org/ns/locn#')
dc_terms= Namespace('http://purl.org/dc/terms/')
schema = Namespace('http://schema.org/')
regorg = Namespace('http://www.w3.org/ns/regorg#')
person = Namespace('http://www.w3.org/ns/person#')
vcard = Namespace('http://www.w3.org/2006/vcard/ns#')
dbpedia = Namespace('https://dbpedia.org/ontology/')

organisatie = Namespace('https://data.vlaanderen.be/ns/organisatie#')
persoon = Namespace('https://data.vlaanderen.be/ns/persoon#')
adres = Namespace('https://data.vlaanderen.be/ns/adres#')
generiek = Namespace('https://data.vlaanderen.be/ns/generiek#')
mandaat = Namespace('http://data.vlaanderen.be/ns/mandaat#')
besluit = Namespace('http://data.vlaanderen.be/ns/besluit#')

#lblod = Namespace('https://contacthub-dev.lblod.info/id/')
lblod = Namespace('https://contacthub-qa.lblod.info/id/')
os = Namespace('https://data.vlaanderen.be/id/concept/OrganisatieStatus/')
oc = Namespace('https://data.vlaanderen.be/id/concept/OrganisatieClassificatie/')


# Predefined concepts:
bestuur_van_de_eredienst = URIRef("http://data.vlaanderen.be/id/concept/BestuurseenheidClassificatieCode/66ec74fd-8cfc-4e16-99c6-350b35012e86")

voorzitter_concept = concept_uri(lblod + 'concept/BestuursFunctieCode/', 'voorzitter')
secretaris_concept = concept_uri(lblod + 'concept/BestuursFunctieCode/', 'secretaris')
penningmeester_concept = concept_uri(lblod + 'concept/BestuursFunctieCode/', 'penningmeester')