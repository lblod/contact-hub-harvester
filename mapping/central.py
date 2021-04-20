import pandas as pd
import numpy as np
from datetime import datetime
from rdflib import Graph, Literal, RDF, URIRef
from rdflib.namespace import XSD, FOAF, SKOS, RDF

import cleansing.central as cls_central
from helper.functions import add_literal, concept_uri, exists_address_central, export_df, export_data
import helper.namespaces as ns

def create_status_uri(g, data):
  for status in data['Status_CKB'].dropna().unique():
    subject, _ = concept_uri(ns.os, status)
    g.add((subject, RDF.type, SKOS.Concept))
    g.add((subject, SKOS.prefLabel, Literal(status, lang='nl')))
    if(status.startswith('Operationeel') or status.startswith('Actief')) :
      g.add((subject, SKOS.broader, ns.os.actief))
    else:
      g.add((subject, SKOS.broader, ns.os.nietactief))

def create_bestuursfuncie(g):
  voorzitter_concept, _ = concept_uri(ns.bf + 'concept/BestuursFunctieCode/', 'voorzitter')
  
  g.add((voorzitter_concept, RDF.type, SKOS.Concept))
  g.add((voorzitter_concept, SKOS.prefLabel, Literal('Voorzitter', lang='nl')))
  g.add((voorzitter_concept, SKOS.inScheme, URIRef('http://data.vlaanderen.be/id/conceptscheme/BestuursfunctieCode')))

  co_voorzitter_concept, _ = concept_uri(ns.bf + 'concept/BestuursFunctieCode/', 'co-voorzitter')
  
  g.add((co_voorzitter_concept, RDF.type, SKOS.Concept))
  g.add((co_voorzitter_concept, SKOS.prefLabel, Literal('Co-Voorzitter', lang='nl')))
  g.add((co_voorzitter_concept, SKOS.inScheme, URIRef('http://data.vlaanderen.be/id/conceptscheme/BestuursfunctieCode')))

  secretaris_concept, _ = concept_uri(ns.bf + 'concept/BestuursFunctieCode/', 'secretaris')

  g.add((secretaris_concept, RDF.type, SKOS.Concept))
  g.add((secretaris_concept, SKOS.prefLabel, Literal('Secretaris', lang='nl')))
  g.add((secretaris_concept, SKOS.inScheme, URIRef('http://data.vlaanderen.be/id/conceptscheme/BestuursfunctieCode')))

  secretaris_general_concept, _ = concept_uri(ns.bf + 'concept/BestuursFunctieCode/', 'secretaris-generaal')

  g.add((secretaris_general_concept, RDF.type, SKOS.Concept))
  g.add((secretaris_general_concept, SKOS.prefLabel, Literal('Secretaris-Generaal', lang='nl')))
  g.add((secretaris_general_concept, SKOS.inScheme, URIRef('http://data.vlaanderen.be/id/conceptscheme/BestuursfunctieCode')))

  penning_meester_concept, _ = concept_uri(ns.bf + 'concept/BestuursFunctieCode/', 'penningmeester')

  g.add((penning_meester_concept, RDF.type, SKOS.Concept))
  g.add((penning_meester_concept, SKOS.prefLabel, Literal('Penningmeester', lang='nl')))
  g.add((penning_meester_concept, SKOS.inScheme, URIRef('http://data.vlaanderen.be/id/conceptscheme/BestuursfunctieCode')))

  lid_concept, _ = concept_uri(ns.bf + 'concept/BestuursFunctieCode/', 'lid')

  g.add((lid_concept, RDF.type, SKOS.Concept))
  g.add((lid_concept, SKOS.prefLabel, Literal('Lid', lang='nl')))
  g.add((lid_concept, SKOS.inScheme, URIRef('http://data.vlaanderen.be/id/conceptscheme/BestuursfunctieCode')))

  bisschop_concept, _ = concept_uri(ns.bf + 'concept/BestuursFunctieCode/', 'bisschop')

  g.add((bisschop_concept, RDF.type, SKOS.Concept))
  g.add((bisschop_concept, SKOS.prefLabel, Literal('Bisschop', lang='nl')))
  g.add((bisschop_concept, SKOS.inScheme, URIRef('http://data.vlaanderen.be/id/conceptscheme/BestuursfunctieCode')))

  kardinaal_concept, _ = concept_uri(ns.bf + 'concept/BestuursFunctieCode/', 'kardinaal')

  g.add((kardinaal_concept, RDF.type, SKOS.Concept))
  g.add((kardinaal_concept, SKOS.prefLabel, Literal('Kardinaal-Aartsbischop', lang='nl')))
  g.add((kardinaal_concept, SKOS.inScheme, URIRef('http://data.vlaanderen.be/id/conceptscheme/BestuursfunctieCode')))

  aartsbisschop_concept, _ = concept_uri(ns.bf + 'concept/BestuursFunctieCode/', 'aartsbisschop')

  g.add((aartsbisschop_concept, RDF.type, SKOS.Concept))
  g.add((aartsbisschop_concept, SKOS.prefLabel, Literal('Metropoliet-Aartsbisschop van België', lang='nl')))
  g.add((aartsbisschop_concept, SKOS.inScheme, URIRef('http://data.vlaanderen.be/id/conceptscheme/BestuursfunctieCode')))

  ned_voorzitter_concept, _ = concept_uri(ns.bf + 'concept/BestuursFunctieCode/', 'ned_voorzitter')

  g.add((ned_voorzitter_concept, RDF.type, SKOS.Concept))
  g.add((ned_voorzitter_concept, SKOS.prefLabel, Literal('Nederlandstalige Vicevoorzitter', lang='nl')))
  g.add((ned_voorzitter_concept, SKOS.inScheme, URIRef('http://data.vlaanderen.be/id/conceptscheme/BestuursfunctieCode')))

  fran_voorzitter_concept, _ = concept_uri(ns.bf + 'concept/BestuursFunctieCode/', 'fran_voorzitter')

  g.add((fran_voorzitter_concept, RDF.type, SKOS.Concept))
  g.add((fran_voorzitter_concept, SKOS.prefLabel, Literal('Franstalige Vicevoorzitter', lang='nl')))
  g.add((fran_voorzitter_concept, SKOS.inScheme, URIRef('http://data.vlaanderen.be/id/conceptscheme/BestuursfunctieCode')))


