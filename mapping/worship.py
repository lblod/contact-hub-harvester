import pandas as pd
import numpy as np
from rdflib import Graph, Literal, RDF, URIRef, N
from rdflib.namespace import FOAF , XSD, DC, FOAF, SKOS, RDF, RDFS

import cleansing.worship as cls_worship
from helper.functions import add_literal, concept_uri, expor_data
import helper.namespaces as ns

def create_status_uri(g, data):
  for status in data['Status_EB'].dropna().unique():
    subject = concept_uri(ns.os, status)
    g.add((subject, RDF.type, SKOS.Concept))
    g.add((subject, SKOS.prefLabel, Literal(status, lang='nl')))
    g.add((subject, SKOS.definition, Literal(status, lang='nl')))
    if status.startswith('Operationeel'):
      g.add((subject, SKOS.broader, ns.os.actief))
    else:
      g.add((subject, SKOS.broader, ns.os.nietactief))

def main(file): 
  worship_raw = pd.read_excel(file)
  worship_cleansed = cls_worship.main(worship_raw)

  g = Graph()

  create_status_uri(g, worship_cleansed)
  
  for index, row in worship_cleansed.iterrows():
    abb_id = concept_uri(ns.lblod + 'organisatie/', str(row['organization_id']))
    g.add((abb_id, RDF.type, ns.org.Organization))

    g.add((abb_id, ns.regorg.orgStatus, concept_uri(ns.os, str(row['Status_EB']))))

    site_id = concept_uri(ns.lblod + 'vestiging/', str(row['organization_id']))
    g.add((site_id, RDF.type, ns.org.Site))

    address_id = concept_uri(ns.lblod + 'adresvoorstelling/', str(row['organization_id']))
    g.add((address_id, RDF.type, ns.locn.Address))
    add_literal(address_id, ns.locn.adminUnitL2, 'Provincie_EB Cleansed')
    add_literal(address_id, ns.locn.thoroughfare, 'Straat_EB')
    add_literal(address_id, ns.adres['Adresvoorstelling.huisnummer'], 'Huisnr_EB Cleansed', XSD.string)
    add_literal(address_id, ns.adres['Adresvoorstelling.busnummer'], 'Busnummer_EB Cleansed', XSD.string)
    add_literal(address_id, ns.locn.postCode, 'Postcode_EB Cleansed', XSD.string)
    add_literal(address_id, ns.adres.gemeenttenaam, 'Gemeente_EB Cleansed', XSD.string)
    g.add((address_id, ns.adres.land, Literal('België', lang='nl')))

    g.add((site_id, ns.organisatie.bestaatUit, address_id))
    g.add((abb_id, ns.org.hasPrimarySite, site_id))

    add_literal(abb_id, SKOS.prefLabel, 'Naam_EB')
    add_literal(abb_id, ns.regorg.legalName, 'Naam_EB')

    kbo_id = concept_uri(ns.lblod + 'gestructureerdeIdentificator/', str(row['KBO_EB Cleansed']))
    g.add((kbo_id, RDF.type, ns.generiek.GestructureerdeIdentificator))
    add_literal(kbo_id, ns.generiek.lokaleIdentificator, 'KBO_EB Cleansed', XSD.string)

    g.add((abb_id, ns.org.classification, ns.bestuur_van_de_eredienst))

    #Bestuur
    bestuur = concept_uri(ns.lblod + 'bestuursorgaan/', str(row['organization_id']))
    g.add((bestuur, RDF.type, ns.besluit.Bestuursorgaan))
    g.add((bestuur, ns.besluit.bestuurt, abb_id))

    bestuur_temporary = concept_uri(ns.lblod + 'bestuursorgaan/', str(row['organization_id']) + str(datetime.now().year))
    g.add((bestuur_temporary, RDF.type, ns.besluit.Bestuursorgaan))
    g.add((bestuur_temporary, ns.generiek.isTijdspecialisatieVan, bestuur))

    # Voorzitter
    voorzitter = concept_uri(ns.lblod + 'persoon/', str(row['Naam_voorzitter_EB First']) + str(row['Naam_voorzitter_EB Last']))
    g.add((voorzitter, RDF.type, ns.person.Person))
    add_literal(voorzitter, ns.persoon.gebruikteVoornaam, 'Naam_voorzitter_EB First')
    add_literal(voorzitter, FOAF.familyName, 'Naam_voorzitter_EB Last')

    ## Tel voorzitter - 
    voorzitter_site_id = concept_uri(ns.lblod + 'vestiging/', str(row['organization_id']) + str(row['Naam_voorzitter_EB First']) + str(row['Naam_voorzitter_EB Last']))
    g.add((voorzitter_site_id, RDF.type, ns.org.Site))
    g.add((voorzitter, ns.org.basedAt, voorzitter_site_id))

    voorzitter_contact_uri = concept_uri(ns.lblod + 'contactinfo/', str(row['organization_id']) + str(row['Naam_voorzitter_EB First']) + str(row['Naam_voorzitter_EB Last']) + 'Tel_voorzitter_EB 1')
    g.add((voorzitter_contact_uri, RDF.type, ns.schema.ContactPoint))
    g.add((voorzitter_site_id, ns.org.siteAddress, voorzitter_contact_uri))
    add_literal(voorzitter_contact_uri, ns.schema.telephone, 'Tel_voorzitter_EB 1')
    add_literal(voorzitter_contact_uri, ns.schema.email, 'Mail_voorzitter_EB Cleansed')  

    if str(row['Tel_voorzitter_EB 2']) != str(np.nan):
      voorzitter_contact_2_uri = concept_uri(np.lblod + 'contactinfo/', str(row['organization_id']) + str(row['Naam_voorzitter_EB First']) + str(row['Naam_voorzitter_EB Last']) + 'Tel_voorzitter_EB 2')
      g.add((voorzitter_contact_2_uri, RDF.type, np.schema.ContactPoint))
      g.add((voorzitter_site_id, np.org.siteAddress, voorzitter_contact_2_uri))
      add_literal(voorzitter_contact_2_uri, np.schema.telephone, 'Tel_voorzitter_EB 2')

    # Address
    voorzitter_address_id = concept_uri(np.lblod + 'adresvoorstelling/', str(row['organization_id']) + str(row['Naam_voorzitter_EB First']) + str(row['Naam_voorzitter_EB Last'])) 
    g.add((voorzitter_address_id, RDF.type, np.locn.Address))
    g.add((voorzitter_site_id, np.organisatie.bestaatUit, voorzitter_address_id))
    add_literal(voorzitter_address_id, ns.locn.fullAddress, 'Adres_voorzitter_EB Cleansed')
    
    ## Mandataris
    voorzitter_mandataris = concept_uri(ns.lblod + 'mandataris/', str(row['organization_id']) + str(row['Naam_voorzitter_EB First']) + str(row['Naam_voorzitter_EB Last']) + 'voorzitter')
    g.add((voorzitter_mandataris, RDF.type, ns.mandaat.Mandataris))
    g.add((voorzitter, ns.mandaat.isAangesteldAls, voorzitter_mandataris))
    g.add((voorzitter_mandataris, ns.mandaat.isBestuurlijkeAliasVan, voorzitter))
    #start
    #einde
    #status ~ cf loket lokale besturen PoC https://poc-form-builder.relance.s.redpencil.io/codelijsten
    voorzitter_mandaat = concept_uri(ns.lblod + 'mandaat/', str(row['organization_id']) + str(row['Naam_voorzitter_EB First']) + str(row['Naam_voorzitter_EB Last']))
    g.add((voorzitter_mandaat, RDF.type, ns.mandaat.Mandaat))
    g.add((voorzitter_mandataris, ns.org.holds, voorzitter_mandaat))
    g.add((voorzitter_mandaat, ns.org.role, ns.voorzitter_concept))

    g.add((bestuur_temporary, ns.org.hasPost, voorzitter_mandaat))
    #g.add((voorzitter_mandaat, org.holds, bestuur_temporary))
    
    #Secretaris
    secretaris =  concept_uri(ns.lblod + 'persoon/', str(row['Naam_secretaris_EB First']) + str(row['Naam_secretaris_EB Last']))
    g.add((secretaris, RDF.type, ns.person.Person))
    add_literal(secretaris, ns.persoon.gebruikteVoornaam, 'Naam_secretaris_EB First')
    add_literal(secretaris, FOAF.familyName, 'Naam_secretaris_EB Last')
    
    ## Tel secretaris
    secretaris_vestiging_uri = concept_uri(ns.lblod + 'vestiging/', str(row['organization_id']) + str(row['Naam_secretaris_EB First']) + str(row['Naam_secretaris_EB Last']))
    g.add((secretaris_vestiging_uri, RDF.type, ns.org.Site))
    g.add((secretaris, ns.org.basedAt, secretaris_vestiging_uri))

    secretaris_contact_uri = concept_uri(ns.lblod + 'contactinfo/', str(row['organization_id']) + str(row['Naam_secretaris_EB First']) + str(row['Naam_secretaris_EB Last']) + 'Tel_secretaris_EB 1')
    g.add((secretaris_contact_uri, RDF.type, ns.schema.ContactPoint))
    g.add((secretaris_vestiging_uri, ns.organisatie.contactinfo, secretaris_contact_uri))
    add_literal(secretaris_contact_uri, ns.schema.telephone, 'Tel_secretaris_EB 1')
    add_literal(secretaris_contact_uri, ns.schema.email, 'Mail_secretaris_EB Cleansed')

    if str(row['Tel_secretaris_EB 2']) != str(np.nan):
      secretaris_contact_2_uri = concept_uri(ns.lblod + 'contactinfo/', str(row['organization_id']) + str(row['Naam_secretaris_EB First']) + str(row['Naam_secretaris_EB Last']) + 'Tel_secretaris_EB 2')
      g.add((secretaris_contact_2_uri, RDF.type, ns.schema.ContactPoint))
      g.add((secretaris_vestiging_uri, ns.org.siteAddress, secretaris_contact_2_uri))
      add_literal(secretaris_contact_2_uri, ns.schema.telephone, 'Tel_secretaris_EB 2')

    secretaris_address_id = concept_uri(ns.lblod + 'adresvoorstelling/', str(row['organization_id']) + str(row['Naam_secretaris_EB First']) + str(row['Naam_secretaris_EB Last'])) 
    g.add((secretaris_address_id, RDF.type, ns.locn.Address))
    g.add((secretaris_vestiging_uri, ns.organisatie.bestaatUit, secretaris_address_id))
    add_literal(secretaris_address_id, ns.locn.fullAddress, 'Adres_secretaris_EB Cleansed')

    #Mandataris
    secretaris_mandataris = concept_uri(ns.lblod + 'mandataris/', str(row['organization_id']) + str(row['Naam_secretaris_EB First']) + str(row['Naam_secretaris_EB Last']) + 'secretaris')
    g.add((secretaris_mandataris, RDF.type, ns.mandaat.Mandataris))
    g.add((secretaris, ns.mandaat.isAangesteldAls, secretaris_mandataris))
    g.add((secretaris_mandataris, ns.mandaat.isBestuurlijkeAliasVan, secretaris))
    #start
    #einde
    #status
    secretaris_mandaat = concept_uri(ns.lblod + 'mandaat/', str(row['organization_id']) + str(row['Naam_secretaris_EB First']) + str(row['Naam_secretaris_EB Last']))
    g.add((secretaris_mandaat, RDF.type, ns.mandaat.Mandaat))
    g.add((secretaris_mandataris, ns.org.holds, secretaris_mandaat))
    g.add((secretaris_mandaat, ns.org.role, ns.secretaris_concept))
    
    g.add((bestuur_temporary, ns.org.hasPost, secretaris_mandaat))
    #g.add((secretaris_mandaat, org.holds, bestuur_temporary))

    #Penningmeester
    penningmeester =  concept_uri(ns.lblod + 'persoon/', str(row['Naam_penningmeester_EB First']) + str(row['Naam_penningmeester_EB Last']))
    g.add((penningmeester, RDF.type, ns.person.Person))
    add_literal(penningmeester, ns.persoon.gebruikteVoornaam, 'Naam_penningmeester_EB First')
    add_literal(penningmeester, FOAF.familyName, 'Naam_penningmeester_EB Last')
    
    ## Tel penningmeester
    penningmeester_vestiging_uri = concept_uri(ns.lblod + 'vestiging/', str(row['organization_id']) + str(row['Naam_penningmeester_EB First']) + str(row['Naam_penningmeester_EB Last']))
    g.add((penningmeester_vestiging_uri, RDF.type, ns.org.Site))
    g.add((penningmeester, ns.org.basedAt, penningmeester_vestiging_uri))

    penningmeester_contact_uri = concept_uri(ns.lblod + 'contactinfo/', str(row['organization_id']) + str(row['Naam_penningmeester_EB First']) + str(row['Naam_penningmeester_EB Last']) + 'Tel_penningmeester_EB 1')
    g.add((penningmeester_contact_uri, RDF.type, ns.schema.ContactPoint))
    g.add((penningmeester_vestiging_uri, ns.organisatie.contactinfo, penningmeester_contact_uri))
    add_literal(penningmeester_contact_uri, ns.schema.telephone, 'Tel_penningmeester_EB 1')
    add_literal(penningmeester_contact_uri, ns.schema.email, 'Mail_penningmeester_EB Cleansed')

    if str(row['Tel_penningmeester_EB 2']) != str(np.nan):
      penningmeester_contact_2_uri = concept_uri(ns.lblod + 'contactinfo/', str(row['organization_id']) + str(row['Naam_penningmeester_EB First']) + str(row['Naam_penningmeester_EB Last']) + 'Tel_penningmeester_EB 2')
      g.add((penningmeester_contact_2_uri, RDF.type, ns.schema.ContactPoint))
      g.add((penningmeester_vestiging_uri, ns.organisatie.contactinfo, penningmeester_contact_2_uri))
      add_literal(penningmeester_contact_2_uri, ns.schema.telephone, 'Tel_penningmeester_EB 2')

    penningmeester_address_id = concept_uri(ns.lblod + 'adresvoorstelling/', str(row['organization_id']) + str(row['Naam_penningmeester_EB First']) + str(row['Naam_penningmeester_EB Last'])) 
    g.add((penningmeester_address_id, RDF.type, ns.locn.Address))
    g.add((penningmeester_vestiging_uri, ns.organisatie.bestaatUit, penningmeester_address_id))
    add_literal(penningmeester_address_id, ns.locn.fullAddress, 'Adres_penningmeester_EB Cleansed')

    #Mandataris
    penningmeester_mandataris = concept_uri(ns.lblod + 'mandataris/', str(row['organization_id']) + str(row['Naam_penningmeester_EB First']) + str(row['Naam_penningmeester_EB Last']) + 'penningmeester')
    g.add((penningmeester_mandataris, RDF.type, ns.mandaat.Mandataris))
    g.add((penningmeester, ns.mandaat.isAangesteldAls, penningmeester_mandataris))
    g.add((penningmeester_mandataris, ns.mandaat.isBestuurlijkeAliasVan, penningmeester))
    #start
    #einde
    #status
    penningmeester_mandaat = concept_uri(ns.lblod + 'mandaat/', str(row['organization_id']) + str(row['Naam_penningmeester_EB First']) + str(row['Naam_penningmeester_EB Last']))
    g.add((penningmeester_mandaat, RDF.type, ns.mandaat.Mandaat))
    g.add((penningmeester_mandataris, ns.org.holds, penningmeester_mandaat))
    g.add((penningmeester_mandaat, ns.org.role, ns.penningmeester_concept))
    
    g.add((bestuur_temporary, ns.org.hasPost, penningmeester_mandaat))
    #g.add((penningmeester_mandaat, org.holds, bestuur_temporary))

    export_data(g)
  
  