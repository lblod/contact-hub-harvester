import helper.functions as helper
import pandas as pd
import numpy as np

def main(eb):
  eb[['Titel Cleansed']] = pd.DataFrame(eb['Titel'].astype(str).apply(helper.space_cleansing).values.tolist())

  eb['Gemeente_EB Cleansed'] = eb['Gemeente_EB'].str.strip().str.title().replace('Antwerpen (Deurne', 'Antwerpen (Deurne)')

  eb['Provincie_EB Cleansed'] = eb['Provincie_EB Cleansed'].replace('nan', np.NaN)

  worship[['KBOnr_cleansed', 'KBOnr_comment']] = pd.DataFrame(eb['KBOnr'].astype(str).apply(helper.kbo_cleansing).values.tolist(), columns=['kbo_cleansed','comment'])
  
  eb['organization_id'] = eb['KBO_EB Cleansed'].fillna(eb['Titel'])

  eb[['Huisnr_EB Cleansed', 'Busnummer_EB Cleansed', 'Huisnr_EB Comment']] = pd.DataFrame(eb['Huisnr_EB'].astype(str).apply(helper.split_house_bus_number).values.tolist(), columns=['house_number', 'bus_number', 'comment'])

  eb[['Postcode_EB Cleansed', 'Postcode_EB Comment']] = pd.DataFrame(eb['Postcode_EB'].astype(str).apply(helper.postcode_cleansing).values.tolist(), columns=['postcode_cleansed','comment'])

  eb['Naam_voorzitter_EB Cleansed'] = eb['Naam_voorzitter_EB'].str.replace('<br>', '').str.strip()
  
  eb[['Naam_voorzitter_EB First', 'Naam_voorzitter_EB Last', 'Naam_voorzitter_EB Comment']] = pd.DataFrame(eb['Naam_voorzitter_EB Cleansed'].astype(str).apply(helper.splitname).values.tolist(), columns=['first', 'last', 'comment'])

  eb['Adres_voorzitter_EB Cleansed'] = eb['Adres_voorzitter_EB'].str.replace('<br>', '').str.strip()

  eb[['Mail_voorzitter_EB Cleansed', 'Mail_voorzitter_EB Comment']] = pd.DataFrame(eb['Mail_voorzitter_EB'].astype(str).apply(helper.mail_cleansing).values.tolist(), columns=['mail_cleansed','comment'])

  eb[['Tel_voorzitter_EB 1', 'Tel_voorzitter_EB 2', 'Tel_voorzitter_EB Comment']] = pd.DataFrame(eb['Tel_voorzitter_EB'].astype(str).apply(helper.telephone_number_cleansing).values.tolist(), columns=['telephone_number_1', 'telephone_number_2', 'comment'])

  eb['Naam_penningmeester_EB Cleansed'] = eb['Naam_penningmeester_EB'].str.replace('<br>', '').str.strip()
  eb[['Naam_penningmeester_EB First', 'Naam_penningmeester_EB Last', 'Naam_penningmeester_EB Comment']] = pd.DataFrame(eb['Naam_penningmeester_EB Cleansed'].astype(str).apply(helper.splitname).values.tolist(), columns=['first', 'last', 'comment'])

  eb['Adres_penningmeester_EB Cleansed'] = eb['Adres_penningmeester_EB'].str.replace('<br>', '').str.strip()

  eb[['Mail_penningmeester_EB Cleansed', 'Mail_penningmeester_EB Comment']] = pd.DataFrame(eb['Mail_penningmeester_EB'].astype(str).apply(helper.mail_cleansing).values.tolist(), columns=['mail_cleansed','comment'])

  eb[['Tel_penningmeester_EB 1', 'Tel_penningmeester_EB 2', 'Tel_penningmeester_EB Comment']] = pd.DataFrame(eb['Tel_penningmeester_EB'].astype(str).apply(helper.telephone_number_cleansing).values.tolist(), columns=['telephone_number_1', 'telephone_number_2', 'comment'])

  eb['Naam_secretaris_EB Cleansed'] = eb['Naam_secretaris_EB'].str.replace('<br>', '').str.strip()
  eb[['Naam_secretaris_EB First', 'Naam_secretaris_EB Last', 'Naam_secretaris_EB Comment']] = pd.DataFrame(eb['Naam_secretaris_EB Cleansed'].astype(str).apply(helper.splitname).values.tolist(), columns=['first', 'last', 'comment'])

  eb['Adres_secretaris_EB Cleansed'] = eb['Adres_secretaris_EB'].str.replace('<br>', '').str.strip()

  eb[['Mail_secretaris_EB Cleansed', 'Mail_secretaris_EB Comment']] = pd.DataFrame(eb['Mail_secretaris_EB'].astype(str).apply(helper.mail_cleansing).values.tolist(), columns=['mail_cleansed','comment'])

  eb[['Tel_secretaris_EB 1', 'Tel_secretaris_EB 2', 'Tel_secretaris_EB Comment']] = pd.DataFrame(eb['Tel_secretaris_EB'].astype(str).apply(helper.telephone_number_cleansing).values.tolist(), columns=['telephone_number_1', 'telephone_number_2', 'comment'])

  eb['Naam_Lid4 Cleansed'] = eb['Naam_Lid4'].str.replace('<br>', '').str.strip()
  eb[['Naam_Lid4 First', 'Naam_Lid4 Last', 'Naam_Lid4 Comment']] = pd.DataFrame(eb['Naam_Lid4 Cleansed'].astype(str).apply(helper.splitname).values.tolist(), columns=['first', 'last', 'comment'])

  eb['Naam_Lid5 Cleansed'] = eb['Naam_Lid5'].str.replace('<br>', '').str.strip()
  eb[['Naam_Lid5 First', 'Naam_Lid5 Last', 'Naam_Lid5 Comment']] = pd.DataFrame(eb['Naam_Lid5 Cleansed'].astype(str).apply(helper.splitname).values.tolist(), columns=['first', 'last', 'comment'])
  
  eb['Datum verkiezing penningmeester Cleansed'] = eb['Datum verkiezing penningmeester'].replace(' ', np.NaN)

  return eb