def main(file):
  central_raw = pd.read_excel(file)
  central_cleansed = cls_central.main(central_raw)

  export_df(central_cleansed, 'central')

  g = Graph()

  create_status_uri(g, central_cleansed)
  create_bestuursfuncie(g)

  for _, row in central_cleansed.iterrows():    
    abb_id, _ = concept_uri(ns.lblod + 'organisatie/', str(row['organization_id']))
    g.add((abb_id, RDF.type, ns.org.Organization))

    add_literal(g, abb_id, SKOS.prefLabel, str(row['Naam_CKB']))
    add_literal(g, abb_id, ns.regorg.legalName, str(row['Naam_CKB']))

    status, _ = concept_uri(ns.os, row['Status_CKB'])
    g.add((abb_id, ns.regorg.orgStatus, status))

    g.add((abb_id, ns.org.classification, ns.bestuurseenheid_classification_code["centraal"]))

    if str(row['KBO_CKB_cleansed']) != str(np.nan):
      kbo_uri, _  = concept_uri(ns.lblod + 'gestructureerdeIdentificator/', str(row['KBO_CKB_cleansed']))
      g.add((kbo_uri, RDF.type, ns.generiek.GestructureerdeIdentificator))
      add_literal(g, kbo_uri, ns.generiek.lokaleIdentificator, str(row['KBO_CKB_cleansed']), XSD.string)
      g.add((abb_id, ns.generiek.gestructureerdeIdentificator, kbo_uri))

    if str(row['Titel']) != str(np.nan):
      naam_uri, _ = concept_uri(ns.lblod + 'gestructureerdeIdentificator/', str(row['Titel']))
      g.add((naam_uri, RDF.type, ns.generiek.GestructureerdeIdentificator))
      add_literal(g, naam_uri, ns.generiek.lokaleIdentificator, str(row['Titel']), XSD.string)
      g.add((abb_id, ns.generiek.gestructureerdeIdentificator, naam_uri))


    # Vestiging
    if exists_address_central(row):
      vestiging_uri, _ = concept_uri(ns.lblod + 'vestiging/', row['organization_id'])
      g.add((vestiging_uri, RDF.type, ns.org.Site))
      
      address_uri, _ = concept_uri(ns.lblod + 'adresvoorstelling/', row['organization_id'])
      g.add((address_uri, RDF.type, ns.locn.Address))
      g.add((vestiging_uri, ns.organisatie.bestaatUit, address_uri))
      add_literal(g, address_uri, ns.locn.thoroughfare, str(row['Straat_CKB']))
      add_literal(g, address_uri, ns.adres['Adresvoorstelling.huisnummer'], str(row['Huisnr_CKB_Cleansed']), XSD.string)
      add_literal(g, address_uri, ns.adres['Adresvoorstelling.busnummer'], str(row['Busnummer_CKB_Cleansed']), XSD.string)
      add_literal(g, address_uri, ns.locn.postCode, str(row['Postcode_CKB']), XSD.string)
      add_literal(g, address_uri, ns.adres.gemeentenaam, str(row['Gemeente_CKB']))
      add_literal(g, address_uri, ns.locn.adminUnitL2, str(row['Provincie_CKB']))
      g.add((address_uri, ns.adres.land, Literal('België', lang='nl')))

      g.add((abb_id, ns.org.hasPrimarySite, vestiging_uri))

    #Bestuur
    #bestuur = concept_uri(ns.lblod + 'bestuursorgaan/', row['organization_id'])
    #g.add((bestuur, RDF.type, ns.besluit.Bestuursorgaan))
    #g.add((bestuur, ns.besluit.bestuurt, abb_id))

    bestuur_temporary, _ = concept_uri(ns.lblod + 'bestuursorgaan/', str(row['organization_id']) + str(datetime.now().year))
    g.add((bestuur_temporary, RDF.type, ns.besluit.Bestuursorgaan))
    g.add((bestuur_temporary, ns.generiek.isTijdspecialisatieVan, abb_id))

    # Voorzitter
    voorzitter, _ = concept_uri(ns.lblod + 'persoon/', str(row['Naam_Voorzitter_CKB_first']) + str(row['Naam_Voorzitter_CKB_last']))
    g.add((voorzitter, RDF.type, ns.person.Person))
    add_literal(g, voorzitter, FOAF.givenName, str(row['Naam_Voorzitter_CKB_first']))
    add_literal(g, voorzitter, FOAF.familyName, str(row['Naam_Voorzitter_CKB_last']))

    ## Voorzitter 
    voorzitter_vestiging_uri, _ = concept_uri(ns.lblod + 'vestiging/', str(row['organization_id']) + str(row['Naam_Voorzitter_CKB_first']) + str(row['Naam_Voorzitter_CKB_last']))
    g.add((voorzitter_vestiging_uri, RDF.type, ns.org.Site))
    g.add((voorzitter, ns.org.basedAt, voorzitter_vestiging_uri))

    voorzitter_contact_uri, _ = concept_uri(ns.lblod + 'contactpunt/', str(row['organization_id']) + str(row['Naam_Voorzitter_CKB_first']) + str(row['Naam_Voorzitter_CKB_last']) + str(row['Tel_CKB_voorzitter_1']))
    g.add((voorzitter_contact_uri, RDF.type, ns.schema.ContactPoint))
    add_literal(g, voorzitter_contact_uri, ns.schema.telephone, str(row['Tel_CKB_voorzitter_1']), datatype=XSD.string)
    g.add((voorzitter_vestiging_uri, ns.schema.siteAdress, voorzitter_contact_uri))
    add_literal(g, voorzitter_contact_uri, ns.schema.email, str(row['Mail_voorzitter_CKB_Cleansed']))

    if str(row['Tel_CKB_voorzitter_2']) != str(np.nan):
      voorzitter_contact_2_uri, _ = concept_uri(ns.lblod + 'contactpunt/', str(row['organization_id']) + str(row['Naam_Voorzitter_CKB_first']) + str(row['Naam_Voorzitter_CKB_last']) + str(row['Tel_CKB_voorzitter_2']))
      g.add((voorzitter_contact_2_uri, RDF.type, ns.schema.ContactPoint))
      add_literal(g, voorzitter_contact_2_uri, ns.schema.telephone, str(row['Tel_CKB_voorzitter_2']), datatype=XSD.string)
      g.add((voorzitter_vestiging_uri, ns.schema.siteAdress, voorzitter_contact_uri))

    ## Mandaat
    voorzitter_mandaat, _ = concept_uri(ns.lblod + 'mandaat/', str(row['Naam_Voorzitter_CKB_first']) + str(row['Naam_Voorzitter_CKB_last']) + str(row['organization_id']))
    g.add((voorzitter_mandaat, RDF.type, ns.mandaat.Mandaat))
    g.add((voorzitter_mandaat, ns.org.role, ns.bestursfunctie_code['Voorzitter']))
    g.add((voorzitter_mandaat, ns.org.postIn, bestuur_temporary))

    ## Mandataris
    voorzitter_mandataris, _ = concept_uri(ns.lblod + 'mandataris/', str(row['Naam_Voorzitter_CKB_first']) + str(row['Naam_Voorzitter_CKB_last']) + str(row['organization_id'] + 'voorzitter'))
    g.add((voorzitter_mandataris, RDF.type, ns.mandaat.Mandataris))
    g.add((voorzitter_mandataris, ns.mandaat.isBestuurlijkeAliasVan, voorzitter))
    g.add((voorzitter_mandataris, ns.org.holds, voorzitter_mandaat))
    #start
    #einde
    #status ~ cf loket lokale besturen PoC https://poc-form-builder.relance.s.redpencil.io/codelijsten
    
    g.add((voorzitter, ns.mandaat.isAangesteldAls, voorzitter_mandataris))
    g.add((bestuur_temporary, ns.org.hasPost, voorzitter_mandaat))

    ####
    #Secretaris
    secretaris, _ =  concept_uri(ns.lblod + 'persoon/', str(row['Naam_secretaris_CKB_first']) + str(row['Naam_secretaris_CKB_last']))
    g.add((secretaris, RDF.type, ns.person.Person))
    add_literal(g, secretaris, ns.persoon.gebruikteVoornaam, str(row['Naam_secretaris_CKB_first']))
    add_literal(g, secretaris, FOAF.familyName, str(row['Naam_secretaris_CKB_last']))
    ## Tel secretaris
    secretaris_vestiging_uri, _ = concept_uri(ns.lblod + 'vestiging/', str(row['organization_id']) + str(row['Naam_secretaris_CKB_first']) + str(row['Naam_secretaris_CKB_last']))
    g.add((secretaris_vestiging_uri, RDF.type, ns.org.Site))
    g.add((secretaris, ns.org.basedAt, secretaris_vestiging_uri))

    secretaris_contact_uri, _ = concept_uri(ns.lblod + 'contactinfo/', str(row['organization_id']) + str(row['Naam_secretaris_CKB_first']) + str(row['Naam_secretaris_CKB_last']))
    g.add((secretaris_contact_uri, RDF.type, ns.schema.ContactPoint))
    g.add((secretaris_vestiging_uri, ns.schema.siteAdress, secretaris_contact_uri))
    add_literal(g, secretaris_contact_uri, ns.schema.telephone, str(row['Tel_CKB_secretaris_1']), XSD.string)
    add_literal(g, secretaris_contact_uri, ns.schema.mail, str(row['Mail_secretaris_CKB_Cleansed']), XSD.string)
    add_literal(g, secretaris_contact_uri, ns.schema.telephone, str(row['Tel_CKB_secretaris_2']), XSD.string)

    #Mandataris
    secretaris_mandataris, _ = concept_uri(ns.lblod + 'mandataris/', str(row['Naam_secretaris_CKB_first']) + str(row['Naam_secretaris_CKB_last']) + str(row['organization_id'] + 'secretaris'))
    g.add((secretaris_mandataris, RDF.type, ns.mandaat.Mandataris))
    g.add((secretaris, ns.mandaat.isAangesteldAls, secretaris_mandataris))
    g.add((secretaris_mandataris, ns.mandaat.isBestuurlijkeAliasVan, secretaris))
    #start
    #einde
    #status
    secretaris_mandaat, _ = concept_uri(ns.lblod + 'mandaat/', str(row['Naam_secretaris_CKB_first']) + str(row['Naam_secretaris_CKB_last']) + str(row['organization_id']))
    g.add((secretaris_mandaat, RDF.type, ns.mandaat.Mandaat))
    g.add((secretaris_mandataris, ns.org.holds, secretaris_mandaat))
    g.add((secretaris_mandaat, ns.org.role, ns.bestursfunctie_code['Secretaris']))

    g.add((bestuur_temporary, ns.org.hasPost, secretaris_mandaat))
    g.add((secretaris_mandaat, ns.org.postIn, bestuur_temporary))

  export_data(g, 'central-dev')


