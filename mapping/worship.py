import pandas as pd
import numpy as np
from datetime import datetime
from rdflib import Graph
from rdflib.namespace import FOAF, XSD, FOAF, SKOS, RDF

from helper.functions import add_literal, concept_uri, export_data, get_cleansed_data, exists_address, exists_site_role, exists_address_role, exists_contact_role, exists_role, exists_bestuursperiode, load_graph, get_concept_id, get_label_role
import helper.namespaces as ns


def main(file, mode): 
  worship_cleansed = get_cleansed_data(file, 'worship')

  g = Graph()
  codelist_ere = load_graph('codelist-ere')
  codelist_bestuurseenheid = load_graph('bestuurseenheid-classificatie-code')
  bestuurseenheid_classification_id = get_concept_id(codelist_bestuurseenheid, 'Bestuur van de eredienst')

  print("########### Mapping started #############")

  for _, row in worship_cleansed.iterrows():
    abb_id, abb_uuid = concept_uri(ns.lblod + 'bestuurVanDeEredienst/', str(row['organization_id']))
    g.add((abb_id, RDF.type, ns.ere.BestuurVanDeEredienst))
    add_literal(g, abb_id, ns.mu.uuid, abb_uuid, XSD.string)

    add_literal(g, abb_id, SKOS.prefLabel, str(row['Naam_EB']))
    #add_literal(g, abb_id, ns.rov.legalName, str(row['Naam_EB']))

    #g.add((abb_id, RDFS.subClassOf, ns.org.Organization))

    g.add((abb_id, ns.org.classification, bestuurseenheid_classification_id))

    status, _ = concept_uri(ns.c + 'OrganisatieStatusCode/', str(row['Status_EB Cleansed']))
    g.add((abb_id, ns.rov.orgStatus, status))

    bo_id, bo_uuid = concept_uri(ns.lblod + 'eredienstbestuursorgaan/', str(row['organization_id']))
    g.add((bo_id, RDF.type, ns.ere.Eredienstbestuursorgaan))
    add_literal(g, bo_id, ns.mu.uuid, bo_uuid, XSD.string)

    if str(row['Bestuursorgaan Type']) != str(np.nan):
      bestuursorgaan_classification_id = get_concept_id(codelist_ere, str(row['Bestuursorgaan Type']))
      g.add((bo_id, ns.org.classification, bestuursorgaan_classification_id))

    g.add((bo_id, ns.besluit.bestuurt, abb_id))    
    
    if str(row['KBO_EB Cleansed']) != str(np.nan):
      id_class, id_uuid = concept_uri(ns.lblod +'identificator/', str(row['KBO_EB Cleansed']))
      g.add((id_class, RDF.type, ns.adms.Identifier))
      add_literal(g, id_class, SKOS.notation, 'KBO nummer', XSD.string)
      add_literal(g, id_class, ns.mu.uuid, id_uuid, XSD.string)

      kbo_id, _ = concept_uri(ns.lblod + 'gestructureerdeIdentificator/', str(row['KBO_EB Cleansed']))
      g.add((kbo_id, RDF.type, ns.generiek.GestructureerdeIdentificator))
      add_literal(g, kbo_id, ns.generiek.lokaleIdentificator, str(row['KBO_EB Cleansed']), XSD.string)
      g.add((id_class, ns.generiek.gestructureerdeIdentificator, kbo_id))

      g.add((abb_id, ns.adms.identifier, id_class))

    if str(row['Titel Cleansed']) != str(np.nan):
      id_class, id_uuid = concept_uri(ns.lblod +'identificator/', str(row['Titel Cleansed']))
      g.add((id_class, RDF.type, ns.adms.Identifier))
      add_literal(g, id_class, SKOS.notation, 'SharePoint identificator', XSD.string)
      add_literal(g, id_class, ns.mu.uuid, id_uuid, XSD.string)

      naam_uri, _ = concept_uri(ns.lblod + 'gestructureerdeIdentificator/', str(row['Titel Cleansed']))
      g.add((naam_uri, RDF.type, ns.generiek.GestructureerdeIdentificator))
      add_literal(g, naam_uri, ns.generiek.lokaleIdentificator, str(row['Titel Cleansed']), XSD.string)
      g.add((id_class, ns.generiek.gestructureerdeIdentificator, naam_uri))

      g.add((abb_id, ns.adms.identifier, id_class))

    # Vestiging
    if exists_address(row):
      site_id, site_uuid = concept_uri(ns.lblod + 'vestiging/', str(row['organization_id']))
      g.add((site_id, RDF.type, ns.org.Site))
      add_literal(g, site_id, ns.mu.uuid, site_uuid, XSD.string)

      address_id, _ = concept_uri(ns.lblod + 'adres/', str(row['organization_id']))
      g.add((address_id, RDF.type, ns.locn.Address))
      
      add_literal(g, address_id, ns.locn.thoroughfare, str(row['Straat']))
      add_literal(g, address_id, ns.adres['Adresvoorstelling.huisnummer'], str(row['Huisnr Cleansed']), XSD.string)
      add_literal(g, address_id, ns.adres['Adresvoorstelling.busnummer'], str(row['Busnummer Cleansed']), XSD.string)
      add_literal(g, address_id, ns.locn.postCode, str(row['Postcode Cleansed']), XSD.string)
      add_literal(g, address_id, ns.adres.gemeentenaam, str(row['Gemeente Cleansed']), XSD.string)
      add_literal(g, address_id, ns.locn.adminUnitL2, str(row['Provincie Cleansed']))
      add_literal(g, address_id, ns.adres.land, 'België')

      g.add((site_id, ns.organisatie.bestaatUit, address_id))
      g.add((abb_id, ns.org.hasPrimarySite, site_id))
   
    roles = ['voorzitter', 'secretaris', 'penningmeester']
    roles_lid = ['Lid4', 'Lid5']

    if exists_bestuursperiode(row, roles+roles_lid):
      # Bestuursorgaan (in bestuursperiode)
      bestuur_temporary, bestuur_temporary_uuid = concept_uri(ns.lblod + 'bestuursorgaan/', str(row['organization_id']) + str(datetime.now().year))
      g.add((bestuur_temporary, RDF.type, ns.besluit.Bestuursorgaan))
      add_literal(g, bestuur_temporary, ns.mu.uuid, bestuur_temporary_uuid, XSD.string)
      g.add((bestuur_temporary, ns.generiek.isTijdspecialisatieVan, bo_id))
      #start
      #end

      # Mandaat / Mandataris
      for role in roles:
        if exists_role(row, role):
          # Person role
          person_role, person_uuid = concept_uri(ns.lblod + 'persoon/', str(row[f'Naam_{role} First']) + str(row[f'Naam_{role} Last']))
          g.add((person_role, RDF.type, ns.person.Person))
          add_literal(g, person_role, ns.mu.uuid, person_uuid, XSD.string)
          add_literal(g, person_role, FOAF.givenName, str(row[f'Naam_{role} First']))
          add_literal(g, person_role, FOAF.familyName, str(row[f'Naam_{role} Last']))

          ## Role - Vestiging
          if exists_site_role(row, role):
            person_role_vestiging_uri, person_role_vestiging_uuid = concept_uri(ns.lblod + 'vestiging/', str(row['organization_id']) + str(row[f'Naam_{role} First']) + str(row[f'Naam_{role} Last']))
            g.add((person_role_vestiging_uri, RDF.type, ns.org.Site))
            add_literal(g, person_role_vestiging_uri, ns.mu.uuid, person_role_vestiging_uuid, XSD.string)
            g.add((person_role, ns.org.basedAt, person_role_vestiging_uri))

            ### Role - Contact punt
            if exists_contact_role(row, role):
              person_role_contact_uri, person_role_contact_uuid = concept_uri(ns.lblod + 'contactpunt/', str(row['organization_id']) + str(row[f'Naam_{role} First']) + str(row[f'Naam_{role} Last']) + str(row[f'Tel_{role} 1']))
              g.add((person_role_contact_uri, RDF.type, ns.schema.ContactPoint))
              add_literal(g, person_role_contact_uri, ns.mu.uuid, person_role_contact_uuid, XSD.string)
              g.add((person_role_vestiging_uri, ns.org.siteAddress, person_role_contact_uri))

              add_literal(g, person_role_contact_uri, ns.schema.telephone, str(row[f'Tel_{role} 1']), XSD.string)
              add_literal(g, person_role_contact_uri, ns.schema.email, str(row[f'Mail_{role} Cleansed']), XSD.string)  

              if str(row[f'Tel_{role} 2']) != str(np.nan):
                person_role_contact_2_uri, person_role_contact_2_uuid = concept_uri(ns.lblod + 'contactpunt/', str(row['organization_id']) + str(row[f'Naam_{role} First']) + str(row[f'Naam_{role} Last']) + str(row[f'Tel_{role} 2']))
                g.add((person_role_contact_2_uri, RDF.type, ns.schema.ContactPoint))
                add_literal(g, person_role_contact_2_uri, ns.mu.uuid, person_role_contact_2_uuid, XSD.string)

                add_literal(g, person_role_contact_2_uri, ns.schema.telephone, str(row[f'Tel_{role} 2']), XSD.string)
                g.add((person_role_vestiging_uri, ns.org.siteAddress, person_role_contact_2_uri))

            ### Role - Adres
            if exists_address_role(row, role):
              person_role_address_id, person_role_address_uuid = concept_uri(ns.lblod + 'adres/', str(row['organization_id']) + str(row[f'Naam_{role} First']) + str(row[f'Naam_{role} Last'])) 
              g.add((person_role_address_id, RDF.type, ns.locn.Address))
              add_literal(g, person_role_address_id, ns.mu.uuid, person_role_address_uuid, XSD.string)

              g.add((person_role_vestiging_uri, ns.organisatie.bestaatUit, person_role_address_id))
              add_literal(g, person_role_address_id, ns.locn.fullAddress, str(row[f'Adres_{role} Cleansed']))
          
          ## Role - Mandaat
          person_role_mandaat, person_role_mandaat_uuid = concept_uri(ns.lblod + 'mandaat/', str(row['organization_id']) + str(row[f'Naam_{role} First']) + str(row[f'Naam_{role} Last']))
          g.add((person_role_mandaat, RDF.type, ns.mandaat.Mandaat))
          add_literal(g, person_role_mandaat, ns.mu.uuid, person_role_mandaat_uuid, XSD.string)

          bestuurfunctie_id = get_concept_id(codelist_ere, get_label_role(role + ' worship'))
          g.add((person_role_mandaat, ns.org.role, bestuurfunctie_id))
          g.add((person_role_mandaat, ns.org.postIn, bestuur_temporary))
          g.add((bestuur_temporary, ns.org.hasPost, person_role_mandaat))  

          ## Role - Mandataris
          person_role_mandataris, person_role_mandataris_uuid = concept_uri(ns.lblod + 'mandataris/', str(row['organization_id']) + str(row[f'Naam_{role} First']) + str(row[f'Naam_{role} Last']) + role)
          g.add((person_role_mandataris, RDF.type, ns.mandaat.Mandataris))
          add_literal(g, person_role_mandataris, ns.mu.uuid, person_role_mandataris_uuid, XSD.string)

          g.add((person_role_mandataris, ns.mandaat.isBestuurlijkeAliasVan, person_role))
          g.add((person_role_mandataris, ns.org.holds, person_role_mandaat))
          #add_literal(g, person_role_mandataris, ns.mandaat.start, str(row[f'Datum verkiezing {role}']), XSD.date)
          #Argument Error "2020-08-21 00:00:00" is not a valid <http://www.w3.org/2001/XMLSchema#dateTime> literal: {:production=>:literal, :token=>";"}:
          #einde
          #status
          g.add((person_role, ns.mandaat.isAangesteldAls, person_role_mandataris))
          g.add((person_role_mandaat, ns.org.heldBy, person_role_mandataris))

      ####
      # Lids
      for role in roles_lid:
        if exists_role(row, role):
          lid, lid_uuid =  concept_uri(ns.lblod + 'persoon/', str(row[f'Naam_{role} First']) + str(row[f'Naam_{role} Last']))
          g.add((lid, RDF.type, ns.person.Person))
          add_literal(g, lid, ns.mu.uuid, lid_uuid, XSD.string)
          add_literal(g, lid, FOAF.givenName, str(row[f'Naam_{role} First']))
          add_literal(g, lid, FOAF.familyName, str(row[f'Naam_{role} Last']))

          ## Lid - Mandaat
          lid_mandaat, lid_mandaat_uuid = concept_uri(ns.lblod + 'mandaat/', str(row['organization_id']) + str(row[f'Naam_{role} First']) + str(row[f'Naam_{role} Last']))
          g.add((lid_mandaat, RDF.type, ns.mandaat.Mandaat))
          add_literal(g, lid_mandaat, ns.mu.uuid, lid_mandaat_uuid, XSD.string)

          bestuurfunctie_id = get_concept_id(codelist_ere, get_label_role(role[:-1].lower() + ' worship'))
          g.add((lid_mandaat, ns.org.role, bestuurfunctie_id))
          g.add((lid_mandaat, ns.org.postIn, bestuur_temporary))
          g.add((bestuur_temporary, ns.org.hasPost, lid_mandaat))

          ## Lid - Mandataris
          lid_mandataris, lid_mandataris_uuid = concept_uri(ns.lblod + 'mandataris/', str(row['organization_id']) + str(row[f'Naam_{role} First']) + str(row[f'Naam_{role} Last']) + role)
          g.add((lid_mandataris, RDF.type, ns.mandaat.Mandataris))
          add_literal(g, lid_mandataris, ns.mu.uuid, lid_mandataris_uuid, XSD.string)

          g.add((lid_mandataris, ns.mandaat.isBestuurlijkeAliasVan, lid))
          g.add((lid_mandataris, ns.org.holds, lid_mandaat))
          #add_literal(g, lid_mandataris, ns.mandaat.start, str(row[f'Datum verkiezing {role}']), XSD.date)

          g.add((lid_mandaat, ns.org.heldBy, lid_mandataris))
          g.add((lid, ns.mandaat.isAangesteldAls, lid_mandataris))

  print("########### Mapping finished #############")

  export_data(g, f'worship-{mode}')
  