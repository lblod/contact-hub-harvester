import pandas as pd
import numpy as np
from rdflib import Graph
from rdflib.namespace import XSD, FOAF, SKOS, RDF

from helper.functions import add_literal, concept_uri, export_data
import helper.namespaces as ns

def main(file, mode):
  national_raw = pd.read_excel(file)

  lblod = ns.get_namespace(mode)

  g = Graph()

  for _, row in national_raw.iterrows():
    abb_id, abb_uuid = concept_uri(lblod + 'representatiefOrgaan/', str(row['representatief orgaan']))
    g.add((abb_id, RDF.type, ns.ere.RepresentatiefOrgaan))
    add_literal(g, abb_id, ns.mu.uuid, abb_uuid, XSD.string)

    add_literal(g, abb_id, SKOS.prefLabel, str(row['representatief orgaan']))

    #g.add((abb_id, RDFS.subClassOf, ns.org.Organization))
    #g.add((abb_id, RDFS.subClassOf, ns.org.RegisteredOrganization))
    
    add_literal(g, abb_id, ns.ere.typeEredienst, str(row['Type Eredienst']))

    status, _ = concept_uri(ns.c + 'OrganisatieStatusCode/', str(row['Status']))
    g.add((abb_id, ns.rov.orgStatus, status))

    id_class, id_uuid = concept_uri(lblod +'identificator/', str(row['KBO_nr']))
    g.add((id_class, RDF.type, ns.adms.Identifier))
    add_literal(g, id_class, SKOS.notation, 'KBO nummer', XSD.string)
    add_literal(g, id_class, ns.mu.uuid, id_uuid, XSD.string)

    kbo_uri, kbo_uuid  = concept_uri(lblod + 'gestructureerdeIdentificator/', str(row['KBO_nr']))
    g.add((kbo_uri, RDF.type, ns.generiek.GestructureerdeIdentificator))
    add_literal(g, kbo_uri, ns.mu.uuid, kbo_uuid, XSD.string)
    add_literal(g, kbo_uri, ns.generiek.lokaleIdentificator, str(row['KBO_nr']), XSD.string)
    g.add((id_class, ns.generiek.gestructureerdeIdentificator, kbo_uri))

    g.add((abb_id, ns.adms.identifier, id_class))

    site_id, site_uuid = concept_uri(lblod + 'vestiging/', str(row['representatief orgaan']))
    g.add((site_id, RDF.type, ns.org.Site))
    add_literal(g, site_id, ns.mu.uuid, site_uuid, XSD.string)

    contact_id, contact_uuid = concept_uri(lblod + 'contactpunt/', str(row['representatief orgaan']) + '1')
    g.add((contact_id, RDF.type, ns.schema.ContactPoint))
    add_literal(g, contact_id, ns.mu.uuid, contact_uuid, XSD.string)
    add_literal(g, contact_id, FOAF.page, str(row['Website']), XSD.anyURI)
    add_literal(g, contact_id, ns.schema.telephone, str(row['Telefoon']), XSD.string)
    add_literal(g, contact_id, ns.schema.faxNumber, str(row['Fax']), XSD.string)
    g.add((site_id, ns.schema.siteAddress, contact_id))

    if str(row['Telefoon 2']) != str(np.nan) or str(row['Fax 2']) != str(np.nan):
      contact_2_id, contact_2_uuid = concept_uri(lblod + 'contactpunt/', str(row['representatief orgaan']) + '2')
      g.add((contact_2_id, RDF.type, ns.schema.ContactPoint))
      add_literal(g, contact_2_id, ns.mu.uuid, contact_2_uuid, XSD.string)
      add_literal(g, contact_2_id, ns.schema.telephone, str(row['Telefoon 2']), XSD.string)
      add_literal(g, contact_2_id, ns.schema.faxNumber, str(row['Fax 2']), XSD.string)
      g.add((site_id, ns.schema.siteAddress, contact_2_id))

    address_id, address_uuid = concept_uri(lblod + 'adres/', str(row['representatief orgaan']))
    g.add((address_id, RDF.type, ns.locn.Address))
    add_literal(g, address_id, ns.mu.uuid, address_uuid, XSD.string)
    add_literal(g, address_id, ns.locn.thoroughfare, str(row['Straatnaam']))
    add_literal(g, address_id, ns.adres['Adresvoorstelling.huisnummer'], str(row['Huisnummer']), XSD.string)
    add_literal(g, address_id, ns.adres['Adresvoorstelling.busnummer'], str(row['Busnummer']), XSD.string)
    add_literal(g, address_id, ns.locn.postCode, str(row['Postcode']), XSD.string)
    add_literal(g, address_id, ns.adres.gemeentenaam, str(row['Gemeentenaam']))
    add_literal(g, address_id, ns.locn.adminUnitL2, str(row['Provincie']))
    add_literal(g, address_id, ns.adres.land, 'België')
    
    g.add((site_id, ns.organisatie.bestaatUit, address_id))

    g.add((abb_id, ns.org.hasPrimarySite, site_id))  

    person_id, person_uuid = concept_uri(lblod + 'persoon/', str(row['Gebruikte Voornaam']) + str(row['Achternaam']))
    g.add((person_id, RDF.type, ns.person.Person))
    add_literal(g, person_id, ns.mu.uuid, person_uuid, XSD.string)
    add_literal(g, person_id, FOAF.givenName, str(row['Gebruikte Voornaam']))
    add_literal(g, person_id, FOAF.familyName, str(row['Achternaam']))

    role_id, role_uuid = concept_uri(lblod + 'rol/', str(row['Rol']))
    g.add((role_id, RDF.type, SKOS.Concept))
    add_literal(g, role_id, ns.mu.uuid, role_uuid, XSD.string)
    add_literal(g, role_id, SKOS.prefLabel, str(row['Rol']))

    position_id, position_uuid = concept_uri(lblod + 'positie/', str(row['Rol']))
    g.add((position_id, RDF.type, ns.org.Post))
    add_literal(g, position_id, ns.mu.uuid, position_uuid, XSD.string)
    g.add((position_id, ns.org.role, role_id))

    person_position_id, person_position_uuid = concept_uri(lblod + 'agentInPositie/', str(row['Gebruikte Voornaam']) + str(row['Achternaam']) + str(row['Rol']))
    g.add((person_position_id, RDF.type, ns.organisatie.AgentInPositie))
    add_literal(g, person_position_id, ns.mu.uuid, person_position_uuid, XSD.string)
    g.add((person_position_id, ns.org.holds, position_id))
    g.add((person_position_id, ns.org.heldBy, person_id))
    g.add((person_position_id, ns.org.postIn, abb_id))
    
    g.add((abb_id, ns.org.hasPost, person_position_id))

  export_data(g, f'national-{mode}')

    


