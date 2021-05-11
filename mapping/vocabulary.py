import pandas as pd
import numpy as np
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS

from helper.functions import export_data
import helper.namespaces as ns

def main(file):
  vocabulary_raw = pd.read_excel(file)

  g = Graph()

  for _, row in vocabulary_raw.dropna(subset=['Uri']).iterrows():
    s = URIRef(row['Uri'])
    g.add((s, RDF.type, URIRef(ns.owl+str(row['Ontology type']))))
    g.add((s, RDFS.label, Literal(row['label'], lang='nl')))
    if pd.notna(row['comment']):
      g.add((s, RDFS.comment, Literal(row['comment'].strip(), lang='nl')))


  export_data(g, f'vocab')
  