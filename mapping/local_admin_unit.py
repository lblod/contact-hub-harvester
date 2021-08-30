from rdflib import Graph, URIRef
from rdflib.namespace import XSD, RDF, RDFS
from helper.functions import add_literal, get_all_admin_units, export_data
import helper.namespaces as ns

def main():
  g = Graph()

  results = get_all_admin_units()

  for result in results:
    admin_unit_id = URIRef(result['admin_unit']['value'])
    g.add((admin_unit_id, RDF.type, ns.besluit.Bestuurseenheid))
    add_literal(g, admin_unit_id, ns.mu.uuid, result['uuid']['value'], XSD.string)
    add_literal(g, admin_unit_id, RDFS.label, result['admin_unit_label']['value'], XSD.string)
    g.add((admin_unit_id, ns.besluit.classificatie, URIRef(result['classificatie']['value'])))

  export_data(g, 'local_administrative_units')

  g.serialize('input/codelists/local_admininistrative_units.ttl',format='turtle')
