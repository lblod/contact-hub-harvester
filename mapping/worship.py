import pandas as pd
import numpy as np
from datetime import datetime
from rdflib import Graph, Literal, RDF
from rdflib.namespace import FOAF , XSD, DC, FOAF, SKOS, RDF, RDFS

import cleansing.worship as cls_worship
from helper.functions import add_literal, concept_uri, export_data, export_df, exists_address_worship, exists_site_role_worship, exists_address_role_worship, exists_contact_role_worship, exists_role_worship
import helper.namespaces as ns

def create_status_uri(g, data):
  for status in data['Status_EB'].dropna().unique():
    subject, _ = concept_uri(ns.os, status)
    g.add((subject, RDF.type, SKOS.Concept))
    g.add((subject, SKOS.prefLabel, Literal(status, lang='nl')))
    if status.startswith('Operationeel'):
      g.add((subject, SKOS.broader, ns.os.actief))
    else:
      g.add((subject, SKOS.broader, ns.os.nietactief))

def main(file): 
  worship_raw = pd.read_excel(file)
  worship_cleansed = cls_worship.main(worship_raw)

  export_df(worship_cleansed, 'worship')

  g = Graph()

  create_status_uri(g, worship_cleansed)
  
  for _, row in worship_cleansed.iterrows():
    abb_id, _ = concept_uri(ns.lblod + 'organisatie/', str(row['organization_id']))
    g.add((abb_id, RDF.type, ns.org.Organization))

    status, _ = concept_uri(ns.os, str(row['Status_EB']))
    g.add((abb_id, ns.regorg.orgStatus, status))

    g.add((abb_id, ns.org.classification, ns.bestuurseenheid_classification_code['eredienst']))

    add_literal(g, abb_id, SKOS.prefLabel, str(row['Naam_EB']))
    add_literal(g, abb_id, ns.regorg.legalName, str(row['Naam_EB']))

    if exists_address_worship(row):
      site_id, _ = concept_uri(ns.lblod + 'vestiging/', str(row['organization_id']))
      g.add((site_id, RDF.type, ns.org.Site))

      address_id, _ = concept_uri(ns.lblod + 'adres/', str(row['organization_id']))
      g.add((address_id, RDF.type, ns.locn.Address))
      
      add_literal(g, address_id, ns.locn.thoroughfare, str(row['Straat_EB']))
      add_literal(g, address_id, ns.adres['Adresvoorstelling.huisnummer'], str(row['Huisnr_EB Cleansed']), XSD.string)
      add_literal(g, address_id, ns.adres['Adresvoorstelling.busnummer'], str(row['Busnummer_EB Cleansed']), XSD.string)
      add_literal(g, address_id, ns.locn.postCode, str(row['Postcode_EB Cleansed']), XSD.string)
      add_literal(g, address_id, ns.adres.gemeentenaam, str(row['Gemeente_EB Cleansed']), XSD.string)
      add_literal(g, address_id, ns.locn.adminUnitL2, str(row['Provincie Cleansed']))
      g.add((address_id, ns.adres.land, Literal('België', lang='nl')))

      g.add((site_id, ns.organisatie.bestaatUit, address_id))
      g.add((abb_id, ns.org.hasPrimarySite, site_id))
   
    if str(row['KBO_EB Cleansed']) != str(np.nan):
      kbo_id, _ = concept_uri(ns.lblod + 'gestructureerdeIdentificator/', str(row['KBO_EB Cleansed']))
      g.add((kbo_id, RDF.type, ns.generiek.GestructureerdeIdentificator))
      add_literal(g, kbo_id, ns.generiek.lokaleIdentificator, str(row['KBO_EB Cleansed']), XSD.string)
      g.add((abb_id, ns.generiek.gestructureerdeIdentificator, kbo_id))

    # Bestuurorgaan
    #bestuur = concept_uri(ns.lblod + 'bestuursorgaan/', str(row['organization_id']))
    #g.add((bestuur, RDF.type, ns.besluit.Bestuursorgaan))
    #g.add((bestuur, ns.besluit.bestuurt, abb_id))

    # Bestuursorgaan (in bestuursperiode)
    bestuur_temporary, _ = concept_uri(ns.lblod + 'bestuursorgaan/', str(row['organization_id']) + str(datetime.now().year))
    g.add((bestuur_temporary, RDF.type, ns.besluit.Bestuursorgaan))
    g.add((bestuur_temporary, ns.generiek.isTijdspecialisatieVan, abb_id))

    roles = ['voorzitter', 'secretaris', 'penningmeester']

    # Roles / Mandaat / Mandataris
    for role in roles:
      if exists_role_worship(row, role):
        person_role, _ = concept_uri(ns.lblod + 'persoon/', str(row[f'Naam_{role}_EB First']) + str(row[f'Naam_{role}_EB Last']))
        g.add((person_role, RDF.type, ns.person.Person))
        add_literal(g, person_role, FOAF.givenName, str(row[f'Naam_{role}_EB First']))
        add_literal(g, person_role, FOAF.familyName, str(row[f'Naam_{role}_EB Last']))

        ## Role - Vesting
        if exists_site_role_worship(row, role):
          person_role_vesting_uri, _ = concept_uri(ns.lblod + 'vestiging/', str(row['organization_id']) + str(row[f'Naam_{role}_EB First']) + str(row[f'Naam_{role}_EB Last']))
          g.add((person_role_vesting_uri, RDF.type, ns.org.Site))
          g.add((person_role, ns.org.basedAt, person_role_vesting_uri))

          ### Role - Contact punt
          if exists_contact_role_worship(row, role):
            person_role_contact_uri, _ = concept_uri(ns.lblod + 'contactpunt/', str(row['organization_id']) + str(row[f'Naam_{role}_EB First']) + str(row[f'Naam_{role}_EB Last']) + str(row[f'Tel_{role}_EB 1']))
            g.add((person_role_contact_uri, RDF.type, ns.schema.ContactPoint))
            g.add((person_role_vesting_uri, ns.org.siteAddress, person_role_contact_uri))

            add_literal(g, person_role_contact_uri, ns.schema.telephone, str(row[f'Tel_{role}_EB 1']), XSD.string)
            add_literal(g, person_role_contact_uri, ns.schema.email, str(row[f'Mail_{role}_EB Cleansed']), XSD.string)  

            if str(row[f'Tel_{role}_EB 2']) != str(np.nan):
              person_role_contact_2_uri, _ = concept_uri(ns.lblod + 'contactpunt/', str(row['organization_id']) + str(row[f'Naam_{role}_EB First']) + str(row[f'Naam_{role}_EB Last']) + str(row[f'Tel_{role}_EB 2']))
              g.add((person_role_contact_2_uri, RDF.type, ns.schema.ContactPoint))
              g.add((person_role_vesting_uri, ns.org.siteAddress, person_role_contact_2_uri))

              add_literal(g, person_role_contact_2_uri, ns.schema.telephone, str(row[f'Tel_{role}_EB 2']), XSD.string)

          ### Role - Adres
          if exists_address_role_worship(row, role):
            person_role_address_id, _ = concept_uri(ns.lblod + 'adres/', str(row['organization_id']) + str(row[f'Naam_{role}_EB First']) + str(row[f'Naam_{role}_EB Last'])) 
            g.add((person_role_address_id, RDF.type, ns.locn.Address))
            g.add((person_role_vesting_uri, ns.organisatie.bestaatUit, person_role_address_id))
            add_literal(g, person_role_address_id, ns.locn.fullAddress, str(row[f'Adres_{role}_EB Cleansed']))
        
        ## Role - Mandaat
        person_role_mandaat, _ = concept_uri(ns.lblod + 'mandaat/', str(row['organization_id']) + str(row[f'Naam_{role}_EB First']) + str(row[f'Naam_{role}_EB Last']))
        g.add((person_role_mandaat, RDF.type, ns.mandaat.Mandaat))
        g.add((person_role_mandaat, ns.org.role, ns.bestursfunctie_code[role]))
        g.add((person_role_mandaat, ns.org.postIn, bestuur_temporary))
        g.add((bestuur_temporary, ns.org.hasPost, person_role_mandaat))  

        ## Role - Mandataris
        person_role_mandataris, _ = concept_uri(ns.lblod + 'mandataris/', str(row['organization_id']) + str(row[f'Naam_{role}_EB First']) + str(row[f'Naam_{role}_EB Last']) + role)
        g.add((person_role_mandataris, RDF.type, ns.mandaat.Mandataris))
        g.add((person_role_mandataris, ns.mandaat.isBestuurlijkeAliasVan, person_role_vesting_uri))
        g.add((person_role_mandataris, ns.org.holds, person_role_mandaat))
        add_literal(g, person_role_mandataris, ns.mandaat.start, str(row[f'Datum verkiezing {role}']), XSD.dateTime)
        #einde
        #status ~ cf loket lokale besturen PoC https://poc-form-builder.relance.s.redpencil.io/codelijsten
        g.add((person_role, ns.mandaat.isAangesteldAls, person_role_mandataris))
        g.add((person_role_mandaat, ns.org.heldBy, person_role_mandataris))

    roles_lid = ['Lid4', 'Lid5']
    ####
    # Lids
    for role in roles_lid:
      if exists_role_worship(row, role):
        lid, _ =  concept_uri(ns.lblod + 'persoon/', str(row[f'Naam_{role} First']) + str(row[f'Naam_{role} Last']))
        g.add((lid, RDF.type, ns.person.Person))
        add_literal(g, lid, FOAF.givenName, str(row[f'Naam_{role} First']))
        add_literal(g, lid, FOAF.familyName, str(row[f'Naam_{role} Last']))

        ## Lid 1 - Mandaat
        lid_mandaat, _ = concept_uri(ns.lblod + 'mandaat/', str(row['organization_id']) + str(row[f'Naam_{role} First']) + str(row[f'Naam_{role} Last']))
        g.add((lid_mandaat, RDF.type, ns.mandaat.Mandaat))
        g.add((lid_mandaat, ns.org.role, ns.bestursfunctie_code[role]))
        g.add((lid_mandaat, ns.org.postIn, bestuur_temporary))
        g.add((bestuur_temporary, ns.org.hasPost, lid_mandaat))

        ## Lid 1 - Mandataris
        lid_mandataris, _ = concept_uri(ns.lblod + 'mandataris/', str(row['organization_id']) + str(row[f'Naam_{role} First']) + str(row[f'Naam_{role} Last']) + role)
        g.add((lid_mandataris, RDF.type, ns.mandaat.Mandataris))
        g.add((lid_mandataris, ns.org.holds, lid_mandaat))
        g.add((lid_mandataris, ns.mandaat.isBestuurlijkeAliasVan, lid))
        add_literal(g, lid_mandataris, ns.mandaat.start, str(row[f'Datum verkiezing {role}']), XSD.dateTime)

        g.add((lid, ns.mandaat.isAangesteldAls, lid_mandataris))
        g.add((lid_mandaat, ns.org.heldBy, lid_mandataris))

  export_data(g, 'worship-dev')

    ####    
    # Secretaris

    # secretaris, _ =  concept_uri(ns.lblod + 'persoon/', str(row['Naam_secretaris_EB First']) + str(row['Naam_secretaris_EB Last']))
    # g.add((secretaris, RDF.type, ns.person.Person))
    # add_literal(g, secretaris, ns.persoon.gebruikteVoornaam, str(row['Naam_secretaris_EB First']))
    # add_literal(g, secretaris, FOAF.familyName, str(row['Naam_secretaris_EB Last']))
    
    # ## Secretaris - Vesting
    # secretaris_vestiging_uri, _ = concept_uri(ns.lblod + 'vestiging/', str(row['organization_id']) + str(row['Naam_secretaris_EB First']) + str(row['Naam_secretaris_EB Last']))
    # g.add((secretaris_vestiging_uri, RDF.type, ns.org.Site))
    # g.add((secretaris, ns.org.basedAt, secretaris_vestiging_uri))

    # ### Secretaris - Contact punt
    # secretaris_contact_uri, _ = concept_uri(ns.lblod + 'contactpunt/', str(row['organization_id']) + str(row['Naam_secretaris_EB First']) + str(row['Naam_secretaris_EB Last']) + str(row['Tel_secretaris_EB 1']))
    # g.add((secretaris_contact_uri, RDF.type, ns.schema.ContactPoint))
    # g.add((secretaris_vestiging_uri, ns.org.siteAddress, secretaris_contact_uri))
    # add_literal(g, secretaris_contact_uri, ns.schema.telephone, str(row['Tel_secretaris_EB 1']))
    # add_literal(g, secretaris_contact_uri, ns.schema.email, str(row['Mail_secretaris_EB Cleansed']))

    # if str(row['Tel_secretaris_EB 2']) != str(np.nan):
    #   secretaris_contact_2_uri, _ = concept_uri(ns.lblod + 'contactinfo/', str(row['organization_id']) + str(row['Naam_secretaris_EB First']) + str(row['Naam_secretaris_EB Last']) + str(row['Tel_secretaris_EB 2']))
    #   g.add((secretaris_contact_2_uri, RDF.type, ns.schema.ContactPoint))
    #   g.add((secretaris_vestiging_uri, ns.org.siteAddress, secretaris_contact_2_uri))
    #   add_literal(g, secretaris_contact_2_uri, ns.schema.telephone, str(row['Tel_secretaris_EB 2']))

    # ### Secretaris - Adres
    # secretaris_address_id, _ = concept_uri(ns.lblod + 'adresvoorstelling/', str(row['organization_id']) + str(row['Naam_secretaris_EB First']) + str(row['Naam_secretaris_EB Last'])) 
    # g.add((secretaris_address_id, RDF.type, ns.locn.Address))
    # g.add((secretaris_vestiging_uri, ns.organisatie.bestaatUit, secretaris_address_id))
    # add_literal(g, secretaris_address_id, ns.locn.fullAddress, str(row['Adres_secretaris_EB Cleansed']))

    # ## Secretaris - Mandaat
    # secretaris_mandaat, _ = concept_uri(ns.lblod + 'mandaat/', str(row['organization_id']) + str(row['Naam_secretaris_EB First']) + str(row['Naam_secretaris_EB Last']))
    # g.add((secretaris_mandaat, RDF.type, ns.mandaat.Mandaat))
    # g.add((secretaris_mandaat, ns.org.role, ns.bestursfunctie_code["Secretaris"]))
    # g.add((secretaris_mandaat, ns.org.postIn, bestuur_temporary))
    # g.add((bestuur_temporary, ns.org.hasPost, secretaris_mandaat))
   
    # ## Secreataris - Mandataris
    # secretaris_mandataris, _ = concept_uri(ns.lblod + 'mandataris/', str(row['organization_id']) + str(row['Naam_secretaris_EB First']) + str(row['Naam_secretaris_EB Last']) + 'secretaris')
    # g.add((secretaris_mandataris, RDF.type, ns.mandaat.Mandataris))
    # g.add((secretaris_mandataris, ns.mandaat.isBestuurlijkeAliasVan, secretaris))
    # g.add((secretaris_mandataris, ns.org.holds, secretaris_mandaat))
    # add_literal(g, secretaris_mandataris, ns.mandaat.start, str(row['Datum verkiezing secretaris']), XSD.dateTime)
    # #einde
    # #status
    # g.add((secretaris, ns.mandaat.isAangesteldAls, secretaris_mandataris))
    # g.add((secretaris_mandaat, ns.org.heldBy, secretaris_mandataris))

    # ####
    # # Penningmeester
    # penningmeester, _=  concept_uri(ns.lblod + 'persoon/', str(row['Naam_penningmeester_EB First']) + str(row['Naam_penningmeester_EB Last']))
    # g.add((penningmeester, RDF.type, ns.person.Person))
    # add_literal(g, penningmeester, ns.persoon.gebruikteVoornaam, str(row['Naam_penningmeester_EB First']))
    # add_literal(g, penningmeester, FOAF.familyName, str(row['Naam_penningmeester_EB Last']))
    
    # ## Penningmeester - Vesting
    # penningmeester_vestiging_uri, _ = concept_uri(ns.lblod + 'vestiging/', str(row['organization_id']) + str(row['Naam_penningmeester_EB First']) + str(row['Naam_penningmeester_EB Last']))
    # g.add((penningmeester_vestiging_uri, RDF.type, ns.org.Site))
    # g.add((penningmeester, ns.org.basedAt, penningmeester_vestiging_uri))

    # ### Penningmeester - Contact punt
    # penningmeester_contact_uri, _ = concept_uri(ns.lblod + 'contactinfo/', str(row['organization_id']) + str(row['Naam_penningmeester_EB First']) + str(row['Naam_penningmeester_EB Last']) + str(row['Tel_penningmeester_EB 1']))
    # g.add((penningmeester_contact_uri, RDF.type, ns.schema.ContactPoint))
    # g.add((penningmeester_vestiging_uri, ns.org.siteAddress, penningmeester_contact_uri))
    # add_literal(g, penningmeester_contact_uri, ns.schema.telephone, str(row['Tel_penningmeester_EB 1']))
    # add_literal(g, penningmeester_contact_uri, ns.schema.email, str(row['Mail_penningmeester_EB Cleansed']))

    # if str(row['Tel_penningmeester_EB 2']) != str(np.nan):
    #   penningmeester_contact_2_uri, _ = concept_uri(ns.lblod + 'contactinfo/', str(row['organization_id']) + str(row['Naam_penningmeester_EB First']) + str(row['Naam_penningmeester_EB Last']) + str(row['Tel_penningmeester_EB 2']))
    #   g.add((penningmeester_contact_2_uri, RDF.type, ns.schema.ContactPoint))
    #   g.add((penningmeester_vestiging_uri, ns.org.siteAddress, penningmeester_contact_2_uri))
    #   add_literal(g, penningmeester_contact_2_uri, ns.schema.telephone, str(row['Tel_penningmeester_EB 2']))

    # ### Penningmeester - Adres
    # penningmeester_address_id, _ = concept_uri(ns.lblod + 'adresvoorstelling/', str(row['organization_id']) + str(row['Naam_penningmeester_EB First']) + str(row['Naam_penningmeester_EB Last'])) 
    # g.add((penningmeester_address_id, RDF.type, ns.locn.Address))
    # g.add((penningmeester_vestiging_uri, ns.organisatie.bestaatUit, penningmeester_address_id))
    # add_literal(g, penningmeester_address_id, ns.locn.fullAddress, str(row['Adres_penningmeester_EB Cleansed']))

    # ## Penningmeester - Mandaat
    # penningmeester_mandaat, _ = concept_uri(ns.lblod + 'mandaat/', str(row['organization_id']) + str(row['Naam_penningmeester_EB First']) + str(row['Naam_penningmeester_EB Last']))
    # g.add((penningmeester_mandaat, RDF.type, ns.mandaat.Mandaat))
    # g.add((penningmeester_mandaat, ns.org.role, ns.bestursfunctie_code["Penningmeester"]))
    # g.add((penningmeester_mandaat, ns.org.postIn, bestuur_temporary))
    # g.add((bestuur_temporary, ns.org.hasPost, penningmeester_mandaat))

    # ## Penningmeester - Mandataris
    # penningmeester_mandataris, _ = concept_uri(ns.lblod + 'mandataris/', str(row['organization_id']) + str(row['Naam_penningmeester_EB First']) + str(row['Naam_penningmeester_EB Last']) + 'penningmeester')
    # g.add((penningmeester_mandataris, RDF.type, ns.mandaat.Mandataris))
    # g.add((penningmeester_mandataris, ns.org.holds, penningmeester_mandaat))
    # g.add((penningmeester_mandataris, ns.mandaat.isBestuurlijkeAliasVan, penningmeester))
    # add_literal(g, penningmeester_mandataris, ns.mandaat.start, str(row['Datum verkiezing penningmeester']), XSD.dateTime)
    # #einde
    # #status
    # g.add((penningmeester, ns.mandaat.isAangesteldAls, penningmeester_mandataris))
    # g.add((penningmeester_mandaat, ns.org.heldBy, penningmeester_mandataris))

