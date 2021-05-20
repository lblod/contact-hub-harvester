import pandas as pd
import numpy as np
from datetime import datetime
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import FOAF , XSD, FOAF, RDF, RDFS

import cleansing.contact as cls_contact
from helper.functions import add_literal, concept_uri, export_data, exists_contact_cont, get_cleansed_data, load_graph, get_concept_id
import helper.namespaces as ns

def main(file, mode):
  contact_cleansed = get_cleansed_data(file, 'contact')

  lblod = ns.get_namespace(mode)
  codelist_bestuursfunctie = load_graph('bestuursfunctie-code')

  g = Graph()

  for _, row in contact_cleansed.iterrows():
    abb_id, abb_uuid = concept_uri(lblod + 'persoon/', str(row['Voornaam Contact Cleansed']) + str(row['Familienaam Contact Cleansed']))

    g.add((abb_id, RDF.type, ns.person.Person))
    add_literal(g, abb_id, ns.mu.uuid, abb_uuid, XSD.string)
    add_literal(g, abb_id, FOAF.familyName, str(row['Familienaam Contact Cleansed']), XSD.string)
    add_literal(g, abb_id, ns.persoon.gebruikteVoornaam, str(row['Voornaam Contact Cleansed']), XSD.string)

    if exists_contact_cont(row):
      site_id, site_uuid = concept_uri(lblod + 'vesting/', str(row['Voornaam Contact Cleansed']) + str(row['Familienaam Contact Cleansed']))
      g.add((site_id, RDF.type, ns.org.Site))
      add_literal(g, site_id, ns.mu.uuid, site_uuid, XSD.string)

      contact_id, contact_uuid = concept_uri(lblod + 'contactpunt/', str(row['Voornaam Contact Cleansed']) + str(row['Familienaam Contact Cleansed']) + '1')
      g.add((contact_id, RDF.type, ns.schema.ContactPoint))
      add_literal(g, contact_id, ns.mu.uuid, contact_uuid, XSD.string)

      add_literal(g, contact_id, ns.schema.email, str(row['Titel Cleansed']), XSD.string)
      add_literal(g, contact_id, ns.schema.email, str(row['Mail nr2 Cleansed']), XSD.string)
      add_literal(g, contact_id, ns.schema.telephone, str(row['Telefoonnr Contact 1']), XSD.string) 
      g.add((site_id, ns.schema.siteAddress, contact_id))

      if str(row['Telefoonnr Contact 2']) != str(np.nan):
        contact_tel2_id, contact_tel2_uuid = concept_uri(lblod + 'contactpunt/', str(row['Voornaam Contact Cleansed']) + str(row['Familienaam Contact Cleansed']) + str(row['Telefoonnr Contact 2']))
        g.add((contact_tel2_id, RDF.type, ns.schema.ContactPoint))
        add_literal(g, contact_tel2_id, ns.mu.uuid, contact_tel2_uuid, XSD.string)

        add_literal(g, contact_tel2_id, ns.schema.telephone, str(row['Telefoonnr Contact 2']), XSD.string) 
        g.add((site_id, ns.schema.siteAddress, contact_tel2_id))

      if str(row['GSMnr Contact Cleansed']) != str(np.nan):
        contact_gsm_id, contact_gsm_uuid = concept_uri(lblod + 'contactpunt/', str(row['Voornaam Contact Cleansed']) + str(row['Familienaam Contact Cleansed']) + str(row['GSMnr Contact Cleansed']))
        g.add((contact_gsm_id, RDF.type, ns.schema.ContactPoint))
        add_literal(g, contact_gsm_id, ns.mu.uuid, contact_gsm_uuid, XSD.string)

        add_literal(g, contact_gsm_id, ns.schema.telephone, str(row['GSMnr Contact Cleansed']), XSD.string) 
        g.add((site_id, ns.schema.siteAddress, contact_gsm_id))
      
      g.add((abb_id, ns.org.basedAt, site_id))
      
    if str(row['Id']) != str(np.nan):
      attr_id, _ = concept_uri(lblod + 'gestructureerdeIdentificator/', str(row['Voornaam Contact Cleansed']) + str(row['Familienaam Contact Cleansed']))
      g.add((attr_id, RDF.type, ns.generiek.GestructureerdeIdentificator))
      add_literal(g, attr_id, ns.generiek.lokaleIdentificator, str(row['Id']), XSD.string)

      g.add((abb_id, ns.generiek.gestructureerdeIdentificator, attr_id))

    org_id, _ = concept_uri(lblod + 'organisatie/', str(row['organisation_id']))
    if (str(row['Decretale functie Cleansed']) == str(np.nan)) and (str(row['Functietitel Cleansed']) != str(np.nan)):
      position_id, _ = concept_uri(lblod + 'hoedanigheid/', str(row['organisation_id']) + str(row['Functietitel Cleansed']))
      g.add((position_id, RDF.type, ns.organisatie.Hoedanigheid))

      # TODO: Map Functietitel properly
      role_id, _ = concept_uri(lblod + 'rol/', str(row['Functietitel Cleansed']))
      g.add((role_id, RDF.type, ns.org.Role))
      add_literal(g, role_id, RDFS.label, str(row['Functietitel Cleansed']))

      g.add((position_id, ns.org.role, role_id))

      g.add((position_id, ns.org.postIn, org_id))
      g.add((org_id, ns.org.hasPost, position_id))

      g.add((abb_id, ns.org.holds, position_id))
      g.add((position_id, ns.org.heldBy, abb_id))
    elif str(row['Decretale functie Cleansed']) != str(np.nan):
      # Bestuur temporary
      bestuur_temporary, bestuur_uuid = concept_uri(lblod + 'bestuursorgaan/', str(row['organisation_id']) + str(datetime.now()))
      g.add((bestuur_temporary, RDF.type, ns.besluit.Bestuursorgaan))
      add_literal(g, bestuur_temporary, ns.mu.uuid, bestuur_uuid, XSD.string)
      g.add((bestuur_temporary, ns.generiek.isTijdspecialisatieVan, org_id))

      ## Functionaris
      person_functionaris, _ = concept_uri(lblod + 'functionaris/',  str(row['Voornaam Contact Cleansed']) + str(row['Familienaam Contact Cleansed']) + str(row['organisation_id']) + str(row['Decretale functie Cleansed'].lower().replace(" ", "")))
      g.add((person_functionaris, RDF.type, ns.lblodlg.Functionaris))
      g.add((person_functionaris, ns.mandaat.isBestuurlijkeAliasVan, abb_id))
      #start
      #einde
      #status ~ cf loket lokale besturen PoC https://poc-form-builder.relance.s.redpencil.io/codelijsten
      # https://data.vlaanderen.be/id/conceptscheme/MandatarisStatusCode
      g.add((person_functionaris, ns.mandaat.status, ns.mandataris_status[row['Functionaris status']]))
      g.add((abb_id, ns.mandaat.isAangesteldAls, person_functionaris))

      # https://data.vlaanderen.be/doc/conceptscheme/BestuursfunctieCode
      ## Bestuuursfunctie
      person_bestuursfunctie, person_bestuursfunctie_uuid = concept_uri(lblod + 'bestuursfunctie/', str(row['Voornaam Contact Cleansed']) + str(row['Familienaam Contact Cleansed']) + str(row['organisation_id']))
      g.add((person_bestuursfunctie, RDF.type, ns.lblodlg.Bestuursfunctie))
      add_literal(g, person_bestuursfunctie, ns.mu.uuid, person_bestuursfunctie_uuid, XSD.string)

      bestuursfunctie_code = get_concept_id(codelist_bestuursfunctie, row['Decretale functie Cleansed'])
      g.add((person_bestuursfunctie, ns.org.role, bestuursfunctie_code))
      g.add((person_bestuursfunctie, ns.org.heldBy, person_functionaris))
      g.add((person_functionaris, ns.org.holds, person_bestuursfunctie))

      g.add((bestuur_temporary, ns.org.hasPost, person_bestuursfunctie))
      g.add((person_bestuursfunctie, ns.org.postIn, bestuur_temporary))


  export_data(g, f'contact-{mode}')