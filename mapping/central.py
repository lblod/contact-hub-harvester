import pandas as pd
import numpy as np
from datetime import datetime
from rdflib import Graph, Literal, RDF
from rdflib.namespace import XSD, FOAF, SKOS, RDF, RDFS

import cleansing.central as cls_central
from helper.functions import add_literal, concept_uri, exists_address, exists_bestuursperiode, exists_contact_role, exists_role, exists_site_role, load_graph, get_concept_id, get_label_role, export_df, export_data
import helper.namespaces as ns

def main(file):
  central_raw = pd.read_excel(file)
  central_cleansed = cls_central.main(central_raw)

  export_df(central_cleansed, 'central')

  g = Graph()
  codelist_ere = load_graph('codelist-ere')
  codelist_bestuurseenheid = load_graph('bestuurseenheid-classificatie-code')
  bestuurseenheid_classification_id = get_concept_id(codelist_bestuurseenheid, 'Centraal bestuur van de eredienst')

  for _, row in central_cleansed.iterrows():    
    abb_id, abb_uuid = concept_uri(ns.lblod + 'centraalBestuurVanDeEredienst/', str(row['Titel']))
    g.add((abb_id, RDF.type, ns.ere.CentraalBestuurVanDeEredienst))
    add_literal(g, abb_id, ns.mu.uuid, abb_uuid, XSD.string)

    add_literal(g, abb_id, SKOS.prefLabel, str(row['Naam_CKB']))
    #add_literal(g, abb_id, ns.regorg.legalName, str(row['Naam_CKB']))
    
    #g.add((abb_id, RDFS.subClassOf, ns.org.Organization))

    g.add((abb_id, ns.org.classification, bestuurseenheid_classification_id))

    status, _ = concept_uri(ns.c + 'OrganisatieStatusCode/', str(row['Status_CKB_cleansed']))
    g.add((abb_id, ns.regorg.orgStatus, status))

    bo_id, bo_uuid = concept_uri(ns.lblod + 'centraleBestuursorgaan/', str(row['Titel']))
    g.add((bo_id, RDF.type, ns.ere.CentraleBestuursorgaan))
    add_literal(g, bo_id, ns.mu.uuid, bo_uuid, XSD.string)

    bestuursorgaan_classification_id = get_concept_id(codelist_ere, str(row['Bestuursorgaan Type']))
    g.add((bo_id, ns.org.classification, bestuursorgaan_classification_id))

    g.add((bo_id, ns.besluit.bestuurt, abb_id))    

    if str(row['KBO_CKB_cleansed']) != str(np.nan):
      id_class, id_uuid = concept_uri(ns.lblod +'identifier/', str(row['KBO_CKB_cleansed']))
      g.add((id_class, RDF.type, ns.adms.Identifier))
      add_literal(g, id_class, SKOS.notation, 'KBO nummer', XSD.string)
      add_literal(g, id_class, ns.mu.uuid, id_uuid, XSD.string)

      kbo_uri, _  = concept_uri(ns.lblod + 'gestructureerdeIdentificator/', str(row['KBO_CKB_cleansed']))
      g.add((kbo_uri, RDF.type, ns.generiek.GestructureerdeIdentificator))
      add_literal(g, kbo_uri, ns.generiek.lokaleIdentificator, str(row['KBO_CKB_cleansed']), XSD.string)
      g.add((id_class, ns.generiek.gestructureerdeIdentificator, kbo_uri))

      g.add((abb_id, ns.adms.identifier, id_class))

    if str(row['Titel']) != str(np.nan):
      id_class, id_uuid = concept_uri(ns.lblod +'identificator/', str(row['Titel']))
      g.add((id_class, RDF.type, ns.adms.Identifier))
      add_literal(g, id_class, SKOS.notation, 'Titel', XSD.string)
      add_literal(g, id_class, ns.mu.uuid, id_uuid, XSD.string)

      naam_uri, _ = concept_uri(ns.lblod + 'gestructureerdeIdentificator/', str(row['Titel']))
      g.add((naam_uri, RDF.type, ns.generiek.GestructureerdeIdentificator))
      add_literal(g, naam_uri, ns.generiek.lokaleIdentificator, str(row['Titel']), XSD.string)
      g.add((id_class, ns.generiek.gestructureerdeIdentificator, naam_uri))

      g.add((abb_id, ns.adms.identifier, id_class))

    # Vestiging
    if exists_address(row):
      vestiging_uri, vestiging_uuid = concept_uri(ns.lblod + 'vestiging/', str(row['Titel']))
      g.add((vestiging_uri, RDF.type, ns.org.Site))
      add_literal(g, vestiging_uri, ns.mu.uuid, vestiging_uuid, XSD.string)

      address_uri, _ = concept_uri(ns.lblod + 'adres/', str(row['Titel']))
      g.add((address_uri, RDF.type, ns.locn.Address))
      
      add_literal(g, address_uri, ns.locn.thoroughfare, str(row['Straat']))
      add_literal(g, address_uri, ns.adres['Adresvoorstelling.huisnummer'], str(row['Huisnr Cleansed']), XSD.string)
      add_literal(g, address_uri, ns.adres['Adresvoorstelling.busnummer'], str(row['Busnummer Cleansed']), XSD.string)
      add_literal(g, address_uri, ns.locn.postCode, str(row['Postcode Cleansed']), XSD.string)
      add_literal(g, address_uri, ns.adres.gemeentenaam, str(row['Gemeente Cleansed']))
      add_literal(g, address_uri, ns.locn.adminUnitL2, str(row['Provincie Cleansed']))
      g.add((address_uri, ns.adres.land, Literal('België', lang='nl')))

      g.add((vestiging_uri, ns.organisatie.bestaatUit, address_uri))
      g.add((abb_id, ns.org.hasPrimarySite, vestiging_uri))

    roles = ['voorzitter', 'secretaris']

    if exists_bestuursperiode(row, roles):    
      # Bestuursorgaan (in bestuursperiode)
      bestuur_temporary, bestuur_temporary_uuid = concept_uri(ns.lblod + 'bestuursorgaan/', str(row['Titel']) + str(datetime.now().year))
      g.add((bestuur_temporary, RDF.type, ns.besluit.Bestuursorgaan))
      add_literal(g, bestuur_temporary, ns.mu.uuid, bestuur_temporary_uuid, XSD.string)
      g.add((bestuur_temporary, ns.generiek.isTijdspecialisatieVan, bo_id))
      #start
      #end

       # Mandaat / Mandataris
      for role in roles:
        if exists_role(row, role):
          # Person Role
          person_role, person_uuid = concept_uri(ns.lblod + 'persoon/', str(row[f'Naam_{role} First']) + str(row[f'Naam_{role} Last']))
          g.add((person_role, RDF.type, ns.person.Person))
          add_literal(g, person_role, ns.mu.uuid, person_uuid, XSD.string)
          add_literal(g, person_role, FOAF.givenName, str(row[f'Naam_{role} First']))
          add_literal(g, person_role, FOAF.familyName, str(row[f'Naam_{role} Last']))

          ## Role - Vestiging
          if exists_contact_role(row, role):
            person_role_vestiging_uri, person_role_vestiging_uuid = concept_uri(ns.lblod + 'vestiging/', str(row['Titel']) + str(row[f'Naam_{role} First']) + str(row[f'Naam_{role} Last']))
            g.add((person_role_vestiging_uri, RDF.type, ns.org.Site))
            add_literal(g, person_role_vestiging_uri, ns.mu.uuid, person_role_vestiging_uuid, XSD.string)
            g.add((person_role, ns.org.basedAt, person_role_vestiging_uri))

            #Contact
            person_role_contact_uri, person_role_contact_uuid = concept_uri(ns.lblod + 'contactpunt/', str(row['Titel']) + str(row[f'Naam_{role} First']) + str(row[f'Naam_{role} Last']) + str(row[f'Tel_{role} 1']))
            g.add((person_role_contact_uri, RDF.type, ns.schema.ContactPoint))
            add_literal(g, person_role_contact_uri, ns.mu.uuid, person_role_contact_uuid, XSD.string)
            g.add((person_role_vestiging_uri, ns.schema.siteAdress, person_role_contact_uri))

            add_literal(g, person_role_contact_uri, ns.schema.telephone, str(row[f'Tel_{role} 1']), XSD.string)
            add_literal(g, person_role_contact_uri, ns.schema.email, str(row[f'Mail_{role} Cleansed']), XSD.string)
          
            if str(row[f'Tel_{role} 2']) != str(np.nan):
              person_role_contact_2_uri, person_role_contact_2_uuid = concept_uri(ns.lblod + 'contactpunt/', str(row['Titel']) + str(row['Naam_{role} First']) + str(row[f'Naam_{role} Last']) + str(row[f'Tel_{role} 2']))
              g.add((person_role_contact_2_uri, RDF.type, ns.schema.ContactPoint))
              add_literal(g, person_role_contact_2_uri, ns.mu.uuid, person_role_contact_2_uuid, XSD.string)
              
              add_literal(g, person_role_contact_2_uri, ns.schema.telephone, str(row[f'Tel_{role} 2']), XSD.string)
              g.add((person_role_vestiging_uri, ns.schema.siteAdress, person_role_contact_2_uri))

          ## Mandaat
          person_role_mandaat, person_role_mandaat_uuid = concept_uri(ns.lblod + 'mandaat/', str(row['Titel']) + str(row[f'Naam_{role} First']) + str(row[f'Naam_{role} Last']))
          g.add((person_role_mandaat, RDF.type, ns.mandaat.Mandaat))
          add_literal(g, person_role_mandaat, ns.mu.uuid, person_role_mandaat_uuid, XSD.string)

          bestuurfunctie_id = get_concept_id(codelist_ere, get_label_role(role + ' central'))
          g.add((person_role_mandaat, ns.org.role, bestuurfunctie_id))
          g.add((person_role_mandaat, ns.org.postIn, bestuur_temporary))
          g.add((bestuur_temporary, ns.org.hasPost, person_role_mandaat))

          ## Mandataris
          person_role_mandataris, person_role_mandataris_uuid = concept_uri(ns.lblod + 'mandataris/', str(row['Titel'] + str(row[f'Naam_{role} First']) + str(row[f'Naam_{role} Last']) + role))
          g.add((person_role_mandataris, RDF.type, ns.mandaat.Mandataris))
          add_literal(g, person_role_mandataris, ns.mu.uuid, person_role_mandataris_uuid, XSD.string)
          
          g.add((person_role_mandataris, ns.mandaat.isBestuurlijkeAliasVan, person_role))
          g.add((person_role_mandataris, ns.org.holds, person_role_mandaat))
          #start
          #einde
          #status

          g.add((person_role_mandaat, ns.org.heldBy, person_role_mandataris))
          g.add((person_role, ns.mandaat.isAangesteldAls, person_role_mandataris))
          

  export_data(g, 'central-qa')