#  # Lid 1
#     lid1, _ =  concept_uri(ns.lblod + 'persoon/', str(row['Naam_Lid4 First']) + str(row['Naam_Lid4 Last']))
#     g.add((lid1, RDF.type, ns.person.Person))
#     add_literal(g, lid1, ns.persoon.gebruikteVoornaam, str(row['Naam_Lid4 First']))
#     add_literal(g, lid1, FOAF.familyName, str(row['Naam_Lid4 Last']))

#     ## Lid 1 - Mandaat
#     lid1_mandaat, _ = concept_uri(ns.lblod + 'mandaat/', str(row['organization_id']) + str(row['Naam_Lid4 First']) + str(row['Naam_Lid4 Last']))
#     g.add((lid1_mandaat, RDF.type, ns.mandaat.Mandaat))
#     g.add((lid1_mandaat, ns.org.role, ns.bestursfunctie_code["Lid"]))
#     g.add((lid1_mandaat, ns.org.postIn, bestuur_temporary))
#     g.add((bestuur_temporary, ns.org.hasPost, lid1_mandaat))

#     ## Lid 1 - Mandataris
#     lid1_mandataris, _ = concept_uri(ns.lblod + 'mandataris/', str(row['organization_id']) + str(row['Naam_Lid4 First']) + str(row['Naam_Lid4 Last']) + 'lid1')
#     g.add((lid1_mandataris, RDF.type, ns.mandaat.Mandataris))
#     g.add((lid1_mandataris, ns.org.holds, lid1_mandaat))
#     g.add((lid1_mandataris, ns.mandaat.isBestuurlijkeAliasVan, lid1))
#     add_literal(g, lid1_mandataris, ns.mandaat.start, str(row['Datum verkiezing lid 4']), XSD.dateTime)

