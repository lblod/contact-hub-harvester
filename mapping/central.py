import numpy as np
from datetime import datetime, timedelta
import dateparser
from rdflib import Graph
from rdflib.namespace import XSD, FOAF, SKOS, RDF, RDFS

from helper.functions import add_literal, concept_uri, exists_address, exists_bestuursperiode, exists_contact_role, exists_role, load_graph, get_concept_id, get_label_role, get_cleansed_data, export_data
import helper.namespaces as ns

def main(file, mode):
  # To have a new cleansed data, delete the previous xlsx in the output folder
  central_cleansed = get_cleansed_data(file, 'central')

  lblod = ns.get_namespace(mode)

  g = Graph()
  codelist_ere = load_graph('codelist-ere')
  codelist_bestuurseenheid = load_graph('bestuurseenheid-classificatie-code')
  bestuurseenheid_classification_id = get_concept_id(codelist_bestuurseenheid, 'Centraal bestuur van de eredienst')

  print("########### Mapping started #############")

  for _, row in central_cleansed.iterrows():    
    abb_id, abb_uuid = concept_uri(lblod + 'centraalBestuurVanDeEredienst/', str(row['Titel']))
    g.add((abb_id, RDF.type, ns.org.Organization))
    g.add((abb_id, RDF.type, ns.euro.PublicOrganisation))
    g.add((abb_id, RDF.type, ns.besluit.Bestuurseenheid))
    g.add((abb_id, RDF.type, ns.ere.CentraalBestuurVanDeEredienst))
    add_literal(g, abb_id, ns.mu.uuid, abb_uuid, XSD.string)

    add_literal(g, abb_id, SKOS.prefLabel, str(row['Naam_CKB']))
    #add_literal(g, abb_id, ns.rov.legalName, str(row['Naam_CKB']))

    g.add((abb_id, ns.org.classification, bestuurseenheid_classification_id))

    type_ere = get_concept_id(codelist_ere, str(row['Type_eredienst_CKB']))
    g.add((abb_id, ns.ere.typeEredienst, type_ere))

    status = get_concept_id(codelist_ere, str(row['Status_CKB_cleansed']))
    g.add((abb_id, ns.rov.orgStatus, status))

    gemeente_id, gemeente_uuid = concept_uri(lblod + 'werkingsgebieden/', str(row['Gemeente Cleansed']))
    g.add((gemeente_id, RDF.type, ns.prov.Location))
    add_literal(g, gemeente_id, ns.mu.uuid, gemeente_uuid, XSD.string)
    add_literal(g, gemeente_id, RDFS.label, str(row['Gemeente Cleansed']))
    g.add((abb_id, ns.besluit.werkingsgebied, gemeente_id))

    if str(row['Representatief orgaan']) != str(np.nan):
      national_id, _ = concept_uri(lblod + 'representatiefOrgaan/', str(row['Representatief orgaan']))
      g.add((abb_id, ns.org.linkedTo, national_id))

    bo_id, bo_uuid = concept_uri(lblod + 'centraleBestuursorgaan/', str(row['Titel']))
    g.add((bo_id, RDF.type, ns.besluit.Bestuursorgaan))
    g.add((bo_id, RDF.type, ns.ere.CentraleBestuursorgaan))
    add_literal(g, bo_id, ns.mu.uuid, bo_uuid, XSD.string)

    bestuursorgaan_classification_id = get_concept_id(codelist_ere, str(row['Bestuursorgaan Type']))
    g.add((bo_id, ns.org.classification, bestuursorgaan_classification_id))

    g.add((bo_id, ns.besluit.bestuurt, abb_id))    

    if str(row['KBO_CKB_cleansed']) != str(np.nan):
      id_class, id_uuid = concept_uri(lblod +'identificator/', str(row['KBO_CKB_cleansed']))
      g.add((id_class, RDF.type, ns.adms.Identifier))
      add_literal(g, id_class, SKOS.notation, 'KBO nummer', XSD.string)
      add_literal(g, id_class, ns.mu.uuid, id_uuid, XSD.string)

      kbo_uri, kbo_uuid  = concept_uri(lblod + 'gestructureerdeIdentificator/', str(row['KBO_CKB_cleansed']))
      g.add((kbo_uri, RDF.type, ns.generiek.GestructureerdeIdentificator))
      add_literal(g, kbo_uri, ns.mu.uuid, kbo_uuid, XSD.string)
      add_literal(g, kbo_uri, ns.generiek.lokaleIdentificator, str(row['KBO_CKB_cleansed']), XSD.string)
      g.add((id_class, ns.generiek.gestructureerdeIdentificator, kbo_uri))

      g.add((abb_id, ns.adms.identifier, id_class))

    if str(row['Titel']) != str(np.nan):
      id_class, id_uuid = concept_uri(lblod +'identificator/', str(row['Titel']))
      g.add((id_class, RDF.type, ns.adms.Identifier))
      add_literal(g, id_class, SKOS.notation, 'SharePoint identificator', XSD.string)
      add_literal(g, id_class, ns.mu.uuid, id_uuid, XSD.string)

      naam_uri, naam_uuid = concept_uri(lblod + 'gestructureerdeIdentificator/', str(row['Titel']))
      g.add((naam_uri, RDF.type, ns.generiek.GestructureerdeIdentificator))
      add_literal(g, naam_uri, ns.mu.uuid, naam_uuid, XSD.string)
      add_literal(g, naam_uri, ns.generiek.lokaleIdentificator, str(row['Titel']), XSD.string)
      g.add((id_class, ns.generiek.gestructureerdeIdentificator, naam_uri))

      g.add((abb_id, ns.adms.identifier, id_class))

    # Vestiging
    if exists_address(row):
      vestiging_uri, vestiging_uuid = concept_uri(lblod + 'vestiging/', str(row['Titel']))
      g.add((vestiging_uri, RDF.type, ns.org.Site))
      add_literal(g, vestiging_uri, ns.mu.uuid, vestiging_uuid, XSD.string)

      address_uri, address_uuid = concept_uri(lblod + 'adressen/', str(row['Titel']))
      g.add((address_uri, RDF.type, ns.locn.Address))
      add_literal(g, address_uri, ns.mu.uuid, address_uuid, XSD.string)
      
      add_literal(g, address_uri, ns.locn.thoroughfare, str(row['Straat']))
      add_literal(g, address_uri, ns.adres['Adresvoorstelling.huisnummer'], str(row['Huisnr Cleansed']), XSD.string)
      add_literal(g, address_uri, ns.adres['Adresvoorstelling.busnummer'], str(row['Busnummer Cleansed']), XSD.string)
      add_literal(g, address_uri, ns.locn.postCode, str(row['Postcode Cleansed']), XSD.string)
      add_literal(g, address_uri, ns.adres.gemeentenaam, str(row['Gemeente Cleansed']))
      add_literal(g, address_uri, ns.locn.adminUnitL2, str(row['Provincie Cleansed']))
      add_literal(g, address_uri, ns.adres.land, 'België')

      g.add((vestiging_uri, ns.organisatie.bestaatUit, address_uri))
      g.add((abb_id, ns.org.hasPrimarySite, vestiging_uri))

    roles = ['voorzitter', 'secretaris']

    if exists_bestuursperiode(row, roles):    
      # Bestuursorgaan (in bestuursperiode)

      bestuur_temporary_17, bestuur_temporary_17_uuid = concept_uri(lblod + 'bestuursorganen/', str(row['Titel']) + '2017')
      g.add((bestuur_temporary_17, RDF.type, ns.besluit.Bestuursorgaan))
      add_literal(g, bestuur_temporary_17, ns.mu.uuid, bestuur_temporary_17_uuid, XSD.string)
      g.add((bestuur_temporary_17, ns.generiek.isTijdspecialisatieVan, bo_id))

      if str(row['Verkiezingen17_Opmerkingen Cleansed']) != str(np.nan):
        add_literal(g, bestuur_temporary_17, ns.mandaat.bindingStart, dateparser.parse(str(row['Verkiezingen17_Opmerkingen Cleansed'])), XSD.dateTime)
      if str(row['Verkiezingen2020_Opmerkingen Cleansed']) != str(np.nan):
        add_literal(g, bestuur_temporary_17, ns.mandaat.bindingEinde, dateparser.parse(str(row['Verkiezingen2020_Opmerkingen Cleansed'])), XSD.dateTime)
      elif str(row['Verkiezingen17_Opmerkingen Cleansed']) != str(np.nan):
        # end date = start date + 3 years
        add_literal(g, bestuur_temporary_17, ns.mandaat.bindingEinde, (dateparser.parse(str(row['Verkiezingen17_Opmerkingen Cleansed'])) + timedelta(days=1095)).isoformat(), XSD.dateTime)
      elif str(row['Status_CKB_cleansed']) == 'Niet Actief':
        add_literal(g, bestuur_temporary_17, ns.mandaat.bindingEinde, dateparser.parse(str(row['Opmerkingen_CKB Date'])), XSD.dateTime)

      if str(row['Status_CKB_cleansed']) == 'Actief':
        bestuur_temporary_20, bestuur_temporary_20_uuid = concept_uri(lblod + 'bestuursorganen/', str(row['Titel']) + '2020')
        g.add((bestuur_temporary_20, RDF.type, ns.besluit.Bestuursorgaan))
        add_literal(g, bestuur_temporary_20, ns.mu.uuid, bestuur_temporary_20_uuid, XSD.string)
        g.add((bestuur_temporary_20, ns.generiek.isTijdspecialisatieVan, bo_id))

        if str(row['Verkiezingen2020_Opmerkingen Cleansed']) != str(np.nan):
          add_literal(g, bestuur_temporary_20, ns.mandaat.bindingStart, dateparser.parse(str(row['Verkiezingen2020_Opmerkingen Cleansed'])), XSD.dateTime)

        # From 2023 the next bestuursorgaan in bestuursperiode will begin the same day
        if str(row['Type_eredienst_CKB']) != 'Israëlitisch':
          add_literal(g, bestuur_temporary_20, ns.mandaat.bindingEinde, datetime(2023, 4, 30).isoformat(), XSD.dateTime)
        else:
          add_literal(g, bestuur_temporary_20, ns.mandaat.bindingEinde, datetime(2023, 5, 31).isoformat(), XSD.dateTime)
    
       # Mandaat / Mandataris
      for role in roles:
        if exists_role(row, role):
          # Person Role
          person_role, person_uuid = concept_uri(lblod + 'personen/', str(row[f'Naam_{role} First']) + str(row[f'Naam_{role} Last']))
          g.add((person_role, RDF.type, ns.person.Person))
          add_literal(g, person_role, ns.mu.uuid, person_uuid, XSD.string)
          add_literal(g, person_role, FOAF.givenName, str(row[f'Naam_{role} First']))
          add_literal(g, person_role, FOAF.familyName, str(row[f'Naam_{role} Last']))

          ## Mandaat
          person_role_mandaat, person_role_mandaat_uuid = concept_uri(lblod + 'mandaten/', str(row['Titel']) + str(row[f'Naam_{role} First']) + str(row[f'Naam_{role} Last']))
          g.add((person_role_mandaat, RDF.type, ns.mandaat.Mandaat))
          add_literal(g, person_role_mandaat, ns.mu.uuid, person_role_mandaat_uuid, XSD.string)

          bestuurfunctie_id = get_concept_id(codelist_ere, get_label_role(role + ' central'))
          g.add((person_role_mandaat, ns.org.role, bestuurfunctie_id))

          if str(row['Verkiezingen2020_Opmerkingen Cleansed']) != str(np.nan):
            g.add((person_role_mandaat, ns.org.postIn, bestuur_temporary_20))
            g.add((bestuur_temporary_20, ns.org.hasPost, person_role_mandaat))
          else:
            g.add((person_role_mandaat, ns.org.postIn, bestuur_temporary_17))
            g.add((bestuur_temporary_17, ns.org.hasPost, person_role_mandaat))

          ## Mandataris
          person_role_mandataris, person_role_mandataris_uuid = concept_uri(lblod + 'mandatarissen/', str(row['Titel'] + str(row[f'Naam_{role} First']) + str(row[f'Naam_{role} Last']) + role))
          g.add((person_role_mandataris, RDF.type, ns.mandaat.Mandataris))
          g.add((person_role_mandataris, RDF.type, ns.ere.EredienstMandataris))
          add_literal(g, person_role_mandataris, ns.mu.uuid, person_role_mandataris_uuid, XSD.string)

          ## Mandataris - Contact punt
          if exists_contact_role(row, role):
            person_role_contact_uri, person_role_contact_uuid = concept_uri(lblod + 'contact-punten/', str(row['Titel']) + str(row[f'Naam_{role} First']) + str(row[f'Naam_{role} Last']) + str(row[f'Tel_{role} 1']))
            g.add((person_role_contact_uri, RDF.type, ns.schema.ContactPoint))
            add_literal(g, person_role_contact_uri, ns.mu.uuid, person_role_contact_uuid, XSD.string)
            g.add((person_role_mandataris, ns.schema.contactPoint, person_role_contact_uri))

            add_literal(g, person_role_contact_uri, ns.schema.telephone, str(row[f'Tel_{role} 1']), XSD.string)
            add_literal(g, person_role_contact_uri, ns.schema.email, str(row[f'Mail_{role} Cleansed']), XSD.string)
          
            if str(row[f'Tel_{role} 2']) != str(np.nan):
              person_role_contact_2_uri, person_role_contact_2_uuid = concept_uri(lblod + 'contact-punten/', str(row['Titel']) + str(row[f'Naam_{role} First']) + str(row[f'Naam_{role} Last']) + str(row[f'Tel_{role} 2']))
              g.add((person_role_contact_2_uri, RDF.type, ns.schema.ContactPoint))
              add_literal(g, person_role_contact_2_uri, ns.mu.uuid, person_role_contact_2_uuid, XSD.string)
              
              add_literal(g, person_role_contact_2_uri, ns.schema.telephone, str(row[f'Tel_{role} 2']), XSD.string)
              g.add((person_role_mandataris, ns.schema.contactPoint, person_role_contact_2_uri))
          
          g.add((person_role_mandataris, ns.mandaat.isBestuurlijkeAliasVan, person_role))
          g.add((person_role_mandataris, ns.org.holds, person_role_mandaat))
          if str(row['Verkiezingen2020_Opmerkingen Cleansed']) != str(np.nan):
            add_literal(g, person_role_mandataris, ns.mandaat.start, dateparser.parse(str(row['Verkiezingen2020_Opmerkingen Cleansed'])), XSD.dateTime)
          
          #einde
          g.add((person_role_mandataris, ns.mandaat.status, ns.mandataris_status['Effectief']))

          g.add((person_role_mandaat, ns.org.heldBy, person_role_mandataris))
          g.add((person_role, ns.mandaat.isAangesteldAls, person_role_mandataris))

  print("########### Mapping finished #############")       

  export_data(g, f'central-{mode}')


