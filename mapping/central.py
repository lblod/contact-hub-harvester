import pandas as pd
import numpy as np
from datetime import datetime
from rdflib import Graph, Literal, RDF
from rdflib.namespace import XSD, FOAF, SKOS, RDF

import cleansing.central as cls_central
from helper.functions import add_literal, concept_uri, exists_address, exists_bestuursperiode, exists_role, export_df, export_data
import helper.namespaces as ns

def main(file):
  central_raw = pd.read_excel(file)
  central_cleansed = cls_central.main(central_raw)

  export_df(central_cleansed, 'central')

  g = Graph()

  for _, row in central_cleansed.iterrows():    
    abb_id, _ = concept_uri(ns.lblod + 'organisatie/', str(row['Titel']))
    g.add((abb_id, RDF.type, ns.org.Organization))

    add_literal(g, abb_id, SKOS.prefLabel, str(row['Naam_CKB']))
    add_literal(g, abb_id, ns.regorg.legalName, str(row['Naam_CKB']))

    status, _ = concept_uri(ns.os, row['Status_CKB_cleansed'])
    g.add((abb_id, ns.regorg.orgStatus, status))

    g.add((abb_id, ns.org.classification, ns.bestuurseenheid_classification_code["centraal"]))

    if str(row['KBO_CKB_cleansed']) != str(np.nan):
      kbo_uri, _  = concept_uri(ns.lblod + 'gestructureerdeIdentificator/', str(row['KBO_CKB_cleansed']))
      g.add((kbo_uri, RDF.type, ns.generiek.GestructureerdeIdentificator))
      add_literal(g, kbo_uri, ns.generiek.lokaleIdentificator, str(row['KBO_CKB_cleansed']), XSD.string)
      g.add((abb_id, ns.generiek.gestructureerdeIdentificator, kbo_uri))

    if str(row['Titel']) != str(np.nan):
      naam_uri, _ = concept_uri(ns.lblod + 'gestructureerdeIdentificator/', str(row['Titel']))
      g.add((naam_uri, RDF.type, ns.generiek.GestructureerdeIdentificator))
      add_literal(g, naam_uri, ns.generiek.lokaleIdentificator, str(row['Titel']), XSD.string)
      g.add((abb_id, ns.generiek.gestructureerdeIdentificator, naam_uri))

    # Vestiging
    if exists_address(row):
      vestiging_uri, _ = concept_uri(ns.lblod + 'vestiging/', row['Titel'])
      g.add((vestiging_uri, RDF.type, ns.org.Site))
      
      address_uri, _ = concept_uri(ns.lblod + 'adres/', row['Titel'])
      g.add((address_uri, RDF.type, ns.locn.Address))
      g.add((vestiging_uri, ns.organisatie.bestaatUit, address_uri))
      add_literal(g, address_uri, ns.locn.thoroughfare, str(row['Straat']))
      add_literal(g, address_uri, ns.adres['Adresvoorstelling.huisnummer'], str(row['Huisnr Cleansed']), XSD.string)
      add_literal(g, address_uri, ns.adres['Adresvoorstelling.busnummer'], str(row['Busnummer Cleansed']), XSD.string)
      add_literal(g, address_uri, ns.locn.postCode, str(row['Postcode Cleansed']), XSD.string)
      add_literal(g, address_uri, ns.adres.gemeentenaam, str(row['Gemeente Cleansed']))
      add_literal(g, address_uri, ns.locn.adminUnitL2, str(row['Provincie Cleansed']))
      g.add((address_uri, ns.adres.land, Literal('België', lang='nl')))

      g.add((abb_id, ns.org.hasPrimarySite, vestiging_uri))

    roles = ['voorzitter', 'secretaris']

    if exists_bestuursperiode(row, roles):
      #Bestuur
      #bestuur = concept_uri(ns.lblod + 'bestuursorgaan/', row['organization_id'])
      #g.add((bestuur, RDF.type, ns.besluit.Bestuursorgaan))
      #g.add((bestuur, ns.besluit.bestuurt, abb_id))
      for role in roles:
        if exists_role(row, role):
          bestuur_temporary, _ = concept_uri(ns.lblod + 'bestuursorgaan/', str(row['Titel']) + str(datetime.now().year))
          g.add((bestuur_temporary, RDF.type, ns.besluit.Bestuursorgaan))
          g.add((bestuur_temporary, ns.generiek.isTijdspecialisatieVan, abb_id))

          # Person Role
          person_role, _ = concept_uri(ns.lblod + 'persoon/', str(row[f'Naam_{role} First']) + str(row[f'Naam_{role} Last']))
          g.add((person_role, RDF.type, ns.person.Person))
          add_literal(g, person_role, FOAF.givenName, str(row[f'Naam_{role} First']))
          add_literal(g, person_role, FOAF.familyName, str(row[f'Naam_{role} Last']))

          ## Vestiging
          person_role_vestiging_uri, _ = concept_uri(ns.lblod + 'vestiging/', str(row['Titel']) + str(row[f'Naam_{role} First']) + str(row[f'Naam_{role} Last']))
          g.add((person_role_vestiging_uri, RDF.type, ns.org.Site))
          g.add((person_role, ns.org.basedAt, person_role_vestiging_uri))

          person_role_contact_uri, _ = concept_uri(ns.lblod + 'contactpunt/', str(row['Titel']) + str(row[f'Naam_{role} First']) + str(row[f'Naam_{role} Last']) + str(row[f'Tel_{role} 1']))
          g.add((person_role_contact_uri, RDF.type, ns.schema.ContactPoint))
          g.add((person_role_vestiging_uri, ns.schema.siteAdress, person_role_contact_uri))
          add_literal(g, person_role_contact_uri, ns.schema.telephone, str(row[f'Tel_{role} 1']), XSD.string)
          add_literal(g, person_role_contact_uri, ns.schema.email, str(row[f'Mail_{role} Cleansed']), XSD.string)
        

          if str(row[f'Tel_{role} 2']) != str(np.nan):
            person_role_contact_2_uri, _ = concept_uri(ns.lblod + 'contactpunt/', str(row['Titel']) + str(row['Naam_{role} First']) + str(row[f'Naam_{role} Last']) + str(row[f'Tel_{role} 2']))
            g.add((person_role_contact_2_uri, RDF.type, ns.schema.ContactPoint))
            add_literal(g, person_role_contact_2_uri, ns.schema.telephone, str(row[f'Tel_{role} 2']), XSD.string)
            g.add((person_role_vestiging_uri, ns.schema.siteAdress, person_role_contact_uri))

          ## Mandaat
          person_role_mandaat, _ = concept_uri(ns.lblod + 'mandaat/', str(row['Titel']) + str(row[f'Naam_{role} First']) + str(row[f'Naam_{role} Last']))
          g.add((person_role_mandaat, RDF.type, ns.mandaat.Mandaat))
          g.add((person_role_mandaat, ns.org.role, ns.bestursfunctie_code[role]))
          g.add((person_role_mandaat, ns.org.postIn, bestuur_temporary))

          ## Mandataris
          person_role_mandataris, _ = concept_uri(ns.lblod + 'mandataris/', str(row['Titel'] + str(row[f'Naam_{role} First']) + str(row[f'Naam_{role} Last']) + role))
          g.add((person_role_mandataris, RDF.type, ns.mandaat.Mandataris))
          g.add((person_role_mandataris, ns.mandaat.isBestuurlijkeAliasVan, person_role))
          g.add((person_role_mandataris, ns.org.holds, person_role_mandaat))
          #start
          #einde
          #status ~ cf loket lokale besturen PoC https://poc-form-builder.relance.s.redpencil.io/codelijsten
          
          g.add((person_role, ns.mandaat.isAangesteldAls, person_role_mandataris))
          g.add((bestuur_temporary, ns.org.hasPost, person_role_mandaat))

    ####
    #Secretaris
    # secretaris, _ =  concept_uri(ns.lblod + 'persoon/', str(row['Naam_secretaris_CKB_first']) + str(row['Naam_secretaris_CKB_last']))
    # g.add((secretaris, RDF.type, ns.person.Person))
    # add_literal(g, secretaris, ns.persoon.gebruikteVoornaam, str(row['Naam_secretaris_CKB_first']))
    # add_literal(g, secretaris, FOAF.familyName, str(row['Naam_secretaris_CKB_last']))
    # ## Tel secretaris
    # secretaris_vestiging_uri, _ = concept_uri(ns.lblod + 'vestiging/', str(row['Titel']) + str(row['Naam_secretaris_CKB_first']) + str(row['Naam_secretaris_CKB_last']))
    # g.add((secretaris_vestiging_uri, RDF.type, ns.org.Site))
    # g.add((secretaris, ns.org.basedAt, secretaris_vestiging_uri))

    # secretaris_contact_uri, _ = concept_uri(ns.lblod + 'contactinfo/', str(row['Titel']) + str(row['Naam_secretaris_CKB_first']) + str(row['Naam_secretaris_CKB_last']))
    # g.add((secretaris_contact_uri, RDF.type, ns.schema.ContactPoint))
    # g.add((secretaris_vestiging_uri, ns.schema.siteAdress, secretaris_contact_uri))
    # add_literal(g, secretaris_contact_uri, ns.schema.telephone, str(row['Tel_CKB_secretaris_1']), XSD.string)
    # add_literal(g, secretaris_contact_uri, ns.schema.mail, str(row['Mail_secretaris_CKB_Cleansed']), XSD.string)
    # add_literal(g, secretaris_contact_uri, ns.schema.telephone, str(row['Tel_CKB_secretaris_2']), XSD.string)

    # #Mandataris
    # secretaris_mandataris, _ = concept_uri(ns.lblod + 'mandataris/', str(row['Naam_secretaris_CKB_first']) + str(row['Naam_secretaris_CKB_last']) + str(row['Titel'] + 'secretaris'))
    # g.add((secretaris_mandataris, RDF.type, ns.mandaat.Mandataris))
    # g.add((secretaris, ns.mandaat.isAangesteldAls, secretaris_mandataris))
    # g.add((secretaris_mandataris, ns.mandaat.isBestuurlijkeAliasVan, secretaris))
    # #start
    # #einde
    # #status
    # secretaris_mandaat, _ = concept_uri(ns.lblod + 'mandaat/', str(row['Naam_secretaris_CKB_first']) + str(row['Naam_secretaris_CKB_last']) + str(row['Titel']))
    # g.add((secretaris_mandaat, RDF.type, ns.mandaat.Mandaat))
    # g.add((secretaris_mandataris, ns.org.holds, secretaris_mandaat))
    # g.add((secretaris_mandaat, ns.org.role, ns.bestursfunctie_code['Secretaris']))

    # g.add((bestuur_temporary, ns.org.hasPost, secretaris_mandaat))
    # g.add((secretaris_mandaat, ns.org.postIn, bestuur_temporary))

  export_data(g, 'central-dev')


