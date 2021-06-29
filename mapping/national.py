import pandas as pd
import numpy as np
from rdflib import Graph
from rdflib.namespace import XSD, FOAF, SKOS, RDF

from helper.functions import add_literal, concept_uri, export_data, get_concept_id, get_full_address, load_graph
import helper.namespaces as ns

def main(file, mode):
  national_raw = pd.read_excel(file)

  lblod = ns.get_namespace(mode)

  codelist_ere = load_graph('codelist-ere')

  g = Graph()

  for _, row in national_raw.iterrows():
    abb_id, abb_uuid = concept_uri(lblod + 'representatieveOrganen/', str(row['representatief orgaan']))
    #g.add((abb_id, RDF.type, ns.org.Organization))
    g.add((abb_id, RDF.type, ns.ere.RepresentatiefOrgaan))
    add_literal(g, abb_id, ns.mu.uuid, abb_uuid, XSD.string)

    add_literal(g, abb_id, SKOS.prefLabel, str(row['representatief orgaan']), XSD.string)

    #g.add((abb_id, RDFS.subClassOf, ns.org.Organization))
    #g.add((abb_id, RDFS.subClassOf, ns.org.RegisteredOrganization))
    
    if str(row['Type Eredienst']) != str(np.nan):
      type_ere = get_concept_id(codelist_ere, str(row['Type Eredienst']))
      g.add((abb_id, ns.ere.typeEredienst, type_ere)) 

    status = get_concept_id(codelist_ere, str(row['Status']))
    g.add((abb_id, ns.rov.orgStatus, status))

    id_class, id_uuid = concept_uri(lblod +'identificatoren/', str(row['KBO_nr']) + 'identificatoren')
    g.add((id_class, RDF.type, ns.adms.Identifier))
    add_literal(g, id_class, SKOS.notation, 'KBO nummer', XSD.string)
    add_literal(g, id_class, ns.mu.uuid, id_uuid, XSD.string)

    kbo_uri, kbo_uuid  = concept_uri(lblod + 'gestructureerdeIdentificatoren/', str(row['KBO_nr']) + 'gestructureerdeIdentificatoren')
    g.add((kbo_uri, RDF.type, ns.generiek.GestructureerdeIdentificator))
    add_literal(g, kbo_uri, ns.mu.uuid, kbo_uuid, XSD.string)
    add_literal(g, kbo_uri, ns.generiek.lokaleIdentificator, str(row['KBO_nr']), XSD.string)
    g.add((id_class, ns.generiek.gestructureerdeIdentificator, kbo_uri))

    g.add((abb_id, ns.adms.identifier, id_class))

    site_id, site_uuid = concept_uri(lblod + 'vestigingen/', str(row['representatief orgaan']) + 'vestigingen')
    g.add((site_id, RDF.type, ns.org.Site))
    add_literal(g, site_id, ns.mu.uuid, site_uuid, XSD.string)

    contact_id, contact_uuid = concept_uri(lblod + 'contact-punten/', str(row['representatief orgaan']) + 'contact-punten/1')
    g.add((contact_id, RDF.type, ns.schema.ContactPoint))
    add_literal(g, contact_id, ns.mu.uuid, contact_uuid, XSD.string)
    add_literal(g, contact_id, FOAF.page, str(row['Website']), XSD.anyURI)
    add_literal(g, contact_id, ns.schema.telephone, str(row['Telefoon']), XSD.string)
    add_literal(g, contact_id, ns.schema.faxNumber, str(row['Fax']), XSD.string)
    g.add((site_id, ns.schema.siteAddress, contact_id))

    if str(row['Telefoon 2']) != str(np.nan) or str(row['Fax 2']) != str(np.nan):
      contact_2_id, contact_2_uuid = concept_uri(lblod + 'contact-punten/', str(row['representatief orgaan']) + 'contact-punten/2')
      g.add((contact_2_id, RDF.type, ns.schema.ContactPoint))
      add_literal(g, contact_2_id, ns.mu.uuid, contact_2_uuid, XSD.string)
      add_literal(g, contact_2_id, ns.schema.telephone, str(row['Telefoon 2']), XSD.string)
      add_literal(g, contact_2_id, ns.schema.faxNumber, str(row['Fax 2']), XSD.string)
      g.add((site_id, ns.schema.siteAddress, contact_2_id))

    address_id, address_uuid = concept_uri(lblod + 'adressen/', str(row['representatief orgaan']))
    g.add((address_id, RDF.type, ns.locn.Address))
    add_literal(g, address_id, ns.mu.uuid, address_uuid, XSD.string)
    add_literal(g, address_id, ns.locn.thoroughfare, str(row['Straatnaam']), XSD.string)
    add_literal(g, address_id, ns.adres['Adresvoorstelling.huisnummer'], str(row['Huisnummer']), XSD.string)
    add_literal(g, address_id, ns.adres['Adresvoorstelling.busnummer'], str(row['Busnummer']), XSD.string)
    add_literal(g, address_id, ns.locn.postCode, str(row['Postcode']), XSD.string)
    add_literal(g, address_id, ns.adres.gemeentenaam, str(row['Gemeentenaam']), XSD.string)
    add_literal(g, address_id, ns.locn.adminUnitL2, str(row['Provincie']), XSD.string)
    add_literal(g, address_id, ns.adres.land, 'België', XSD.string)

    add_literal(g, address_id, ns.locn.fullAddress, get_full_address(str(row['Straatnaam']), str(row['Huisnummer']), str(row['Busnummer']), str(row['Postcode']), str(row['Gemeentenaam'])), XSD.string)
    
    g.add((site_id, ns.organisatie.bestaatUit, address_id))

    g.add((abb_id, ns.org.hasPrimarySite, site_id))  

    person_id, person_uuid = concept_uri(lblod + 'personen/', str(row['Voornaam']) + str(row['Achternaam']))
    g.add((person_id, RDF.type, ns.person.Person))
    add_literal(g, person_id, ns.mu.uuid, person_uuid, XSD.string)
    add_literal(g, person_id, FOAF.givenName, str(row['Voornaam']), XSD.string)
    add_literal(g, person_id, FOAF.familyName, str(row['Achternaam']), XSD.string)
    add_literal(g, person_id, ns.persoon.gebruikteVoornaam, str(row['Gebruikte Voornaam']), XSD.string)

    role_id, role_uuid = concept_uri(lblod + 'rol/', str(row['Rol']))
    g.add((role_id, RDF.type, ns.org.Role))
    add_literal(g, role_id, ns.mu.uuid, role_uuid, XSD.string)
    add_literal(g, role_id, SKOS.prefLabel, str(row['Rol']), XSD.string)

    position_id, position_uuid = concept_uri(lblod + 'positie/', str(row['representatief orgaan']) + str(row['Rol']))
    g.add((position_id, RDF.type, ns.org.Post))
    add_literal(g, position_id, ns.mu.uuid, position_uuid, XSD.string)
    g.add((position_id, ns.org.role, role_id))
    g.add((position_id, ns.org.postIn, abb_id))
    g.add((abb_id, ns.org.hasPost, position_id))

    person_position_id, person_position_uuid = concept_uri(lblod + 'agentenInPositie/', str(row['Voornaam']) + str(row['Achternaam']) + str(row['Rol']))
    g.add((person_position_id, RDF.type, ns.organisatie.AgentInPositie))
    add_literal(g, person_position_id, ns.mu.uuid, person_position_uuid, XSD.string)
    g.add((person_position_id, ns.org.holds, position_id))
    g.add((person_position_id, ns.org.heldBy, person_id))
    
  export_data(g, f'national-{mode}')

    


