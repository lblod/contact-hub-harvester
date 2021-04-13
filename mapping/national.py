import pandas as pd
from datetime import datetime
from rdflib import Graph, Literal, RDF
from rdflib.namespace import XSD, FOAF, SKOS, RDF

from helper.functions import add_literal, concept_uri, export_data
import helper.namespaces as ns


def create_category_uri(g, data):
  for category in data['Classification'].unique():
    category_id, _ = concept_uri(ns.oc, category)
    g.add((category_id, RDF.type, SKOS.Concept))
    g.add((category_id, SKOS.prefLabel, Literal(category, lang='nl')))

def main(file):
  national_raw = pd.read_excel(file)

  g = Graph()

  create_category_uri(g, national_raw)

  for _, row in national_raw.iterrows():
    abb_id, _ = concept_uri(ns.lblod + 'organisatie/', str(row['representatief orgaan']))

    g.add((abb_id, RDF.type, ns.org.Organization))

    add_literal(g, abb_id, SKOS.prefLabel, str(row['representatief orgaan']), XSD.string)

    classification, _ = concept_uri(ns.oc, row['Classification'])
    g.add((abb_id, ns.org.classification, classification))

    site_id, _ = concept_uri(ns.lblod + 'vesting/', str(row['representatief orgaan']))
    g.add((site_id, RDF.type, ns.org.Site))

    contact_id, _ = concept_uri(ns.lblod + 'contactpunt/', str(row['representatief orgaan']))
    g.add((contact_id, RDF.type, ns.schema.ContactPoint))
    add_literal(g, contact_id, FOAF.page, str(row['Website']), XSD.anyURI)
    add_literal(g, contact_id, ns.schema.telephone, str(row['Telefoon']), XSD.string)
    add_literal(g, contact_id, ns.schema.faxNumber, str(row['Fax']), XSD.string)
    g.add((site_id, ns.schema.siteAddress, contact_id))
    
    address_id, _ = concept_uri(ns.lblod + 'adres/', str(row['representatief orgaan']))
    g.add((address_id, RDF.type, ns.locn.Address))
    add_literal(g, address_id, ns.locn.thoroughfare, str(row['Straatnaam']))
    add_literal(g, address_id, ns.adres['Adresvoorstelling.huisnummer'], str(row['Huisnummer']), XSD.string)
    add_literal(g, address_id, ns.adres['Adresvoorstelling.busnummer'], str(row['Busnummer']), XSD.string)
    add_literal(g, address_id, ns.locn.postCode, str(row['Postcode']), XSD.string)
    add_literal(g, address_id, ns.adres.gemeenttenaam, str(row['Gemeentenaam']))
    add_literal(g, address_id, ns.locn.adminUnitL2, str(row['Provincie']))
    g.add((address_id, ns.adres.land, Literal('België', lang='nl')))
    g.add((site_id, ns.organisatie.bestaatUit, address_id))

    g.add((abb_id, ns.org.hasPrimarySite, site_id))

    g.add((abb_id, ns.regorg.orgStatus, ns.os.actief))    

    #Bestuur
    #bestuur = concept_uri(ns.lblod + 'bestuursorgaan/', str(row['representatief orgaan']))
    #g.add((bestuur, RDF.type, ns.besluit.Bestuursorgaan))
    #g.add((bestuur, ns.besluit.bestuurt, abb_id))

    bestuur_temporary, _ = concept_uri(ns.lblod + 'bestuursorgaan/', (row['representatief orgaan'] + str(datetime.now())))
    g.add((bestuur_temporary, RDF.type, ns.besluit.Bestuursorgaan))
    g.add((bestuur_temporary, ns.generiek.isTijdspecialisatieVan, abb_id))

    person_id, _ = concept_uri(ns.lblod + 'persoon/', str(row['Gebruikte Voornaam']) + str(row['Achternaam']))
    g.add((person_id, RDF.type, ns.person.Person))
    add_literal(g, person_id, ns.persoon.gebruikteVoornaam, str(row['Gebruikte Voornaam']))
    add_literal(g, person_id, FOAF.familyName, str(row['Achternaam']))

    ## Mandaat
    rol_mandaat, _ = concept_uri(ns.lblod + 'mandaat/', str(row['representatief orgaan']) + str(row['Gebruikte Voornaam']) + str(row['Achternaam']))
    g.add((rol_mandaat, RDF.type, ns.mandaat.Mandaat))
    g.add((rol_mandaat, ns.org.role, ns.bestursfunctie_code[row['Rol']]))
    g.add((rol_mandaat, ns.org.postIn, bestuur_temporary))
    g.add((bestuur_temporary, ns.org.hasPost, rol_mandaat))
    
    ## Mandataris
    mandataris, _ = concept_uri(ns.lblod + 'mandataris/', str(row['representatief orgaan']) + str(row['Gebruikte Voornaam']) + str(row['Achternaam']) + str(row['Rol'].lower().replace(" ", "")))
    g.add((mandataris, RDF.type, ns.mandaat.Mandataris))
    g.add((mandataris, ns.mandaat.isBestuurlijkeAliasVan, person_id))
    g.add((mandataris, ns.org.holds, rol_mandaat))
    g.add((person_id, ns.mandaat.isAangesteldAls, mandataris))
    g.add((rol_mandaat, ns.org.heldBy, mandataris))
    #start
    #einde
    #status ~ cf loket lokale besturen PoC https://poc-form-builder.relance.s.redpencil.io/codelijsten
  
  export_data(g, 'national-dev')

    


