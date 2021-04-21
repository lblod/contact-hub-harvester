import pandas as pd
import numpy as np
from rdflib import Graph, Literal, RDF
from rdflib.namespace import FOAF , XSD, DC, SKOS, RDF

import cleansing.organization as cls_org
from helper.functions import add_literal, concept_uri, export_data, export_df, exists_site_org, exists_contact_org, exists_address
import helper.namespaces as ns

def create_status_uri(g, data):
  for status in data['Organisatiestatus'].dropna().unique():
    subject, _ = concept_uri(ns.os, status)
    g.add((subject, RDF.type, SKOS.Concept))
    g.add((subject, SKOS.prefLabel, Literal(status, lang='nl')))
    if status.startswith('Actief') or status.startswith('Valt Niet Meer'):
      g.add((subject, SKOS.broader, ns.os.actief))
    else:
      g.add((subject, SKOS.broader, ns.os.nietactief))

def create_category_uri(g, data):
  for category in data['Type Entiteit'].dropna().unique():
    category, _ = concept_uri(ns.oc, category)
    g.add((category, RDF.type, SKOS.Concept))
    g.add((category, SKOS.prefLabel, Literal(category, lang='nl')))

def main(file): 
  org_raw = pd.read_excel(file)
  orgs_cleansed = cls_org.main(org_raw)

  export_df(orgs_cleansed, 'org')

  g = Graph()

  create_status_uri(g, orgs_cleansed)
  create_category_uri(g, orgs_cleansed)
  
  for _, row in orgs_cleansed.iterrows():
    abb_id, abb_uuid = concept_uri(ns.lblod + 'organisatie/', str(row['organisation_id']))
    g.add((abb_id, RDF.type, ns.org.Organization))
    add_literal(g, abb_id, ns.mu.uuid, abb_uuid, XSD.string)

    add_literal(g, abb_id, ns.regorg.legalName, str(row['Maatschappelijke Naam']))
    add_literal(g, abb_id, SKOS.prefLabel, str(row['Titel']))

    classification, _ = concept_uri(ns.oc, row['Type Entiteit'])
    g.add((abb_id, ns.org.classification, classification))

    status, _ = concept_uri(ns.os, str(row['Organisatiestatus']))
    g.add((abb_id, ns.regorg.orgStatus, status))

    add_literal(g, abb_id, ns.dbpedia.nisCode, str(row['NIScode_cleansed']), XSD.string)

    if str(row['KBOnr_cleansed']) != str(np.nan):
      kbo_id, _ = concept_uri(ns.lblod + 'gestructureerdeIdentificator/', str(row['organisation_id']) + str(row['KBOnr_cleansed']))
      g.add((kbo_id, RDF.type, ns.generiek.GestructureerdeIdentificator))
      add_literal(g, kbo_id, ns.generiek.lokaleIdentificator, str(row['KBOnr_cleansed']), XSD.string)

      g.add((abb_id, ns.generiek.gestructureerdeIdentificator, kbo_id))
    
    if str(row['Unieke Naam']) != str(np.nan):
      unieke_naam_id, _ = concept_uri(ns.lblod + 'gestructureerdeIdentificator/', str(row['organisation_id']) + str(row['Unieke Naam']) + '1')
      g.add((unieke_naam_id, RDF.type, ns.generiek.GestructureerdeIdentificator))
      add_literal(g, unieke_naam_id, ns.generiek.lokaleIdentificator, str(row['Unieke Naam']), XSD.string)

      g.add((abb_id, ns.generiek.gestructureerdeIdentificator, unieke_naam_id))

    if str(row['Unieke Naam van actieve organisaties']) != str(np.nan):
      unieke_naam_active_id, _ = concept_uri(ns.lblod + 'gestructureerdeIdentificator/', str(row['organisation_id']) + str(row['Unieke Naam van actieve organisaties']) + '2')
      g.add((unieke_naam_active_id, RDF.type, ns.generiek.GestructureerdeIdentificator))
      add_literal(g, unieke_naam_active_id, ns.generiek.lokaleIdentificator, str(row['Unieke Naam van actieve organisaties']), XSD.string)

      g.add((abb_id, ns.generiek.gestructureerdeIdentificator, unieke_naam_id))

    if exists_site_org(row):
      site_id, _ = concept_uri(ns.lblod + 'vesting/', str(row['organisation_id']))
      g.add((site_id, RDF.type, ns.org.Site))

      if exists_contact_org(row):
        contact_id, _ = concept_uri(ns.lblod + 'contactinfo/', str(row['organisation_id']))
        g.add((contact_id, RDF.type, ns.schema.ContactPoint))
        
        add_literal(g, contact_id, FOAF.page, str(row['Website Cleansed']), XSD.anyURI)
        add_literal(g, contact_id, ns.schema.telephone, str(row['Algemeen telefoonnr']), XSD.string)
        add_literal(g, contact_id, ns.schema.email, str(row['Algemeen mailadres']), XSD.string)

        g.add((site_id, ns.schema.siteAddress, contact_id))

      if exists_address(row):
        address_id, _ = concept_uri(ns.lblod + 'adresvoorstelling/', str(row['organisation_id']))
        g.add((address_id, RDF.type, ns.locn.Address))
        add_literal(g, address_id, ns.locn.thoroughfare, str(row['Straat']))
        add_literal(g, address_id, ns.adres['Adresvoorstelling.huisnummer'], str(row['Huisnr_cleansed']), XSD.string)
        add_literal(g, address_id, ns.adres['Adresvoorstelling.busnummer'], str(row['Busnr_new']), XSD.string)
        add_literal(g, address_id, ns.locn.postCode, str(row['Postcode van de organisatie_cleansed']), XSD.string)
        add_literal(g, address_id, ns.adres.gemeentenaam, str(row['Gemeente van de organisatie']))
        add_literal(g, address_id, ns.locn.adminUnitL2, str(row['Provincie Cleansed']))
        g.add((address_id, ns.adres.land, Literal('België', lang='nl')))

        g.add((site_id, ns.organisatie.bestaatUit, address_id))
      
      g.add((abb_id, ns.org.hasPrimarySite, site_id))

    if row['Unieke Naam'] != row['Moederentiteit']:
      find_moeder_kboid = orgs_cleansed[orgs_cleansed['Unieke Naam'] == row['Moederentiteit']]
      if len(find_moeder_kboid) > 0:
        org_id, _ = concept_uri(ns.lblod + 'organisatie/', str(find_moeder_kboid.iloc[0]['organisation_id']))
        g.add((abb_id, ns.org.linkedTo, org_id))

    if pd.notna(row['Actief vanaf']):
      change_event_open_id, _ = concept_uri(ns.lblod + 'veranderingsgebeurtenis/', str(row['organisation_id']) + str(row['Actief vanaf']))
      g.add((change_event_open_id, RDF.type, ns.organisatie.Oprichting))
      add_literal(g, change_event_open_id, DC.date, str(row['Actief vanaf']), XSD.dateTime)
      g.add((abb_id, ns.org.resultedFrom, change_event_open_id))

    if row['Organisatiestatus'] == 'Valt niet meer onder Vlaams toezicht':
      change_event_not_flemish_id, _ = concept_uri(ns.lblod + 'veranderingsgebeurtenis/', str(row['organisation_id']) + str(row['Actief tot']) + str(row['Actief tot']))
      g.add((change_event_not_flemish_id, RDF.type, ns.organisatie.Vervanging))
      g.add((abb_id, ns.org.resultedFrom, change_event_not_flemish_id))

    elif row['Organisatiestatus'] == 'Gefusioneerd':
      change_event_merged_id, _ = concept_uri(ns.lblod + 'veranderingsgebeurtenis/', str(row['organisation_id']) + str(row['Actief tot']))
      g.add((change_event_merged_id, RDF.type, ns.organisatie.Fusie))
      if pd.notna(row['Actief tot']):
        add_literal(g, change_event_merged_id, DC.date, str(row['Actief tot']), XSD.dateTime)
      # addLiteral(change_event_merged_id, NEED PROPERTY, 'Opmerkingen ivm Organisatie')
    
      merged_abb_id, _ = concept_uri(ns.lblod + 'organisatie/', str(row['Resulting organisation']))
      g.add((change_event_merged_id, ns.org.originalOrganization, abb_id))
      g.add((change_event_merged_id, ns.org.resultingOrganization, merged_abb_id))
      g.add((abb_id, ns.org.changedBy, change_event_merged_id))

    elif pd.notna(row['Actief tot']):
      change_event_close_id, _ = concept_uri(ns.lblod + 'veranderingsgebeurtenis/', str(row['organisation_id']) + str(row['Actief tot']))
      g.add((change_event_close_id, RDF.type, ns.organisatie.Stopzetting))
      add_literal(g, change_event_close_id, DC.date, str(row['Actief tot']), XSD.dateTime)
      g.add((abb_id, ns.org.changedBy, change_event_close_id))
  
  export_data(g, 'org-dev')