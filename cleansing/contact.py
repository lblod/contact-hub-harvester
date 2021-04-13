import helper.functions as helper
import pandas as pd
import numpy as np

def main(df):

  df[['Titel Cleansed', 'Titel Comment']] = pd.DataFrame(df['Titel'].astype(str).apply(helper.mail_cleansing).values.tolist(), columns=['titel_cleansed','comment'])

  df[['Referentieorganisatie Cleansed']] = pd.DataFrame(df['Referentieorganisatie'].astype(str).apply(helper.referentieorganisatie_cleansing).values.tolist())

  df['Decretale functie Cleansed'] = df[df['Decretale functie'] != 'Griffier']['Decretale functie'].str.title().replace('GEEN of ONBEKEND', np.nan)

  df[['Decretale functie Cleansed', 'Functionaris status']] = pd.DataFrame(df[df['Decretale functie'] != 'Griffier']['Decretale functie'].astype(str).apply(helper.decretale_functie_cleasing).values.tolist(), columns=['decretale cleansed','status'])

  df[['Familienaam Contact Cleansed', 'Familienaam Contact Comment']] = pd.DataFrame(df['Familienaam Contact'].astype(str).apply(helper.naam_contact_cleansing).values.tolist(), columns=['naam_contact_cleansed','comment'])

  df[['Voornaam Contact Cleansed', 'Voornaam Contact Comment']] = pd.DataFrame(df['Voornaam Contact'].astype(str).apply(helper.naam_contact_cleansing).values.tolist(), columns=['naam_contact_cleansed','comment'])

  df[['Telefoonnr Contact 1', 'Telefoonnr Contact 2', 'Telefoonnr Contact Comment']] = pd.DataFrame(df['Telefoonnr Contact'].astype(str).apply(helper.telephone_number_cleansing).values.tolist(), columns=['telephone_number_1', 'telephone_number_2', 'comment'])

  df[['GSMnr Contact Cleansed', 'GSMnr Contact 2', 'GSMnr Contact Comment']] = pd.DataFrame(df['GSMnr Contact'].astype(str).apply(helper.telephone_number_cleansing).values.tolist(), columns=['telephone_number_1', 'telephone_number_2', 'comment'])

  df['Functietitel Cleansed'] = df['Functietitel'].str.strip().str.title()
  
  df['Functietitel Cleansed'] = df['Functietitel Cleansed'].replace('0', np.nan)
  
  df['Werkt in:KBOnr Cleansed'] = df['Werkt in:KBOnr'].replace('Onbekend', np.nan)

  df['organisation_id'] = df['Werkt in:KBOnr Cleansed'].fillna(df['Referentieorganisatie'])

  df[['Mail nr2 Cleansed', 'Mail nr2 Comment']] = pd.DataFrame(df['Mail nr2'].astype(str).apply(helper.mail_cleansing).values.tolist(), columns=['mail_cleansed','comment'])
  
  df[(~df['Familienaam Contact Cleansed'].isnull() | ~df['Voornaam Contact Cleansed'].isnull())]

  df = df[df['Decretale functie'] != 'Griffier']

  return df