#     g.add((lid1, ns.mandaat.isAangesteldAls, lid1_mandataris))
#     g.add((lid1_mandaat, ns.org.heldBy, lid1_mandataris))

#     ###
#     # Lid 2
#     lid2, _ =  concept_uri(ns.lblod + 'persoon/', str(row['Naam_Lid5 First']) + str(row['Naam_Lid5 Last']))
#     g.add((lid2, RDF.type, ns.person.Person))
#     add_literal(g, lid2, ns.persoon.gebruikteVoornaam, str(row['Naam_Lid5 First']))
#     add_literal(g, lid2, FOAF.familyName, str(row['Naam_Lid5 Last']))

#     ## Lid 2 - Mandaat
#     lid2_mandaat, _ = concept_uri(ns.lblod + 'mandaat/', str(row['organization_id']) + str(row['Naam_Lid5 First']) + str(row['Naam_Lid5 Last']))
#     g.add((lid2_mandaat, RDF.type, ns.mandaat.Mandaat))
#     g.add((lid2_mandaat, ns.org.role, ns.bestursfunctie_code["Lid"]))
#     g.add((lid2_mandaat, ns.org.postIn, bestuur_temporary))
#     g.add((bestuur_temporary, ns.org.hasPost, lid2_mandaat))

#     ## Lid 2 - Mandataris
#     lid2_mandataris, _ = concept_uri(ns.lblod + 'mandataris/', str(row['organization_id']) + str(row['Naam_Lid5 First']) + str(row['Naam_Lid5 Last']) + 'lid2')
#     g.add((lid2_mandataris, RDF.type, ns.mandaat.Mandataris))
#     g.add((lid2_mandataris, ns.org.holds, lid2_mandaat))
#     g.add((lid2_mandataris, ns.mandaat.isBestuurlijkeAliasVan, lid2))
#     add_literal(g, lid2_mandataris, ns.mandaat.start, str(row['Datum verkiezing lid 4']), XSD.dateTime)

#     g.add((lid2, ns.mandaat.isAangesteldAls, lid2_mandataris))
#     g.add((lid2_mandaat, ns.org.heldBy, lid2_mandataris))
  
  
  