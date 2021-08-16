import json
import numpy as np
from datetime import datetime, timedelta
import dateparser
from rdflib import Graph, URIRef
from rdflib.namespace import FOAF, XSD, SKOS, RDF, RDFS, DCTERMS

from helper.functions import add_literal, concept_uri, exists_bestuursperiode_worship, exists_role_worship, export_data, get_cleansed_data, exists_address, exists_address_role, exists_contact_role, exists_bestuursperiode_worship, get_adm_unit_concept, get_location_id, load_graph, get_concept_id, get_label_role, exists_given_and_family_name, get_full_address, shuffle_word
import helper.namespaces as ns


def main(file, mode): 
  worship_cleansed = get_cleansed_data(file, 'worship')

  lblod = ns.get_namespace(mode)

  g = Graph()
  codelist_ere = load_graph('codelist-ere')
  codelist_bestuurseenheid = load_graph('bestuurseenheid-classificatie-code')
  locations = load_graph('locations')
  worship_bestuurseenheid_classification_id = get_concept_id(codelist_bestuurseenheid, 'Bestuur van de eredienst')
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

    g.add((abb_id, ns.org.classification, worship_bestuurseenheid_classification_id))

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

    if str(row['Titel']) != str(np.nan):
      id_class, id_uuid = concept_uri(lblod +'identificatoren/', str(row['Titel']) + 'identificatoren')
      g.add((id_class, RDF.type, ns.adms.Identifier))
      add_literal(g, id_class, SKOS.notation, 'SharePoint identificator', XSD.string)
      add_literal(g, id_class, ns.mu.uuid, id_uuid, XSD.string)

      naam_uri, naam_uuid = concept_uri(lblod + 'gestructureerdeIdentificator/', str(row['Titel']) + 'gestructureerdeIdentificator')
      g.add((naam_uri, RDF.type, ns.generiek.GestructureerdeIdentificator))
      add_literal(g, naam_uri, ns.mu.uuid, naam_uuid, XSD.string)
      add_literal(g, naam_uri, ns.generiek.lokaleIdentificator, str(row['Titel']), XSD.string)
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
          g.add((municipality_adminunit, ns.org.classification, URIRef(municipality_res['classificatie']['value'])))
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
          g.add((province_adminunit, ns.org.classification, URIRef(province_res['classificatie']['value'])))
          add_literal(g, province_adminunit, SKOS.prefLabel, province, XSD.string)
          add_literal(g, province_adminunit, ns.mu.uuid, province_res['uuid']['value'], XSD.string)
      
      if len(local_eng['Cross-Border']) == 1 and local_eng['Municipality']:          
        gemeente_id = get_location_id(locations, local_eng['Cross-Border'][0], 'Gemeente')
        if gemeente_id != None:
          g.add((abb_id, ns.besluit.werkingsgebied, gemeente_id))
      elif len(local_eng['Cross-Border']) == 1 and local_eng['Province']:
        provincie_id = get_location_id(locations, local_eng['Cross-Border'][0], 'Provincie')
        if provincie_id != None:
          g.add((abb_id, ns.besluit.werkingsgebied, provincie_id))
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

    roles = ['voorzitter', 'secretaris', 'penningmeester', 'Lid4', 'Lid5']
  
    if exists_bestuursperiode_worship(row, roles):
      # Bestuursorgaan (in bestuursperiode)
      start_date_bestuur_temporary_17 = None
      end_date_bestuur_temporary_17 = None
      start_date_bestuur_temporary_20 = None
      end_date_bestuur_temporary_20 = None

      if str(row['Verkiezingen17_Opmerkingen Cleansed']) != str(np.nan):
        start_date_bestuur_temporary_17 = dateparser.parse(str(row['Verkiezingen17_Opmerkingen Cleansed']))

      if str(row['Verkiezingen2020_Opmerkingen Cleansed']) != str(np.nan):
        start_date_bestuur_temporary_20 = dateparser.parse(str(row['Verkiezingen2020_Opmerkingen Cleansed']))

      if bool(row['Verkiezingen17']) == True:
        # Bestuursorgaan in bestuursperiode 2017-2020
        bestuur_temporary_17, bestuur_temporary_17_uuid = concept_uri(lblod + 'eredienstbestuursorganen/', str(row['organization_id']) + 'eredienstbestuursorganen/2017')
        g.add((bestuur_temporary_17, RDF.type, ns.besluit.Bestuursorgaan))
        #g.add((bestuur_temporary_17, RDF.type, ns.ere.Eredienstbestuursorgaan))

        add_literal(g, bestuur_temporary_17, ns.mu.uuid, bestuur_temporary_17_uuid, XSD.string)
        g.add((bestuur_temporary_17, ns.generiek.isTijdspecialisatieVan, bo_id))
        
        # start date of governing body temporary 2017
        if start_date_bestuur_temporary_17 != None:
          add_literal(g, bestuur_temporary_17, ns.mandaat.bindingStart, start_date_bestuur_temporary_17.isoformat(), XSD.dateTime)
        
        # end date of governing body temporary 2017
        if start_date_bestuur_temporary_20 != None:
          end_date_bestuur_temporary_17 = start_date_bestuur_temporary_20        
          print("from 2017", end_date_bestuur_temporary_17)
          add_literal(g, bestuur_temporary_17, ns.mandaat.bindingEinde, end_date_bestuur_temporary_17.isoformat(), XSD.dateTime)
          
        elif start_date_bestuur_temporary_17 != None:
          remain_years = 2020 - start_date_bestuur_temporary_17.year
          print(remain_years)
          end_date_bestuur_temporary_17 = (start_date_bestuur_temporary_17 + timedelta(days=remain_years*365)).isoformat()
          print("from 2020", end_date_bestuur_temporary_17)
          add_literal(g, bestuur_temporary_20, ns.mandaat.bindingEinde, end_date_bestuur_temporary_17, XSD.dateTime)


      if str(row['Status_EB Cleansed']) == 'Actief':
        # Bestuursorgaan in bestuursperiode 2020-2023
        bestuur_temporary_20, bestuur_temporary_20_uuid = concept_uri(lblod + 'eredienstbestuursorganen/', str(row['organization_id']) + 'eredienstbestuursorganen/2020')
        g.add((bestuur_temporary_20, RDF.type, ns.besluit.Bestuursorgaan))
        #g.add((bestuur_temporary_20, RDF.type, ns.ere.Eredienstbestuursorgaan))
        add_literal(g, bestuur_temporary_20, ns.mu.uuid, bestuur_temporary_20_uuid, XSD.string)
        g.add((bestuur_temporary_20, ns.generiek.isTijdspecialisatieVan, bo_id))
        
        if start_date_bestuur_temporary_20 != None:
          add_literal(g, bestuur_temporary_20, ns.mandaat.bindingStart, start_date_bestuur_temporary_20, XSD.dateTime)
      
        # From 2023 the next bestuursorgaan in bestuursperiode will begin the same day
        if str(row['Type_eredienst Cleansed']) == 'Israëlitisch':
          end_date_bestuur_temporary_20 = datetime(2023, 5, 31).isoformat()
          add_literal(g, bestuur_temporary_20, ns.mandaat.bindingEinde, end_date_bestuur_temporary_20, XSD.dateTime)
        else:
          end_date_bestuur_temporary_20 = datetime(2023, 4, 30).isoformat()
          add_literal(g, bestuur_temporary_20, ns.mandaat.bindingEinde, end_date_bestuur_temporary_20, XSD.dateTime)

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
         
          if str(row[f'Datum verkiezing {role}']) != 'NaT':
            year_election = dateparser.parse(str(row[f'Datum verkiezing {role}'])).year
            
            if year_election <= 2019:
              if not 'Lid' in role:
                person_role_mandaat, person_role_mandaat_uuid = concept_uri(lblod + 'mandaten/', str(row['organization_id']) + 'eredienstbestuursorganen/2017/' + role)
                g.add((bestuur_temporary_17, ns.org.hasPost, person_role_mandaat))
              person_lid_mandaat, person_lid_mandaat_uuid = concept_uri(lblod + 'mandaten/', str(row['organization_id']) + 'eredienstbestuursorganen/2017/Lid')             
              g.add((bestuur_temporary_17, ns.org.hasPost, person_lid_mandaat)) 

              #if str(row[f'Type Helft Cleansed {role}']) == 'Kleine helft':
                #person_lid_mandaat, person_lid_mandaat_uuid = concept_uri(lblod + 'mandaten/', str(row['organization_id']) + 'eredienstbestuursorganen/2017/Lid')
                #person_lid_mandaat, person_lid_mandaat_uuid = concept_uri(lblod + 'mandaten/', str(row['organization_id']) + 'eredienstbestuursorganen/2020/Lid')
            else:
              if not 'Lid' in role:
                person_role_mandaat, person_role_mandaat_uuid = concept_uri(lblod + 'mandaten/', str(row['organization_id']) + 'eredienstbestuursorganen/2020/' + role)
                g.add((bestuur_temporary_20, ns.org.hasPost, person_role_mandaat))
              
              person_lid_mandaat, person_lid_mandaat_uuid = concept_uri(lblod + 'mandaten/', str(row['organization_id']) + 'eredienstbestuursorganen/2020/Lid')
              g.add((bestuur_temporary_20, ns.org.hasPost, person_lid_mandaat))  
          
          elif str(row['Status_EB Cleansed']) == 'Niet Actief':
            if not 'Lid' in role:
              person_role_mandaat, person_role_mandaat_uuid = concept_uri(lblod + 'mandaten/', str(row['organization_id']) + 'eredienstbestuursorganen/2017/' + role)
              g.add((bestuur_temporary_17, ns.org.hasPost, person_role_mandaat))

            person_lid_mandaat, person_lid_mandaat_uuid = concept_uri(lblod + 'mandaten/', str(row['organization_id']) + 'eredienstbestuursorganen/2017/Lid')             
            g.add((bestuur_temporary_17, ns.org.hasPost, person_lid_mandaat)) 

          if person_role_mandaat != None:
            start_mandataris = None
            expected_end_mandataris = None
            end_mandataris = None

            if str(row[f'Datum verkiezing {role}']) != 'NaT':
              start_mandataris = dateparser.parse(str(row[f'Datum verkiezing {role}']))

            year_election = dateparser.parse(str(row[f'Datum verkiezing {role}'])).year
            if year_election >= 2017 and year_election < 2020 and end_date_bestuur_temporary_17 != None:
              expected_end_mandataris = end_date_bestuur_temporary_17
              end_mandataris = expected_end_mandataris
            elif end_date_bestuur_temporary_17 == None:
              remain_years = 2020 - year_election
              expected_end_mandataris = (start_mandataris + timedelta(days=remain_years*365)).isoformat()
              end_mandataris = expected_end_mandataris
            elif end_date_bestuur_temporary_20 != None:
              expected_end_mandataris = end_date_bestuur_temporary_20
        
            if 'Lid' not in role:
              ## Role - Mandaat
              g.add((person_role_mandaat, RDF.type, ns.mandaat.Mandaat))
              add_literal(g, person_role_mandaat, ns.mu.uuid, person_role_mandaat_uuid, XSD.string)

              bestuurfunctie_id = get_concept_id(codelist_ere, get_label_role(role + ' worship'))
              g.add((person_role_mandaat, ns.org.role, bestuurfunctie_id))

              ## Role - Mandataris
              person_role_mandataris, person_role_mandataris_uuid = concept_uri(lblod + 'mandatarissen/', str(row['organization_id']) + person_uuid + role)
              #g.add((person_role_mandataris, RDF.type, ns.mandaat.Mandataris))
              g.add((person_role_mandataris, RDF.type, ns.ere.EredienstMandataris))
              add_literal(g, person_role_mandataris, ns.mu.uuid, person_role_mandataris_uuid, XSD.string)

              g.add((person_role_mandataris, ns.mandaat.isBestuurlijkeAliasVan, person_role))
              g.add((person_role_mandataris, ns.org.holds, person_role_mandaat))
            
              g.add((person_role_mandataris, ns.mandaat.status, ns.mandataris_status['Effectief']))
              g.add((person_role, ns.mandaat.isAangesteldAls, person_role_mandataris))

              if start_mandataris != None:
                add_literal(g, person_role_mandataris, ns.mandaat.start, start_mandataris, XSD.dateTime)

              if expected_end_mandataris != None:
                add_literal(g, person_role_mandataris, ns.ere.geplandeEinddatumAanstelling, expected_end_mandataris, XSD.dateTime)

              if end_mandataris != None:
                add_literal(g, person_role_mandataris, ns.mandaat.einde, end_mandataris, XSD.dateTime)
                
            # Lid - Mandaat
            g.add((person_lid_mandaat, RDF.type, ns.mandaat.Mandaat))
            add_literal(g, person_lid_mandaat, ns.mu.uuid, person_lid_mandaat_uuid, XSD.string)

            bestuurfunctie_id = get_concept_id(codelist_ere, get_label_role('lid worship'))
            g.add((person_lid_mandaat, ns.org.role, bestuurfunctie_id))

            person_lid_mandataris, person_lid_mandataris_uuid = concept_uri(lblod + 'mandatarissen/', str(row['organization_id']) + person_uuid + 'lid')
            #g.add((person_lid_mandataris, RDF.type, ns.mandaat.Mandataris))
            g.add((person_lid_mandataris, RDF.type, ns.ere.EredienstMandataris))
            add_literal(g, person_lid_mandataris, ns.mu.uuid, person_lid_mandataris_uuid, XSD.string)

            g.add((person_lid_mandataris, ns.mandaat.isBestuurlijkeAliasVan, person_role))
            g.add((person_lid_mandataris, ns.org.holds, person_lid_mandaat))

            if str(row[f'Type Helft Cleansed {role}']) != str(np.nan):
              type_half = get_concept_id(codelist_ere, str(row[f'Type Helft Cleansed {role}']))
              g.add((person_lid_mandataris, ns.ere.typeHelft, type_half))

            g.add((person_lid_mandataris, ns.mandaat.status, ns.mandataris_status['Effectief']))
            g.add((person_role, ns.mandaat.isAangesteldAls, person_lid_mandataris))
  
            if start_mandataris != None:
              add_literal(g, person_lid_mandataris, ns.mandaat.start, start_mandataris, XSD.dateTime)

            if expected_end_mandataris != None:                
              add_literal(g, person_lid_mandataris, ns.ere.geplandeEinddatumAanstelling, expected_end_mandataris, XSD.dateTime)
          
            if end_mandataris != None:
              add_literal(g, person_lid_mandataris, ns.mandaat.einde, end_mandataris, XSD.dateTime)
               
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
      # for role in roles_lid:
      #   if exists_role_worship(row, role):
      #     if exists_given_and_family_name(row, role):
      #       lid, lid_uuid =  concept_uri(lblod + 'personen/', str(row[f'Naam_{role} First']) + str(row[f'Naam_{role} Last']))
      #       add_literal(g, lid, FOAF.givenName, str(row[f'Naam_{role} First']), XSD.string)
      #       add_literal(g, lid, FOAF.familyName, str(row[f'Naam_{role} Last']), XSD.string)
      #     else:
      #       lid, lid_uuid =  concept_uri(lblod + 'personen/', str(row[f'Naam_{role} Cleansed']))
      #       add_literal(g, lid, FOAF.givenName, str(row[f'Naam_{role} Cleansed']), XSD.string)
          
      #     g.add((lid, RDF.type, ns.person.Person))
      #     add_literal(g, lid, ns.mu.uuid, lid_uuid, XSD.string)

      #     ## Lid - Mandaat
      #     #lid_mandaat = None
      #     if str(row[f'Datum verkiezing {role}']) != 'NaT':
      #       year_election = dateparser.parse(str(row[f'Datum verkiezing {role}'])).year
            
      #       if person_lid_mandaat != None:
      #         if year_election <= 2019:
      #         if str(row[f'Type Helft Cleansed {role}']) == 'Kleine helft':
      #           lid_mandaat, lid_mandaat_uuid = concept_uri(lblod + 'mandaten/', str(row['organization_id']) + 'eredienstbestuursorganen/2017/Lid')
      #         else:
      #           lid_mandaat, lid_mandaat_uuid = concept_uri(lblod + 'mandaten/', str(row['organization_id']) + 'eredienstbestuursorganen/2020/Lid')

      #         g.add((lid_mandaat, ns.org.postIn, bestuur_temporary_17))
      #         lid_mandaat, lid_mandaat_uuid = concept_uri(lblod + 'mandaten/', str(row['organization_id']) + 'eredienstbestuursorganen/2017/Lid')
      #           g.add((bestuur_temporary_17, ns.org.hasPost, person_lid_mandaat))
      #         else:
      #           g.add((bestuur_temporary_20, ns.org.hasPost, person_lid_mandaat)) 
      #       elif person_lid_mandaat == None and year_election <= 2019:
      #         person_lid_mandaat, person_lid_mandaat_uuid = concept_uri(lblod + 'mandaten/', str(row['organization_id']) + 'eredienstbestuursorganen/2017/Lid')
      #         g.add((bestuur_temporary_20, ns.org.hasPost, person_lid_mandaat))
      #       else:
      #         person_lid_mandaat, person_lid_mandaat_uuid = concept_uri(lblod + 'mandaten/', str(row['organization_id']) + 'eredienstbestuursorganen/2020/Lid')
      #         g.add((bestuur_temporary_20, ns.org.hasPost, person_lid_mandaat))
      #     elif str(row['Status_EB Cleansed']) == 'Niet Actief':
      #       #lid_mandaat, lid_mandaat_uuid = concept_uri(lblod + 'mandaten/', str(row['organization_id']) + 'eredienstbestuursorganen/2017/Lid') 
      #       #g.add((lid_mandaat, ns.org.postIn, bestuur_temporary_17))
      #       g.add((bestuur_temporary_17, ns.org.hasPost, person_lid_mandaat))
          
      #     # if lid_mandaat != None:
      #     #   g.add((lid_mandaat, RDF.type, ns.mandaat.Mandaat))
      #     #   add_literal(g, lid_mandaat, ns.mu.uuid, lid_mandaat_uuid, XSD.string)

      #       # bestuurfunctie_id = get_concept_id(codelist_ere, get_label_role('lid worship'))
      #       # g.add((lid_mandaat, ns.org.role, bestuurfunctie_id))

      #     ## Lid - Mandataris
      #     lid_mandataris, lid_mandataris_uuid = concept_uri(lblod + 'mandatarissen/', str(row['organization_id']) + lid_uuid + role)
      #     #g.add((lid_mandataris, RDF.type, ns.mandaat.Mandataris))
      #     g.add((lid_mandataris, RDF.type, ns.ere.EredienstMandataris))
      #     add_literal(g, lid_mandataris, ns.mu.uuid, lid_mandataris_uuid, XSD.string)

      #     g.add((lid_mandataris, ns.mandaat.isBestuurlijkeAliasVan, lid))
      #     g.add((lid_mandataris, ns.org.holds, person_lid_mandaat))

      #     if str(row[f'Type Helft Cleansed {role}']) != str(np.nan):
      #       type_half = get_concept_id(codelist_ere, str(row[f'Type Helft Cleansed {role}']))
      #       g.add((lid_mandataris, ns.ere.typeHelft, type_half))

      #     if str(row[f'Datum verkiezing {role}']) != 'NaT':
      #       add_literal(g, lid_mandataris, ns.mandaat.start, dateparser.parse(str(row[f'Datum verkiezing {role}'])).isoformat(), XSD.dateTime)
      #       add_literal(g, person_role_mandataris, ns.ere.geplandeEinddatumAanstelling, (dateparser.parse(str(row[f'Datum verkiezing {role}'])) + timedelta(days=1095)).isoformat(), XSD.dateTime)

      #     #g.add((lid_mandaat, ns.org.heldBy, lid_mandataris))
      #     g.add((lid, ns.mandaat.isAangesteldAls, lid_mandataris))

    elif str(row['Status_EB Cleansed']) == 'Actief':
      # Bestuursorgaan in bestuursperiode 2020-2023
      bestuur_temporary_20, bestuur_temporary_20_uuid = concept_uri(lblod + 'eredienstbestuursorganen/', str(row['organization_id']) + 'eredienstbestuursorganen/2020')
      g.add((bestuur_temporary_20, RDF.type, ns.besluit.Bestuursorgaan))
      #g.add((bestuur_temporary_20, RDF.type, ns.ere.Eredienstbestuursorgaan))
      add_literal(g, bestuur_temporary_20, ns.mu.uuid, bestuur_temporary_20_uuid, XSD.string)
      g.add((bestuur_temporary_20, ns.generiek.isTijdspecialisatieVan, bo_id))

       # From 2023 the next bestuursorgaan in bestuursperiode will begin the same day
      if str(row['Type_eredienst Cleansed']) == 'Israëlitisch':
        add_literal(g, bestuur_temporary_20, ns.mandaat.bindingEinde, datetime(2023, 5, 31).isoformat(), XSD.dateTime)
      else:
        add_literal(g, bestuur_temporary_20, ns.mandaat.bindingEinde, datetime(2023, 4, 30).isoformat(), XSD.dateTime)


  print("########### Mapping finished #############")

  export_data(g, f'worship-{mode}')
  