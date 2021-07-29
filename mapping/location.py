from rdflib import Graph, URIRef
from rdflib.namespace import XSD, RDF, RDFS
from helper.functions import add_literal, get_all_locations, export_data
import helper.namespaces as ns

def main():
  g = Graph()

  results = get_all_locations()

  for result in results:
    location_id = URIRef(result['loc']['value'])
    g.add((location_id, RDF.type, ns.prov.Location))
    add_literal(g, location_id, ns.mu.uuid, result['uuid']['value'], XSD.string)
    add_literal(g, location_id, RDFS.label, result['label']['value'], XSD.string)
    add_literal(g, location_id, ns.ext.werkingsgebiedNiveau, result['level']['value'], XSD.string)

  export_data(g, 'locations')

  g.serialize('input/codelists/locations.ttl',format='turtle')

