import pandas as pd
import numpy as np
from datetime import datetime
from rdflib import Graph, Literal, RDF, URIRef
from rdflib.namespace import FOAF , XSD, DC, FOAF, SKOS, RDF, RDFS

import cleansing.worship as cls_worship
from helper.functions import add_literal, concept_uri, export_data
import helper.namespaces as ns

def create_status_uri(g, data):
  for status in data['Status_EB'].dropna().unique():
    subject = concept_uri(ns.os, status)
    g.add((subject, RDF.type, SKOS.Concept))
    g.add((subject, SKOS.prefLabel, Literal(status, lang='nl')))
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
    add_literal(g, address_id, ns.locn.adminUnitL2, str(row['Provincie_EB Cleansed']))
    add_literal(g, address_id, ns.locn.thoroughfare, str(row['Straat_EB']))
    add_literal(g, address_id, ns.adres['Adresvoorstelling.huisnummer'], str(row['Huisnr_EB Cleansed']), XSD.string)
    add_literal(g, address_id, ns.adres['Adresvoorstelling.busnummer'], str(row['Busnummer_EB Cleansed']), XSD.string)
    add_literal(g, address_id, ns.locn.postCode, str(row['Postcode_EB Cleansed']), XSD.string)
    add_literal(g, address_id, ns.adres.gemeenttenaam, str(row['Gemeente_EB Cleansed']), XSD.string)
    g.add((address_id, ns.adres.land, Literal('België', lang='nl')))

    g.add((site_id, ns.organisatie.bestaatUit, address_id))
    g.add((abb_id, ns.org.hasPrimarySite, site_id))

    add_literal(g, abb_id, SKOS.prefLabel, str(row['Naam_EB']))
    add_literal(g, abb_id, ns.regorg.legalName, str(row['Naam_EB']))

    kbo_id = concept_uri(ns.lblod + 'gestructureerdeIdentificator/', str(row['KBO_EB Cleansed']))
    g.add((kbo_id, RDF.type, ns.generiek.GestructureerdeIdentificator))
    add_literal(g, kbo_id, ns.generiek.lokaleIdentificator, str(row['KBO_EB Cleansed']), XSD.string)

    g.add((abb_id, ns.org.classification, ns.bestuur_van_de_eredienst))

    # Bestuurorgaan
    #bestuur = concept_uri(ns.lblod + 'bestuursorgaan/', str(row['organization_id']))
    #g.add((bestuur, RDF.type, ns.besluit.Bestuursorgaan))
    #g.add((bestuur, ns.besluit.bestuurt, abb_id))

    # Bestuursorgaan (in bestuursperiode)
    bestuur_temporary = concept_uri(ns.lblod + 'bestuursorgaan/', str(row['organization_id']) + str(datetime.now().year))
    g.add((bestuur_temporary, RDF.type, ns.besluit.Bestuursorgaan))
    g.add((bestuur_temporary, ns.generiek.isTijdspecialisatieVan, abb_id))

    # Voorzitter
    voorzitter = concept_uri(ns.lblod + 'persoon/', str(row['Naam_voorzitter_EB First']) + str(row['Naam_voorzitter_EB Last']))
    g.add((voorzitter, RDF.type, ns.person.Person))
    add_literal(g, voorzitter, ns.persoon.gebruikteVoornaam, str(row['Naam_voorzitter_EB First']))
    add_literal(g, voorzitter, FOAF.familyName, str(row['Naam_voorzitter_EB Last']))

    ## Voorzitter - Vesting
    voorzitter_vesting_uri = concept_uri(ns.lblod + 'vestiging/', str(row['organization_id']) + str(row['Naam_voorzitter_EB First']) + str(row['Naam_voorzitter_EB Last']))
    g.add((voorzitter_vesting_uri, RDF.type, ns.org.Site))
    g.add((voorzitter, ns.org.basedAt, voorzitter_vesting_uri))

    ### Voorzitter - Contact punt
    voorzitter_contact_uri = concept_uri(ns.lblod + 'contactpunt/', str(row['organization_id']) + str(row['Naam_voorzitter_EB First']) + str(row['Naam_voorzitter_EB Last']) + str(row['Tel_voorzitter_EB 1']))
    g.add((voorzitter_contact_uri, RDF.type, ns.schema.ContactPoint))
    g.add((voorzitter_vesting_uri, ns.org.siteAddress, voorzitter_contact_uri))
    add_literal(voorzitter_contact_uri, ns.schema.telephone, str(row['Tel_voorzitter_EB 1']))
    add_literal(voorzitter_contact_uri, ns.schema.email, str(row['Mail_voorzitter_EB Cleansed']))  

    if str(row['Tel_voorzitter_EB 2']) != str(np.nan):
      voorzitter_contact_2_uri = concept_uri(ns.lblod + 'contactpunt/', str(row['organization_id']) + str(row['Naam_voorzitter_EB First']) + str(row['Naam_voorzitter_EB Last']) + str(row['Tel_voorzitter_EB 2']))
      g.add((voorzitter_contact_2_uri, RDF.type, ns.schema.ContactPoint))
      g.add((voorzitter_vesting_uri, ns.org.siteAddress, voorzitter_contact_2_uri))
      add_literal(voorzitter_contact_2_uri, ns.schema.telephone, str(row['Tel_voorzitter_EB 2']))

    ### Voorzitter - Adres
    voorzitter_address_id = concept_uri(ns.lblod + 'adresvoorstelling/', str(row['organization_id']) + str(row['Naam_voorzitter_EB First']) + str(row['Naam_voorzitter_EB Last'])) 
    g.add((voorzitter_address_id, RDF.type, ns.locn.Address))
    g.add((voorzitter_vesting_uri, ns.organisatie.bestaatUit, voorzitter_address_id))
    add_literal(voorzitter_address_id, ns.locn.fullAddress, str(row['Adres_voorzitter_EB Cleansed']))
    
    ## Voorzitter - Mandaat
    voorzitter_mandaat = concept_uri(ns.lblod + 'mandaat/', str(row['organization_id']) + str(row['Naam_voorzitter_EB First']) + str(row['Naam_voorzitter_EB Last']))
    g.add((voorzitter_mandaat, RDF.type, ns.mandaat.Mandaat))
    g.add((voorzitter_mandaat, ns.org.role, ns.bestursfunctie_code["Voorzitter"]))
    g.add((voorzitter_mandaat, ns.org.postIn, bestuur_temporary))
    g.add((bestuur_temporary, ns.org.hasPost, voorzitter_mandaat))  

    ## Voorzitter - Mandataris
    voorzitter_mandataris = concept_uri(ns.lblod + 'mandataris/', str(row['organization_id']) + str(row['Naam_voorzitter_EB First']) + str(row['Naam_voorzitter_EB Last']) + 'voorzitter')
    g.add((voorzitter_mandataris, RDF.type, ns.mandaat.Mandataris))
    g.add((voorzitter_mandataris, ns.mandaat.isBestuurlijkeAliasVan, voorzitter))
    g.add((voorzitter_mandataris, ns.org.holds, voorzitter_mandaat))
    add_literal(g, voorzitter_mandataris, ns.mandaat.start, str(row['Datum verkiezing voorzitter']), XSD.dateTime)
    #einde
    #status ~ cf loket lokale besturen PoC https://poc-form-builder.relance.s.redpencil.io/codelijsten
    g.add((voorzitter, ns.mandaat.isAangesteldAls, voorzitter_mandataris))

    ####    
    # Secretaris
    secretaris =  concept_uri(ns.lblod + 'persoon/', str(row['Naam_secretaris_EB First']) + str(row['Naam_secretaris_EB Last']))
    g.add((secretaris, RDF.type, ns.person.Person))
    add_literal(g, secretaris, ns.persoon.gebruikteVoornaam, str(row['Naam_secretaris_EB First']))
    add_literal(g, secretaris, FOAF.familyName, str(row['Naam_secretaris_EB Last']))
    
    ## Secretaris - Vesting
    secretaris_vestiging_uri = concept_uri(ns.lblod + 'vestiging/', str(row['organization_id']) + str(row['Naam_secretaris_EB First']) + str(row['Naam_secretaris_EB Last']))
    g.add((secretaris_vestiging_uri, RDF.type, ns.org.Site))
    g.add((secretaris, ns.org.basedAt, secretaris_vestiging_uri))

    ### Secretaris - Contact punt
    secretaris_contact_uri = concept_uri(ns.lblod + 'contactpunt/', str(row['organization_id']) + str(row['Naam_secretaris_EB First']) + str(row['Naam_secretaris_EB Last']) + str(row['Tel_secretaris_EB 1']))
    g.add((secretaris_contact_uri, RDF.type, ns.schema.ContactPoint))
    g.add((secretaris_vestiging_uri, ns.org.siteAddress, secretaris_contact_uri))
    add_literal(g, secretaris_contact_uri, ns.schema.telephone, str(row['Tel_secretaris_EB 1']))
    add_literal(g, secretaris_contact_uri, ns.schema.email, str(row['Mail_secretaris_EB Cleansed']))

    if str(row['Tel_secretaris_EB 2']) != str(np.nan):
      secretaris_contact_2_uri = concept_uri(ns.lblod + 'contactinfo/', str(row['organization_id']) + str(row['Naam_secretaris_EB First']) + str(row['Naam_secretaris_EB Last']) + str(row['Tel_secretaris_EB 2']))
      g.add((secretaris_contact_2_uri, RDF.type, ns.schema.ContactPoint))
      g.add((secretaris_vestiging_uri, ns.org.siteAddress, secretaris_contact_2_uri))
      add_literal(g, secretaris_contact_2_uri, ns.schema.telephone, str(row['Tel_secretaris_EB 2']))

    ### Secretaris - Adres
    secretaris_address_id = concept_uri(ns.lblod + 'adresvoorstelling/', str(row['organization_id']) + str(row['Naam_secretaris_EB First']) + str(row['Naam_secretaris_EB Last'])) 
    g.add((secretaris_address_id, RDF.type, ns.locn.Address))
    g.add((secretaris_vestiging_uri, ns.organisatie.bestaatUit, secretaris_address_id))
    add_literal(g, secretaris_address_id, ns.locn.fullAddress, str(row['Adres_secretaris_EB Cleansed']))

    ## Secretaris - Mandaat
    secretaris_mandaat = concept_uri(ns.lblod + 'mandaat/', str(row['organization_id']) + str(row['Naam_secretaris_EB First']) + str(row['Naam_secretaris_EB Last']))
    g.add((secretaris_mandaat, RDF.type, ns.mandaat.Mandaat))
    g.add((secretaris_mandaat, ns.org.role, ns.bestursfunctie_code["Secretaris"]))
    g.add((secretaris_mandaat, ns.org.postIn, bestuur_temporary))
    g.add((bestuur_temporary, ns.org.hasPost, secretaris_mandaat))
   
    ## Secreataris - Mandataris
    secretaris_mandataris = concept_uri(ns.lblod + 'mandataris/', str(row['organization_id']) + str(row['Naam_secretaris_EB First']) + str(row['Naam_secretaris_EB Last']) + 'secretaris')
    g.add((secretaris_mandataris, RDF.type, ns.mandaat.Mandataris))
    g.add((secretaris_mandataris, ns.mandaat.isBestuurlijkeAliasVan, secretaris))
    g.add((secretaris_mandataris, ns.org.holds, secretaris_mandaat))
    add_literal(g, secretaris_mandataris, ns.mandaat.start, str(row['Datum verkiezing secretaris']), XSD.dateTime)
    #einde
    #status
    g.add((secretaris, ns.mandaat.isAangesteldAls, secretaris_mandataris))

    ####
    # Penningmeester
    penningmeester =  concept_uri(ns.lblod + 'persoon/', str(row['Naam_penningmeester_EB First']) + str(row['Naam_penningmeester_EB Last']))
    g.add((penningmeester, RDF.type, ns.person.Person))
    add_literal(g, penningmeester, ns.persoon.gebruikteVoornaam, str(row['Naam_penningmeester_EB First']))
    add_literal(g, penningmeester, FOAF.familyName, str(row['Naam_penningmeester_EB Last']))
    
    ## Penningmeester - Vesting
    penningmeester_vestiging_uri = concept_uri(ns.lblod + 'vestiging/', str(row['organization_id']) + str(row['Naam_penningmeester_EB First']) + str(row['Naam_penningmeester_EB Last']))
    g.add((penningmeester_vestiging_uri, RDF.type, ns.org.Site))
    g.add((penningmeester, ns.org.basedAt, penningmeester_vestiging_uri))

    ### Penningmeester - Contact punt
    penningmeester_contact_uri = concept_uri(ns.lblod + 'contactinfo/', str(row['organization_id']) + str(row['Naam_penningmeester_EB First']) + str(row['Naam_penningmeester_EB Last']) + str(row['Tel_penningmeester_EB 1']))
    g.add((penningmeester_contact_uri, RDF.type, ns.schema.ContactPoint))
    g.add((penningmeester_vestiging_uri, ns.org.siteAddress, penningmeester_contact_uri))
    add_literal(g, penningmeester_contact_uri, ns.schema.telephone, str(row['Tel_penningmeester_EB 1']))
    add_literal(g, penningmeester_contact_uri, ns.schema.email, str(row['Mail_penningmeester_EB Cleansed']))

    if str(row['Tel_penningmeester_EB 2']) != str(np.nan):
      penningmeester_contact_2_uri = concept_uri(ns.lblod + 'contactinfo/', str(row['organization_id']) + str(row['Naam_penningmeester_EB First']) + str(row['Naam_penningmeester_EB Last']) + str(row['Tel_penningmeester_EB 2']))
      g.add((penningmeester_contact_2_uri, RDF.type, ns.schema.ContactPoint))
      g.add((penningmeester_vestiging_uri, ns.org.siteAddress, penningmeester_contact_2_uri))
      add_literal(g, penningmeester_contact_2_uri, ns.schema.telephone, str(row['Tel_penningmeester_EB 2']))

    ### Penningmeester - Adres
    penningmeester_address_id = concept_uri(ns.lblod + 'adresvoorstelling/', str(row['organization_id']) + str(row['Naam_penningmeester_EB First']) + str(row['Naam_penningmeester_EB Last'])) 
    g.add((penningmeester_address_id, RDF.type, ns.locn.Address))
    g.add((penningmeester_vestiging_uri, ns.organisatie.bestaatUit, penningmeester_address_id))
    add_literal(g, penningmeester_address_id, ns.locn.fullAddress, str(row['Adres_penningmeester_EB Cleansed']))

    ## Penningmeester - Mandaat
    penningmeester_mandaat = concept_uri(ns.lblod + 'mandaat/', str(row['organization_id']) + str(row['Naam_penningmeester_EB First']) + str(row['Naam_penningmeester_EB Last']))
    g.add((penningmeester_mandaat, RDF.type, ns.mandaat.Mandaat))
    g.add((penningmeester_mandaat, ns.org.role, ns.bestursfunctie_code["Penningmeester"]))
    g.add((penningmeester_mandaat, ns.org.postIn, bestuur_temporary))
    g.add((bestuur_temporary, ns.org.hasPost, penningmeester_mandaat))

    ## Penningmeester - Mandataris
    penningmeester_mandataris = concept_uri(ns.lblod + 'mandataris/', str(row['organization_id']) + str(row['Naam_penningmeester_EB First']) + str(row['Naam_penningmeester_EB Last']) + 'penningmeester')
    g.add((penningmeester_mandataris, RDF.type, ns.mandaat.Mandataris))
    g.add((penningmeester, ns.mandaat.isAangesteldAls, penningmeester_mandataris))
    g.add((penningmeester_mandataris, ns.org.holds, penningmeester_mandaat))
    g.add((penningmeester_mandataris, ns.mandaat.isBestuurlijkeAliasVan, penningmeester))
    add_literal(g, penningmeester_mandataris, ns.mandaat.start, str(row['Datum verkiezing penningmeester']), XSD.dateTime)
    #einde
    #status

    ####
    # Lid 1
    lid1 =  concept_uri(ns.lblod + 'persoon/', str(row['Naam_Lid4 First']) + str(row['Naam_Lid4 Last']))
    g.add((lid1, RDF.type, ns.person.Person))
    add_literal(g, lid1, ns.persoon.gebruikteVoornaam, str(row['Naam_Lid4 First']))
    add_literal(g, lid1, FOAF.familyName, str(row['Naam_Lid4 Last']))

    ## Lid 1 - Mandaat
    lid1_mandaat = concept_uri(ns.lblod + 'mandaat/', str(row['organization_id']) + str(row['Naam_Lid4 First']) + str(row['Naam_Lid4 Last']))
    g.add((lid1_mandaat, RDF.type, ns.mandaat.Mandaat))
    g.add((lid1_mandaat, ns.org.role, ns.bestursfunctie_code["Lid"]))
    g.add((lid1_mandaat, ns.org.postIn, bestuur_temporary))
    g.add((bestuur_temporary, ns.org.hasPost, lid1_mandaat))

    ## Lid 1 - Mandataris
    lid1_mandataris = concept_uri(ns.lblod + 'mandataris/', str(row['organization_id']) + str(row['Naam_Lid4 First']) + str(row['Naam_Lid4 Last']) + 'lid1')
    g.add((lid1_mandataris, RDF.type, ns.mandaat.Mandataris))
    g.add((lid1, ns.mandaat.isAangesteldAls, lid1_mandataris))
    g.add((lid1_mandataris, ns.org.holds, penningmeester_mandaat))
    g.add((lid1_mandataris, ns.mandaat.isBestuurlijkeAliasVan, lid1))
    add_literal(g, lid1_mandataris, ns.mandaat.start, str(row['Datum verkiezing lid 4']), XSD.dateTime)

    ###
    # Lid 2
    lid2 =  concept_uri(ns.lblod + 'persoon/', str(row['Naam_Lid5 First']) + str(row['Naam_Lid5 Last']))
    g.add((lid2, RDF.type, ns.person.Person))
    add_literal(g, lid2, ns.persoon.gebruikteVoornaam, str(row['Naam_Lid5 First']))
    add_literal(g, lid2, FOAF.familyName, str(row['Naam_Lid5 Last']))

    ## Lid 2 - Mandaat
    lid2_mandaat = concept_uri(ns.lblod + 'mandaat/', str(row['organization_id']) + str(row['Naam_Lid5 First']) + str(row['Naam_Lid5 Last']))
    g.add((lid2_mandaat, RDF.type, ns.mandaat.Mandaat))
    g.add((lid2_mandaat, ns.org.role, ns.bestursfunctie_code["Lid"]))
    g.add((lid2_mandaat, ns.org.postIn, bestuur_temporary))
    g.add((bestuur_temporary, ns.org.hasPost, lid2_mandaat))

    ## Lid 2 - Mandataris
    lid2_mandataris = concept_uri(ns.lblod + 'mandataris/', str(row['organization_id']) + str(row['Naam_Lid5 First']) + str(row['Naam_Lid5 Last']) + 'lid2')
    g.add((lid2_mandataris, RDF.type, ns.mandaat.Mandataris))
    g.add((lid2, ns.mandaat.isAangesteldAls, lid2_mandataris))
    g.add((lid2_mandataris, ns.org.holds, penningmeester_mandaat))
    g.add((lid2_mandataris, ns.mandaat.isBestuurlijkeAliasVan, lid2))
    add_literal(g, lid2_mandataris, ns.mandaat.start, str(row['Datum verkiezing lid 4']), XSD.dateTime)


  export_data(g)
  
  