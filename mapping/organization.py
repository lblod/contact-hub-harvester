import pandas as pd
from rdflib import Graph, Literal, RDF, URIRef, N
from rdflib.namespace import FOAF , XSD, DC, FOAF, SKOS, RDF, RDFS

import cleansing.organization as cls_org
from helper.functions import add_literal, concept_uri
import helper.namespaces as ns


def main(file): 
  org_raw = pd.read_excel(file)
  orgs_cleansed = cls_org.main(org_raw)

  g = Graph()
  
  for index, row in orgs_cleansed.iterrows():
    print('test')
