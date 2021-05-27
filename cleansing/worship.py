import helper.functions as helper
import pandas as pd
import numpy as np

def main(eb):
  eb['Public Involvement Cleansed'] = pd.Series(eb[['Opmerkingen_EB','Grensoverschrijdend']].astype(str).apply(helper.remarks_cleansing, axis=1).values)
  
  eb['Status_EB Cleansed'] = pd.Series(eb['Status_EB'].astype(str).apply(helper.status_mapping_worship).values)

  eb['Bestuursorgaan Type'] = pd.Series(eb['Type_eredienst_EB'].astype(str).apply(helper.bestuursorgaan_mapping_worship).values)

  eb[['Titel Cleansed']] = pd.DataFrame(eb['Titel'].astype(str).apply(helper.space_cleansing).values.tolist())

  eb['Gemeente Cleansed'] = eb['Gemeente_EB'].str.strip().str.title().replace('Antwerpen (Deurne', 'Antwerpen (Deurne)')

  eb = helper.provincie_cleansing(eb, 'Gemeente Cleansed', 'Provincie_EB')

  eb['Provincie Cleansed'] = eb['Provincie Cleansed'].replace('nan', np.nan)

  eb[['KBO_EB Cleansed', 'KBO_EB Comment']] = pd.DataFrame(eb['KBO_EB'].astype(str).apply(helper.kbo_cleansing).values.tolist(), columns=['kbo_cleansed','comment'])
  
  eb['organization_id'] = eb['KBO_EB Cleansed'].fillna(eb['Titel Cleansed'])

  eb[['Huisnr Cleansed', 'Busnummer Cleansed', 'Huisnr_EB Comment']] = pd.DataFrame(eb['Huisnr_EB'].astype(str).apply(helper.split_house_bus_number).values.tolist(), columns=['house_number', 'bus_number', 'comment'])

  eb[['Postcode Cleansed', 'Postcode_EB Comment']] = pd.DataFrame(eb['Postcode_EB'].astype(str).apply(helper.postcode_cleansing).values.tolist(), columns=['postcode_cleansed','comment'])

  eb['Straat'] = eb['Straat_EB'].replace('x000D_', '').replace('<br>', '').str.strip()

  eb[['Verkiezingen17_Opmerkingen Cleansed', 'Verkiezingen17_Opmerkingen Comment']] = pd.DataFrame(eb['Verkiezingen17_Opmerkingen'].astype(str).apply(helper.voting_cleansing).values.tolist(), columns=['date_election','comment'])

  eb[['Verkiezingen2020_Opmerkingen Cleansed', 'Verkiezingen2020_Opmerkingen Comment']] = pd.DataFrame(eb['Verkiezingen2020_Opmerkingen'].astype(str).apply(helper.voting_cleansing).values.tolist(), columns=['date_election','comment'])

  eb['Type_eredienst Cleansed'] = eb['Type_eredienst_EB'].replace('Rooms-Katholiek Kathedraal', 'Rooms-Katholiek') 
  
  first_names = helper.load_possible_first_names()

  eb['Naam_voorzitter Cleansed'] = eb['Naam_voorzitter_EB'].replace('<br>', ' ').str.strip()
  
  eb[['Naam_voorzitter First', 'Naam_voorzitter Last', 'Naam_voorzitter Comment']] = pd.DataFrame(eb['Naam_voorzitter Cleansed'].astype(str).apply(helper.splitname, args=(first_names,)).values.tolist(), columns=['first', 'last', 'comment'])

  eb['Adres_voorzitter Cleansed'] = eb['Adres_voorzitter_EB'].replace('<br>', '').str.strip()

  eb[['Mail_voorzitter Cleansed', 'Mail_voorzitter Comment']] = pd.DataFrame(eb['Mail_voorzitter_EB'].astype(str).apply(helper.mail_cleansing).values.tolist(), columns=['mail_cleansed','comment'])

  eb[['Tel_voorzitter 1', 'Tel_voorzitter 2', 'Tel_voorzitter Comment']] = pd.DataFrame(eb['Tel_voorzitter_EB'].astype(str).apply(helper.telephone_number_cleansing).values.tolist(), columns=['telephone_number_1', 'telephone_number_2', 'comment'])

  eb['Naam_penningmeester Cleansed'] = eb['Naam_penningmeester_EB'].replace('<br>', '').str.strip()

  eb[['Naam_penningmeester First', 'Naam_penningmeester Last', 'Naam_penningmeester Comment']] = pd.DataFrame(eb['Naam_penningmeester Cleansed'].astype(str).apply(helper.splitname, args=(first_names,)).values.tolist(), columns=['first', 'last', 'comment'])

  eb['Adres_penningmeester Cleansed'] = eb['Adres_penningmeester_EB'].replace('<br>', '').str.strip()

  eb[['Mail_penningmeester Cleansed', 'Mail_penningmeester Comment']] = pd.DataFrame(eb['Mail_penningmeester_EB'].astype(str).apply(helper.mail_cleansing).values.tolist(), columns=['mail_cleansed','comment'])

  eb[['Tel_penningmeester 1', 'Tel_penningmeester 2', 'Tel_penningmeester Comment']] = pd.DataFrame(eb['Tel_penningmeester_EB'].astype(str).apply(helper.telephone_number_cleansing).values.tolist(), columns=['telephone_number_1', 'telephone_number_2', 'comment'])

  eb['Naam_secretaris Cleansed'] = eb['Naam_secretaris_EB'].replace('<br>', '').str.strip()
  
  eb[['Naam_secretaris First', 'Naam_secretaris Last', 'Naam_secretaris Comment']] = pd.DataFrame(eb['Naam_secretaris Cleansed'].astype(str).apply(helper.splitname, args=(first_names,)).values.tolist(), columns=['first', 'last', 'comment'])

  eb['Adres_secretaris Cleansed'] = eb['Adres_secretaris_EB'].replace('<br>', '').str.strip()

  eb[['Mail_secretaris Cleansed', 'Mail_secretaris Comment']] = pd.DataFrame(eb['Mail_secretaris_EB'].astype(str).apply(helper.mail_cleansing).values.tolist(), columns=['mail_cleansed','comment'])

  eb[['Tel_secretaris 1', 'Tel_secretaris 2', 'Tel_secretaris Comment']] = pd.DataFrame(eb['Tel_secretaris_EB'].astype(str).apply(helper.telephone_number_cleansing).values.tolist(), columns=['telephone_number_1', 'telephone_number_2', 'comment'])

  eb['Naam_Lid4 Cleansed'] = eb['Naam_Lid4'].replace('<br>', '').str.strip()
  
  eb[['Naam_Lid4 First', 'Naam_Lid4 Last', 'Naam_Lid4 Comment']] = pd.DataFrame(eb['Naam_Lid4 Cleansed'].astype(str).apply(helper.splitname, args=(first_names,)).values.tolist(), columns=['first', 'last', 'comment'])

  eb['Naam_Lid5 Cleansed'] = eb['Naam_Lid5'].replace('<br>', '').str.strip()
  
  eb[['Naam_Lid5 First', 'Naam_Lid5 Last', 'Naam_Lid5 Comment']] = pd.DataFrame(eb['Naam_Lid5 Cleansed'].astype(str).apply(helper.splitname, args=(first_names,)).values.tolist(), columns=['first', 'last', 'comment'])
  
  eb['Datum verkiezing penningmeester'] = eb['Datum verkiezing penningmeester'].replace(' ', np.nan)

  eb['Datum verkiezing Lid4'] = eb['Datum verkiezing lid 4']

  eb['Datum verkiezing Lid5'] = eb['Datum verkiezing lid 5']

  return eb