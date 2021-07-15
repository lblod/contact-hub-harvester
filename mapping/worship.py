import json
import numpy as np
import pandas as pd
from datetime import date, datetime, timedelta
import dateparser
from numpy.core.numeric import full
from rdflib import Graph, URIRef
from rdflib.namespace import FOAF, XSD, FOAF, SKOS, RDF, RDFS, DCTERMS

from helper.functions import add_literal, concept_uri, exists_bestuursperiode_worship, exists_role_worship, export_data, get_cleansed_data, exists_address, exists_address_role, exists_contact_role, exists_bestuursperiode_worship, get_adm_unit_concept, get_werkingsgebied_concept, load_graph, get_concept_id, get_label_role, exists_given_and_family_name, get_full_address, shuffle_word
import helper.namespaces as ns


def main(file, mode): 
  worship_cleansed = get_cleansed_data(file, 'worship')

  lblod = ns.get_namespace(mode)

  g = Graph()
  codelist_ere = load_graph('codelist-ere')
  codelist_bestuurseenheid = load_graph('bestuurseenheid-classificatie-code')
  bestuurseenheid_classification_id = get_concept_id(codelist_bestuurseenheid, 'Bestuur van de eredienst')
  BEDIENAAR_FUNCTIE = URIRef('http://lblod.data.gift/concepts/efbf2ff50b5c4f693f129ac03319c4f2')
  BEDIENNAR_FUNCTIE_UUID = 'efbf2ff50b5c4f693f129ac03319c4f2'
  VESTIGING_TYPE = URIRef('http://lblod.data.gift/concepts/f1381723dec42c0b6ba6492e41d6f5dd')

  print("########### Mapping started #############")

  for _, row in worship_cleansed.iterrows():
    abb_id, abb_uuid = concept_uri(lblod + 'besturenVanDeEredienst/', str(row['organization_id']))
    #g.add((abb_id, RDF.type, ns.org.Organization))
    #g.add((abb_id, RDF.type, ns.besluit.Bestuurseenheid))
    g.add((abb_id, RDF.type, ns.ere.BestuurVanDeEredienst))
    
    add_literal(g, abb_id, ns.mu.uuid, abb_uuid, XSD.string)

    add_literal(g, abb_id, SKOS.prefLabel, str(row['Naam_EB']), XSD.string)
    #add_literal(g, abb_id, ns.rov.legalName, str(row['Naam_EB']), XSD.string)

    g.add((abb_id, ns.org.classification, bestuurseenheid_classification_id))

    if str(row['Type_eredienst Cleansed']) != str(np.nan):
      type_ere = get_concept_id(codelist_ere, str(row['Type_eredienst Cleansed']))
      g.add((abb_id, ns.ere.typeEredienst, type_ere))    
  
    add_literal(g, abb_id, ns.ere.grensoverschrijdend, str(row['Grensoverschrijdend']), XSD.boolean)

    add_literal(g, abb_id, ns.ere.denominatie, str(row['Strekking Cleansed']), XSD.string)

    status = get_concept_id(codelist_ere, str(row['Status_EB Cleansed']))
    g.add((abb_id, ns.rov.orgStatus, status))

    if str(row['Naam_CKB_EB1']) != str(np.nan):
      ckb_id, _ = concept_uri(lblod + 'centraleBesturenVanDeEredienst/', str(row['Naam_CKB_EB1']))
      g.add((ckb_id, ns.org.hasSubOrganization, abb_id))

    if str(row['Representatief orgaan']) != str(np.nan):
      national_id, _ = concept_uri(lblod + 'representatieveOrganen/', str(row['Representatief orgaan']))
      g.add((national_id, ns.org.linkedTo, abb_id))

    bo_id, bo_uuid = concept_uri(lblod + 'eredienstbestuursorganen/', str(row['organization_id']) + 'eredienstbestuursorganen')
    g.add((bo_id, RDF.type, ns.besluit.Bestuursorgaan))
    #g.add((bo_id, RDF.type, ns.ere.Eredienstbestuursorgaan))
    add_literal(g, bo_id, ns.mu.uuid, bo_uuid, XSD.string)

    if str(row['Bestuursorgaan Type']) != str(np.nan):
      bestuursorgaan_classification_id = get_concept_id(codelist_ere, str(row['Bestuursorgaan Type']))
      g.add((bo_id, ns.org.classification, bestuursorgaan_classification_id))

    g.add((bo_id, ns.besluit.bestuurt, abb_id))    
    
    if str(row['KBO_EB Cleansed']) != str(np.nan):
      id_class, id_uuid = concept_uri(lblod +'identificatoren/', str(row['KBO_EB Cleansed']) + 'identificatoren')
      g.add((id_class, RDF.type, ns.adms.Identifier))
      add_literal(g, id_class, SKOS.notation, 'KBO nummer', XSD.string)
      add_literal(g, id_class, ns.mu.uuid, id_uuid, XSD.string)

      kbo_id, kbo_uuid = concept_uri(lblod + 'gestructureerdeIdentificatoren/', str(row['KBO_EB Cleansed']) + 'gestructureerdeIdentificatoren')
      g.add((kbo_id, RDF.type, ns.generiek.GestructureerdeIdentificator))
      add_literal(g, kbo_id, ns.mu.uuid, kbo_uuid, XSD.string)
      add_literal(g, kbo_id, ns.generiek.lokaleIdentificator, str(row['KBO_EB Cleansed']), XSD.string)
      g.add((id_class, ns.generiek.gestructureerdeIdentificator, kbo_id))

      g.add((abb_id, ns.adms.identifier, id_class))

    if str(row['Titel Cleansed']) != str(np.nan):
      id_class, id_uuid = concept_uri(lblod +'identificatoren/', str(row['Titel Cleansed']) + 'identificatoren')
      g.add((id_class, RDF.type, ns.adms.Identifier))
      add_literal(g, id_class, SKOS.notation, 'SharePoint identificator', XSD.string)
      add_literal(g, id_class, ns.mu.uuid, id_uuid, XSD.string)

      naam_uri, naam_uuid = concept_uri(lblod + 'gestructureerdeIdentificator/', str(row['Titel Cleansed']) + 'gestructureerdeIdentificator')
      g.add((naam_uri, RDF.type, ns.generiek.GestructureerdeIdentificator))
      add_literal(g, naam_uri, ns.mu.uuid, naam_uuid, XSD.string)
      add_literal(g, naam_uri, ns.generiek.lokaleIdentificator, str(row['Titel Cleansed']), XSD.string)
      g.add((id_class, ns.generiek.gestructureerdeIdentificator, naam_uri))

      g.add((abb_id, ns.adms.identifier, id_class))

    if row['Change Event Cleansed'] != '{}':
      change_events_ = row['Change Event Cleansed']
      json_acceptable_string = change_events_.replace("'", "\"")
      change_events = json.loads(json_acceptable_string)
      
      for key, value in change_events.items():
        change_event_id = get_concept_id(codelist_ere, key)

        ce_id, ce_uuid = concept_uri(lblod + 'veranderingsgebeurtenissen/', abb_uuid + row['Change Event Cleansed'])
        g.add((ce_id, RDF.type, ns.org.ChangeEvent))
        add_literal(g, ce_id, ns.mu.uuid, ce_uuid, XSD.string)
        g.add((ce_id, ns.ch.typeWijziging, change_event_id))
        add_literal(g, ce_id, DCTERMS.date, value, XSD.dateTime)
        add_literal(g, ce_id, DCTERMS.description, row['Statusinfo'], XSD.string)
        
        if key == 'Opschorting Erkenning':
          g.add((ce_id, ns.org.originalOrganization, abb_id))
          g.add((abb_id, ns.org.changedBy, ce_id))
        else:
          g.add((ce_id, ns.org.resultingOrganization, abb_id))
          g.add((abb_id, ns.org.resultedFrom, ce_id))

    local_eng = row['Local Engagement Cleansed']
    json_acceptable_string = local_eng.replace("'", "\"")
    local_eng = json.loads(json_acceptable_string)

    if len(local_eng['Cross-Border']) > 0:
      type_involvement = get_concept_id(codelist_ere, 'Toezichthoudend en financierend')
      for municipality, perc in local_eng['Municipality'].items():
        municipality_res = get_adm_unit_concept(municipality, "Gemeente")
        if municipality_res != None:
          municipality_adminunit = URIRef(municipality_res['s']['value'])
          pi_id, pi_uuid = concept_uri(lblod + 'betrokkenLokaleBesturen/', municipality + abb_uuid)
          g.add((pi_id, RDF.type, ns.ere.BetrokkenLokaleBesturen))
          add_literal(g, pi_id, ns.mu.uuid, pi_uuid, XSD.string)
          if perc != '':
            add_literal(g, pi_id, ns.ere.financieringspercentage, str(perc), XSD.float)
            g.add((pi_id, ns.ere.typebetrokkenheid, type_involvement))
          g.add((pi_id, ns.org.organization, abb_id))
          
          g.add((municipality_adminunit, ns.ere.betrokkenBestuur, pi_id))
          g.add((municipality_adminunit, RDF.type, ns.besluit.Bestuurseenheid))
          add_literal(g, municipality_adminunit, SKOS.prefLabel, municipality, XSD.string)
          add_literal(g, municipality_adminunit, ns.mu.uuid, municipality_res['uuid']['value'], XSD.string)

      for province, perc in local_eng['Province'].items():
        province_res = get_adm_unit_concept(province, "Provincie")
        if province_res != None:
          province_adminunit = URIRef(province_res['s']['value'])
          pi_id, pi_uuid = concept_uri(lblod + 'betrokkenLokaleBesturen/', province + abb_uuid)
          g.add((pi_id, RDF.type, ns.ere.BetrokkenLokaleBesturen))
          add_literal(g, pi_id, ns.mu.uuid, pi_uuid, XSD.string)
          if perc != '':
            add_literal(g, pi_id, ns.ere.financieringspercentage, str(perc), XSD.float)
            g.add((pi_id, ns.ere.typebetrokkenheid, type_involvement))
            
          g.add((pi_id, ns.org.organization, abb_id))
          
          g.add((province_adminunit, ns.ere.betrokkenBestuur, pi_id))
          g.add((province_adminunit, RDF.type, ns.besluit.Bestuurseenheid))
          add_literal(g, province_adminunit, SKOS.prefLabel, province, XSD.string)
          add_literal(g, province_adminunit, ns.mu.uuid, province_res['uuid']['value'], XSD.string)
      
      if len(local_eng['Cross-Border']) == 1 and local_eng['Municipality']:          
        location_concept_g = get_werkingsgebied_concept(local_eng['Cross-Border'][0], 'Gemeente')
        if location_concept_g != None:
          gemeente_id = URIRef(location_concept_g['s']['value'])
          g.add((gemeente_id, RDF.type, ns.prov.Location))
          add_literal(g, gemeente_id, ns.mu.uuid, location_concept_g['uuid']['value'], XSD.string)
          add_literal(g, gemeente_id, RDFS.label, local_eng['Cross-Border'][0], XSD.string)
          add_literal(g, gemeente_id, ns.ext.werkingsgebiedNiveau, 'Gemeente', XSD.string)
          g.add((abb_id, ns.besluit.werkingsgebied, gemeente_id))
      elif len(local_eng['Cross-Border']) == 1 and local_eng['Province']:
        location_concept_p = get_werkingsgebied_concept(local_eng['Cross-Border'][0], 'Provincie')
        if location_concept_p != None:
          province_id = URIRef(location_concept_p['s']['value'])
          g.add((province_id, RDF.type, ns.prov.Location))
          add_literal(g, province_id, ns.mu.uuid, location_concept_p['uuid']['value'], XSD.string)
          add_literal(g, province_id, RDFS.label, local_eng['Cross-Border'][0], XSD.string)
          add_literal(g, province_id, ns.ext.werkingsgebiedNiveau, 'Provincie', XSD.string)
          g.add((abb_id, ns.besluit.werkingsgebied, province_id))
      else:
        region_label = ', '.join(local_eng['Cross-Border'])
        region_id, region_uuid = concept_uri(lblod + 'werkingsgebieden/', region_label + abb_uuid)
        g.add((region_id, RDF.type, ns.prov.Location))
        add_literal(g, region_id, ns.mu.uuid, region_uuid, XSD.string)
        add_literal(g, region_id, RDFS.label, region_label, XSD.string)
        add_literal(g, region_id, ns.ext.werkingsgebiedNiveau, 'Regio', XSD.string)
        g.add((abb_id, ns.besluit.werkingsgebied, region_id))
    
    # Vestiging
    if exists_address(row):
      site_id, site_uuid = concept_uri(lblod + 'vestigingen/', str(row['organization_id']) + 'vestigingen')
      g.add((site_id, RDF.type, ns.org.Site))
      add_literal(g, site_id, ns.mu.uuid, site_uuid, XSD.string)

      address_id, address_uuid = concept_uri(lblod + 'adressen/', str(row['organization_id']) + 'adressen')
      g.add((address_id, RDF.type, ns.locn.Address))
      add_literal(g, address_id, ns.mu.uuid, address_uuid, XSD.string)
      
      add_literal(g, address_id, ns.locn.thoroughfare, str(row['Straat']), XSD.string)
      add_literal(g, address_id, ns.adres['Adresvoorstelling.huisnummer'], str(row['Huisnr Cleansed']), XSD.string)
      add_literal(g, address_id, ns.adres['Adresvoorstelling.busnummer'], str(row['Busnummer Cleansed']), XSD.string)
      add_literal(g, address_id, ns.locn.postCode, str(row['Postcode Cleansed']), XSD.string)
      add_literal(g, address_id, ns.adres.gemeentenaam, str(row['Gemeente Cleansed']), XSD.string)
      add_literal(g, address_id, ns.locn.adminUnitL2, str(row['Provincie Cleansed']), XSD.string)
      add_literal(g, address_id, ns.adres.land, 'België', XSD.string)
      
      add_literal(g, address_id, ns.locn.fullAddress, get_full_address(str(row['Straat']), str(row['Huisnr Cleansed']), str(row['Busnummer Cleansed']), str(row['Postcode Cleansed']), str(row['Gemeente Cleansed'])), XSD.string)

      g.add((site_id, ns.organisatie.bestaatUit, address_id))
      g.add((site_id, ns.ere.vestigingstype, VESTIGING_TYPE))
      g.add((abb_id, ns.org.hasPrimarySite, site_id))

    # DUMMY Bedienaar
    if str(row['Naam_voorzitter Cleansed']) != str(np.nan):
      rol_bedienaar_id, rol_bedienaar_uuid = concept_uri(lblod + 'rollenBedienaar/', abb_uuid + 'Bedienaar')
      g.add((rol_bedienaar_id, RDF.type, ns.ere.RolBedienaar))
      add_literal(g, rol_bedienaar_id, ns.mu.uuid, rol_bedienaar_uuid, XSD.string)

      position_rol_bedienaar_id, position_rol_bedienaar_uuid = concept_uri(lblod + 'positiesBedienaar/', abb_uuid + BEDIENNAR_FUNCTIE_UUID)
      g.add((position_rol_bedienaar_id, RDF.type, ns.ere.PositieBedienaar))
      add_literal(g, position_rol_bedienaar_id, ns.mu.uuid, position_rol_bedienaar_uuid, XSD.string)
      g.add((position_rol_bedienaar_id, ns.ere.functie, BEDIENAAR_FUNCTIE))
      g.add((abb_id, ns.ere.wordtBediendDoor, position_rol_bedienaar_id))

      shuffled_first_name = shuffle_word(str(row['Naam_voorzitter First']))
      shuffled_last_name = shuffle_word(str(row['Naam_voorzitter Last']))
      shuffled_cleansed_name = shuffle_word(str(row['Naam_voorzitter Cleansed']))
      if exists_given_and_family_name(row, 'voorzitter'):
        person_rol_bedienaar, person_rol_bedienaar_uuid = concept_uri(lblod + 'personen/', shuffled_first_name + shuffled_last_name)
        add_literal(g, person_rol_bedienaar, FOAF.givenName, shuffled_first_name, XSD.string)
        add_literal(g, person_rol_bedienaar, FOAF.familyName, shuffled_last_name, XSD.string)
      else:
        person_rol_bedienaar, person_rol_bedienaar_uuid = concept_uri(lblod + 'personen/', shuffled_cleansed_name)
        add_literal(g, person_rol_bedienaar, FOAF.givenName, shuffled_cleansed_name, XSD.string)
      
      g.add((person_rol_bedienaar, RDF.type, ns.person.Person))
      add_literal(g, person_rol_bedienaar, ns.mu.uuid, person_rol_bedienaar_uuid, XSD.string)

      g.add((rol_bedienaar_id, ns.org.heldBy, person_rol_bedienaar))
      g.add((rol_bedienaar_id, ns.org.holds, position_rol_bedienaar_id))

    roles = ['voorzitter', 'secretaris', 'penningmeester']
    roles_lid = ['Lid4', 'Lid5']

    if exists_bestuursperiode_worship(row, roles+roles_lid):
      # Bestuursorgaan (in bestuursperiode)
      
      # Bestuursorgaan in bestuursperiode 2017-2020
      bestuur_temporary_17, bestuur_temporary_17_uuid = concept_uri(lblod + 'eredienstbestuursorganen/', str(row['organization_id']) + 'eredienstbestuursorganen/2017')
      g.add((bestuur_temporary_17, RDF.type, ns.besluit.Bestuursorgaan))
      #g.add((bestuur_temporary_17, RDF.type, ns.ere.Eredienstbestuursorgaan))

      add_literal(g, bestuur_temporary_17, ns.mu.uuid, bestuur_temporary_17_uuid, XSD.string)
      g.add((bestuur_temporary_17, ns.generiek.isTijdspecialisatieVan, bo_id))
      
      if str(row['Verkiezingen17_Opmerkingen Cleansed']) != str(np.nan):
        add_literal(g, bestuur_temporary_17, ns.mandaat.bindingStart, dateparser.parse(str(row['Verkiezingen17_Opmerkingen Cleansed'])), XSD.dateTime)
        
      if str(row['Verkiezingen2020_Opmerkingen Cleansed']) != str(np.nan):
        add_literal(g, bestuur_temporary_17, ns.mandaat.bindingEinde, dateparser.parse(str(row['Verkiezingen2020_Opmerkingen Cleansed'])), XSD.dateTime)
      elif str(row['Verkiezingen17_Opmerkingen Cleansed']) != str(np.nan):
        # end date = start date + 3 years
        add_literal(g, bestuur_temporary_17, ns.mandaat.bindingEinde, (dateparser.parse(str(row['Verkiezingen17_Opmerkingen Cleansed'])) + timedelta(days=1095)).isoformat(), XSD.dateTime)

      if str(row['Status_EB Cleansed']) == 'Actief':
        # Bestuursorgaan in bestuursperiode 2020-2023
        bestuur_temporary_20, bestuur_temporary_20_uuid = concept_uri(lblod + 'eredienstbestuursorganen/', str(row['organization_id']) + 'eredienstbestuursorganen/2020')
        g.add((bestuur_temporary_20, RDF.type, ns.besluit.Bestuursorgaan))
        #g.add((bestuur_temporary_20, RDF.type, ns.ere.Eredienstbestuursorgaan))
        add_literal(g, bestuur_temporary_20, ns.mu.uuid, bestuur_temporary_20_uuid, XSD.string)
        g.add((bestuur_temporary_20, ns.generiek.isTijdspecialisatieVan, bo_id))
        
        if str(row['Verkiezingen2020_Opmerkingen Cleansed']) != str(np.nan):
          add_literal(g, bestuur_temporary_20, ns.mandaat.bindingStart, dateparser.parse(str(row['Verkiezingen2020_Opmerkingen Cleansed'])), XSD.dateTime)
      
        # From 2023 the next bestuursorgaan in bestuursperiode will begin the same day
        if str(row['Type_eredienst Cleansed']) == 'Israëlitisch':
          add_literal(g, bestuur_temporary_20, ns.mandaat.bindingEinde, datetime(2023, 5, 31).isoformat(), XSD.dateTime)
        else:
          add_literal(g, bestuur_temporary_20, ns.mandaat.bindingEinde, datetime(2023, 4, 30).isoformat(), XSD.dateTime)

      person_lid_mandaat = None
      # Mandaat / Mandataris
      for role in roles:
        if exists_role_worship(row, role):
          # Person role
          if exists_given_and_family_name(row, role):
            person_role, person_uuid = concept_uri(lblod + 'personen/', str(row[f'Naam_{role} First']) + str(row[f'Naam_{role} Last']))
            add_literal(g, person_role, FOAF.givenName, str(row[f'Naam_{role} First']), XSD.string)
            add_literal(g, person_role, FOAF.familyName, str(row[f'Naam_{role} Last']), XSD.string)
          else:
            person_role, person_uuid = concept_uri(lblod + 'personen/', str(row[f'Naam_{role} Cleansed']))
            add_literal(g, person_role, FOAF.givenName, str(row[f'Naam_{role} Cleansed']), XSD.string)
            
          g.add((person_role, RDF.type, ns.person.Person))
          add_literal(g, person_role, ns.mu.uuid, person_uuid, XSD.string)

          person_role_mandaat = None
          if str(row[f'Datum verkiezing {role}']) != 'NaT':
            year_election = dateparser.parse(str(row[f'Datum verkiezing {role}'])).year
            
            if year_election <= 2019:
              person_role_mandaat, person_role_mandaat_uuid = concept_uri(lblod + 'mandaten/', str(row['organization_id']) + 'eredienstbestuursorganen/2017/' + role)
              person_lid_mandaat, person_lid_mandaat_uuid = concept_uri(lblod + 'mandaten/', str(row['organization_id']) + 'eredienstbestuursorganen/2017/Lid')
              #if str(row[f'Type Helft Cleansed {role}']) == 'Kleine helft':
                #person_lid_mandaat, person_lid_mandaat_uuid = concept_uri(lblod + 'mandaten/', str(row['organization_id']) + 'eredienstbestuursorganen/2017/Lid')
                #person_lid_mandaat, person_lid_mandaat_uuid = concept_uri(lblod + 'mandaten/', str(row['organization_id']) + 'eredienstbestuursorganen/2020/Lid')
              
              #g.add((person_role_mandaat, ns.org.postIn, bestuur_temporary_17))
              #g.add((person_lid_mandaat, ns.org.postIn, bestuur_temporary_17))
              g.add((bestuur_temporary_17, ns.org.hasPost, person_role_mandaat))
              g.add((bestuur_temporary_17, ns.org.hasPost, person_lid_mandaat)) 
            else:
              person_role_mandaat, person_role_mandaat_uuid = concept_uri(lblod + 'mandaten/', str(row['organization_id']) + 'eredienstbestuursorganen/2020/' + role)
              person_lid_mandaat, person_lid_mandaat_uuid = concept_uri(lblod + 'mandaten/', str(row['organization_id']) + 'eredienstbestuursorganen/2020/Lid') 
              
              #g.add((person_role_mandaat, ns.org.postIn, bestuur_temporary_20))
              #g.add((person_lid_mandaat, ns.org.postIn, bestuur_temporary_20))
              g.add((bestuur_temporary_20, ns.org.hasPost, person_role_mandaat))
              g.add((bestuur_temporary_20, ns.org.hasPost, person_lid_mandaat)) 
          elif str(row['Status_EB Cleansed']) == 'Niet Actief':
            person_role_mandaat, person_role_mandaat_uuid = concept_uri(lblod + 'mandaten/', str(row['organization_id']) + 'eredienstbestuursorganen/2017/' + role)
            person_lid_mandaat, person_lid_mandaat_uuid = concept_uri(lblod + 'mandaten/', str(row['organization_id']) + 'eredienstbestuursorganen/2017/Lid') 
            #g.add((person_role_mandaat, ns.org.postIn, bestuur_temporary_17))
            g.add((bestuur_temporary_17, ns.org.hasPost, person_role_mandaat))
            g.add((bestuur_temporary_17, ns.org.hasPost, person_lid_mandaat)) 

          if person_role_mandaat != None:
            ## Role - Mandaat
            g.add((person_role_mandaat, RDF.type, ns.mandaat.Mandaat))
            add_literal(g, person_role_mandaat, ns.mu.uuid, person_role_mandaat_uuid, XSD.string)

            bestuurfunctie_id = get_concept_id(codelist_ere, get_label_role(role + ' worship'))
            g.add((person_role_mandaat, ns.org.role, bestuurfunctie_id))

            # Lid - Mandaat
            g.add((person_lid_mandaat, RDF.type, ns.mandaat.Mandaat))
            add_literal(g, person_lid_mandaat, ns.mu.uuid, person_lid_mandaat_uuid, XSD.string)

            bestuurfunctie_id = get_concept_id(codelist_ere, get_label_role('lid worship'))
            g.add((person_lid_mandaat, ns.org.role, bestuurfunctie_id))

            ## Role - Mandataris
            person_role_mandataris, person_role_mandataris_uuid = concept_uri(lblod + 'mandatarissen/', str(row['organization_id']) + person_uuid + role)
            #g.add((person_role_mandataris, RDF.type, ns.mandaat.Mandataris))
            g.add((person_role_mandataris, RDF.type, ns.ere.EredienstMandataris))
            add_literal(g, person_role_mandataris, ns.mu.uuid, person_role_mandataris_uuid, XSD.string)

            g.add((person_role_mandataris, ns.mandaat.isBestuurlijkeAliasVan, person_role))
            g.add((person_role_mandataris, ns.org.holds, person_role_mandaat))

            person_lid_mandataris, person_lid_mandataris_uuid = concept_uri(lblod + 'mandatarissen/', str(row['organization_id']) + person_uuid + 'lid')
            #g.add((person_lid_mandataris, RDF.type, ns.mandaat.Mandataris))
            g.add((person_lid_mandataris, RDF.type, ns.ere.EredienstMandataris))
            add_literal(g, person_lid_mandataris, ns.mu.uuid, person_lid_mandataris_uuid, XSD.string)

            g.add((person_lid_mandataris, ns.mandaat.isBestuurlijkeAliasVan, person_role))
            g.add((person_lid_mandataris, ns.org.holds, person_lid_mandaat))

            if str(row[f'Type Helft Cleansed {role}']) != str(np.nan):
              type_half = get_concept_id(codelist_ere, str(row[f'Type Helft Cleansed {role}']))
              g.add((person_lid_mandataris, ns.ere.typeHelft, type_half))

            g.add((person_role_mandataris, ns.mandaat.status, ns.mandataris_status['Effectief']))
            g.add((person_lid_mandataris, ns.mandaat.status, ns.mandataris_status['Effectief']))

            g.add((person_role, ns.mandaat.isAangesteldAls, person_role_mandataris))
            g.add((person_role, ns.mandaat.isAangesteldAls, person_lid_mandataris))
            
            #g.add((person_role_mandaat, ns.org.heldBy, person_role_mandataris))        
            #g.add((person_lid_mandaat, ns.org.heldBy, person_lid_mandataris))

            if str(row[f'Datum verkiezing {role}']) != 'NaT':
              add_literal(g, person_role_mandataris, ns.mandaat.start, dateparser.parse(str(row[f'Datum verkiezing {role}'])).isoformat(), XSD.dateTime)
              add_literal(g, person_lid_mandataris, ns.mandaat.start, dateparser.parse(str(row[f'Datum verkiezing {role}'])).isoformat(), XSD.dateTime)

              # possible end date = start date + 3 years
              year_election = dateparser.parse(str(row[f'Datum verkiezing {role}'])).year
              if year_election >= 2017 and year_election < 2020:
                remain_years = 2020 - year_election
                add_literal(g, person_role_mandataris, ns.ere.geplandeEinddatumAanstelling, (dateparser.parse(str(row[f'Datum verkiezing {role}'])) + timedelta(days=remain_years*365)).isoformat(), XSD.dateTime)
                add_literal(g, person_lid_mandataris, ns.ere.geplandeEinddatumAanstelling, (dateparser.parse(str(row[f'Datum verkiezing {role}'])) + timedelta(days=remain_years*365)).isoformat(), XSD.dateTime)
                add_literal(g, person_role_mandataris, ns.mandaat.einde, (dateparser.parse(str(row[f'Datum verkiezing {role}'])) + timedelta(days=remain_years*365)).isoformat(), XSD.dateTime)
                add_literal(g, person_lid_mandataris, ns.mandaat.einde, (dateparser.parse(str(row[f'Datum verkiezing {role}'])) + timedelta(days=remain_years*365)).isoformat(), XSD.dateTime)
              else:
                add_literal(g, person_role_mandataris, ns.ere.geplandeEinddatumAanstelling, (dateparser.parse(str(row[f'Datum verkiezing {role}'])) + timedelta(days=3*365)).isoformat(), XSD.dateTime)
                add_literal(g, person_lid_mandataris, ns.ere.geplandeEinddatumAanstelling, (dateparser.parse(str(row[f'Datum verkiezing {role}'])) + timedelta(days=3*365)).isoformat(), XSD.dateTime)
              
            ### Mandataris - Contact punt
            if exists_contact_role(row, role):
              person_role_contact_uri, person_role_contact_uuid = concept_uri(lblod + 'contact-punten/', str(row['organization_id']) + person_uuid + role + str(row[f'Tel_{role} 1']))
              g.add((person_role_contact_uri, RDF.type, ns.schema.ContactPoint))
              add_literal(g, person_role_contact_uri, ns.mu.uuid, person_role_contact_uuid, XSD.string)
              g.add((person_role_mandataris, ns.schema.contactPoint, person_role_contact_uri))

              add_literal(g, person_role_contact_uri, ns.schema.telephone, str(row[f'Tel_{role} 1']), XSD.string)
              add_literal(g, person_role_contact_uri, ns.schema.email, str(row[f'Mail_{role} Cleansed']), XSD.string)

              if str(row[f'Tel_{role} 2']) != str(np.nan):
                person_role_contact_2_uri, person_role_contact_2_uuid = concept_uri(lblod + 'contact-punten/', str(row['organization_id']) + person_uuid + role + str(row[f'Tel_{role} 2']))
                g.add((person_role_contact_2_uri, RDF.type, ns.schema.ContactPoint))
                add_literal(g, person_role_contact_2_uri, ns.mu.uuid, person_role_contact_2_uuid, XSD.string)

                add_literal(g, person_role_contact_2_uri, ns.schema.telephone, str(row[f'Tel_{role} 2']), XSD.string)
                g.add((person_role_mandataris, ns.schema.contactPoint, person_role_contact_2_uri))

              ### Role - Adres
              if exists_address_role(row, role):
                person_role_address_id, person_role_address_uuid = concept_uri(lblod + 'adressen/', str(row['organization_id']) + person_uuid + role + 'adressen') 
                g.add((person_role_address_id, RDF.type, ns.locn.Address))
                add_literal(g, person_role_address_id, ns.mu.uuid, person_role_address_uuid, XSD.string)

                g.add((person_role_contact_uri, ns.locn.address, person_role_address_id))
                add_literal(g, person_role_address_id, ns.locn.fullAddress, str(row[f'Adres_{role} Cleansed']), XSD.string)

      ####
      # Lids
      for role in roles_lid:
        if exists_role_worship(row, role):
          if exists_given_and_family_name(row, role):
            lid, lid_uuid =  concept_uri(lblod + 'personen/', str(row[f'Naam_{role} First']) + str(row[f'Naam_{role} Last']))
            add_literal(g, lid, FOAF.givenName, str(row[f'Naam_{role} First']), XSD.string)
            add_literal(g, lid, FOAF.familyName, str(row[f'Naam_{role} Last']), XSD.string)
          else:
            lid, lid_uuid =  concept_uri(lblod + 'personen/', str(row[f'Naam_{role} Cleansed']))
            add_literal(g, lid, FOAF.givenName, str(row[f'Naam_{role} Cleansed']), XSD.string)
          
          g.add((lid, RDF.type, ns.person.Person))
          add_literal(g, lid, ns.mu.uuid, lid_uuid, XSD.string)

          ## Lid - Mandaat
          lid_mandaat = None
          if str(row[f'Datum verkiezing {role}']) != 'NaT':
            year_election = dateparser.parse(str(row[f'Datum verkiezing {role}'])).year
            
            if year_election <= 2019:
              # if str(row[f'Type Helft Cleansed {role}']) == 'Kleine helft':
              #   lid_mandaat, lid_mandaat_uuid = concept_uri(lblod + 'mandaten/', str(row['organization_id']) + 'eredienstbestuursorganen/2017/Lid')
              # else:
              #   lid_mandaat, lid_mandaat_uuid = concept_uri(lblod + 'mandaten/', str(row['organization_id']) + 'eredienstbestuursorganen/2020/Lid')

              #g.add((lid_mandaat, ns.org.postIn, bestuur_temporary_17))
              lid_mandaat, lid_mandaat_uuid = concept_uri(lblod + 'mandaten/', str(row['organization_id']) + 'eredienstbestuursorganen/2017/Lid')
              g.add((bestuur_temporary_17, ns.org.hasPost, lid_mandaat)) 
            else:
              lid_mandaat, lid_mandaat_uuid = concept_uri(lblod + 'mandaten/', str(row['organization_id']) + 'eredienstbestuursorganen/2020/Lid')
              #g.add((lid_mandaat, ns.org.postIn, bestuur_temporary_20))
              g.add((bestuur_temporary_20, ns.org.hasPost, lid_mandaat))              
          elif str(row['Status_EB Cleansed']) == 'Niet Actief':
            lid_mandaat, lid_mandaat_uuid = concept_uri(lblod + 'mandaten/', str(row['organization_id']) + 'eredienstbestuursorganen/2017/Lid') 
            #g.add((lid_mandaat, ns.org.postIn, bestuur_temporary_17))
            g.add((bestuur_temporary_17, ns.org.hasPost, lid_mandaat))
          
          if lid_mandaat != None:
            g.add((lid_mandaat, RDF.type, ns.mandaat.Mandaat))
            add_literal(g, lid_mandaat, ns.mu.uuid, lid_mandaat_uuid, XSD.string)

            bestuurfunctie_id = get_concept_id(codelist_ere, get_label_role('lid worship'))
            g.add((lid_mandaat, ns.org.role, bestuurfunctie_id))

            ## Lid - Mandataris
            lid_mandataris, lid_mandataris_uuid = concept_uri(lblod + 'mandatarissen/', str(row['organization_id']) + person_uuid + role)
            #g.add((lid_mandataris, RDF.type, ns.mandaat.Mandataris))
            g.add((lid_mandataris, RDF.type, ns.ere.EredienstMandataris))
            add_literal(g, lid_mandataris, ns.mu.uuid, lid_mandataris_uuid, XSD.string)

            g.add((lid_mandataris, ns.mandaat.isBestuurlijkeAliasVan, lid))
            g.add((lid_mandataris, ns.org.holds, lid_mandaat))

            if str(row[f'Type Helft Cleansed {role}']) != str(np.nan):
              type_half = get_concept_id(codelist_ere, str(row[f'Type Helft Cleansed {role}']))
              g.add((lid_mandataris, ns.ere.typeHelft, type_half))

            if str(row[f'Datum verkiezing {role}']) != 'NaT':
              add_literal(g, lid_mandataris, ns.mandaat.start, dateparser.parse(str(row[f'Datum verkiezing {role}'])).isoformat(), XSD.dateTime)
              add_literal(g, person_role_mandataris, ns.ere.geplandeEinddatumAanstelling, (dateparser.parse(str(row[f'Datum verkiezing {role}'])) + timedelta(days=1095)).isoformat(), XSD.dateTime)

            g.add((lid_mandaat, ns.org.heldBy, lid_mandataris))
            g.add((lid, ns.mandaat.isAangesteldAls, lid_mandataris))

  print("########### Mapping finished #############")

  export_data(g, f'worship-{mode}')
  