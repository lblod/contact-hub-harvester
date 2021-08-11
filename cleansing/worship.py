import helper.functions as helper
import pandas as pd
import numpy as np

def main(eb):
  eb['Change Event Cleansed'] = pd.Series(eb[['Status_EB', 'Statusinfo']].astype(str).apply(helper.change_event_cleansing, axis=1).values)
  
  eb['Status_EB Cleansed'] = pd.Series(eb['Status_EB'].astype(str).apply(helper.status_mapping_worship).values)

  eb['Bestuursorgaan Type'] = pd.Series(eb['Type_eredienst_EB'].astype(str).apply(helper.bestuursorgaan_mapping_worship).values)

  eb['Type_eredienst Cleansed'] = eb['Type_eredienst_EB'].str.replace('Rooms-Katholiek Kathedraal', 'Rooms-Katholiek')

  eb['Gemeente Cleansed'] = eb['Gemeente_EB'].str.strip().str.title().replace('Antwerpen (Deurne', 'Antwerpen (Deurne)')

  eb[['Gemeente Cleansed', 'Gemeente Comment']] = pd.DataFrame(eb['Gemeente Cleansed'].astype(str).apply(helper.gemeente_cleansing).values.tolist(), columns=['gemeente_cleansed', 'comment'])

  eb[['Provincie Cleansed', 'Provincie Comment']] = pd.DataFrame(eb[['Gemeente Cleansed', 'Provincie_EB']].astype(str).apply(helper.provincie_cleansing, axis=1).values.tolist(), columns=['provincie_cleansed', 'comment'])

  eb['Provincie Cleansed'] = eb['Provincie Cleansed'].replace('nan', np.nan)

  eb['Local Engagement Cleansed'] = pd.Series(eb[['Opmerkingen_EB', 'Grensoverschrijdend', 'Provincie Cleansed', 'Gemeente Cleansed', 'Type_eredienst Cleansed']].astype({'Opmerkingen_EB': str, 'Grensoverschrijdend': bool, 'Provincie Cleansed': str, 'Gemeente Cleansed': str, 'Type_eredienst Cleansed': str}).apply(helper.local_engagement_cleansing, axis=1).values)

  eb['Strekking Cleansed'] = eb['Strekking'].str.replace('Denominatie: ', '').str.replace('denominatie ', '').str.strip()

  eb[['KBO_EB Cleansed', 'KBO_EB Comment']] = pd.DataFrame(eb['KBO_EB'].astype(str).apply(helper.kbo_cleansing).values.tolist(), columns=['kbo_cleansed','comment'])
  
  eb['organization_id'] = eb['KBO_EB Cleansed'].fillna(eb['Titel'])

  eb[['Huisnr Cleansed', 'Busnummer Cleansed', 'Huisnr_EB Comment']] = pd.DataFrame(eb['Huisnr_EB'].astype(str).apply(helper.split_house_bus_number).values.tolist(), columns=['house_number', 'bus_number', 'comment'])

  eb[['Postcode Cleansed', 'Postcode_EB Comment']] = pd.DataFrame(eb['Postcode_EB'].astype(str).apply(helper.postcode_cleansing).values.tolist(), columns=['postcode_cleansed','comment'])

  eb['Straat'] = eb['Straat_EB'].str.replace('_x000D_', '').str.replace('<br>', ' ').str.strip()

  eb[['Verkiezingen17_Opmerkingen Cleansed', 'Verkiezingen17_Opmerkingen Comment']] = pd.DataFrame(eb['Verkiezingen17_Opmerkingen'].astype(str).apply(helper.voting_cleansing).values.tolist(), columns=['date_election','comment'])

  eb[['Verkiezingen2020_Opmerkingen Cleansed', 'Verkiezingen2020_Opmerkingen Comment']] = pd.DataFrame(eb['Verkiezingen2020_Opmerkingen'].astype(str).apply(helper.voting_cleansing).values.tolist(), columns=['date_election','comment'])

  eb['Representatief orgaan'] = pd.Series(eb[['Type_eredienst Cleansed','Provincie Cleansed','Gemeente Cleansed']].astype(str).apply(helper.worship_link_ro, axis=1).values)
  
  first_names = helper.load_possible_first_names()

  eb['Naam_voorzitter Cleansed'] = eb['Naam_voorzitter_EB'].str.replace('<br>', ' ').str.strip()
  
  eb[['Naam_voorzitter First', 'Naam_voorzitter Last', 'Naam_voorzitter Comment']] = pd.DataFrame(eb['Naam_voorzitter Cleansed'].astype(str).apply(helper.splitname, args=(first_names,)).values.tolist(), columns=['first', 'last', 'comment'])

  eb['Naam_voorzitter First'] = eb['Naam_voorzitter First'].str.strip()

  eb['Naam_voorzitter Last'] = eb['Naam_voorzitter Last'].str.strip()
  
  eb['Adres_voorzitter Cleansed'] = eb['Adres_voorzitter_EB'].str.replace('<br>', ' ').str.replace('_x000D_', '').str.strip()

  eb['Mail_voorzitter_EB'] = eb['Mail_voorzitter_EB'].str.replace('<br>', ' ').str.strip()

  eb[['Mail_voorzitter Cleansed', 'Mail_voorzitter Comment']] = pd.DataFrame(eb['Mail_voorzitter_EB'].astype(str).apply(helper.mail_cleansing).values.tolist(), columns=['mail_cleansed','comment'])

  eb[['Tel_voorzitter 1', 'Tel_voorzitter 2', 'Tel_voorzitter Comment']] = pd.DataFrame(eb['Tel_voorzitter_EB'].astype(str).apply(helper.telephone_number_cleansing).values.tolist(), columns=['telephone_number_1', 'telephone_number_2', 'comment'])

  eb['Type Helft Cleansed voorzitter'] = eb['Grote helft/kleine helft voorzitter'].replace('Onbekend', np.nan)
  
  eb['Naam_penningmeester Cleansed'] = eb['Naam_penningmeester_EB'].str.replace('<br>', ' ').str.strip()

  eb[['Naam_penningmeester First', 'Naam_penningmeester Last', 'Naam_penningmeester Comment']] = pd.DataFrame(eb['Naam_penningmeester Cleansed'].astype(str).apply(helper.splitname, args=(first_names,)).values.tolist(), columns=['first', 'last', 'comment'])

  eb['Naam_penningmeester First'] = eb['Naam_penningmeester First'].str.strip()

  eb['Naam_penningmeester Last'] = eb['Naam_penningmeester Last'].str.strip()
  
  eb['Adres_penningmeester Cleansed'] = eb['Adres_penningmeester_EB'].str.replace('<br>', ' ').str.replace('_x000D_', '').str.strip()

  eb['Mail_penningmeester_EB'] = eb['Mail_penningmeester_EB'].str.replace('<br>', ' ').str.strip()

  eb[['Mail_penningmeester Cleansed', 'Mail_penningmeester Comment']] = pd.DataFrame(eb['Mail_penningmeester_EB'].astype(str).apply(helper.mail_cleansing).values.tolist(), columns=['mail_cleansed','comment'])

  eb[['Tel_penningmeester 1', 'Tel_penningmeester 2', 'Tel_penningmeester Comment']] = pd.DataFrame(eb['Tel_penningmeester_EB'].astype(str).apply(helper.telephone_number_cleansing).values.tolist(), columns=['telephone_number_1', 'telephone_number_2', 'comment'])

  eb['Datum verkiezing penningmeester'] = eb['Datum verkiezing penningmeester'].replace(' ', np.nan)

  eb['Type Helft Cleansed penningmeester'] = eb['Grote helft/kleine helft penningmeester'].replace('Onbekend', np.nan)
  
  eb['Naam_secretaris Cleansed'] = eb['Naam_secretaris_EB'].str.replace('<br>', ' ').str.strip()
  
  eb[['Naam_secretaris First', 'Naam_secretaris Last', 'Naam_secretaris Comment']] = pd.DataFrame(eb['Naam_secretaris Cleansed'].astype(str).apply(helper.splitname, args=(first_names,)).values.tolist(), columns=['first', 'last', 'comment'])

  eb['Naam_secretaris First'] = eb['Naam_secretaris First'].str.strip()

  eb['Naam_secretaris Last'] = eb['Naam_secretaris Last'].str.strip()
  
  eb['Adres_secretaris Cleansed'] = eb['Adres_secretaris_EB'].str.replace('<br>', ' ').str.replace('_x000D_', '').str.strip()

  eb['Mail_secretaris_EB'] = eb['Mail_secretaris_EB'].str.replace('<br>', ' ').str.strip()

  eb[['Mail_secretaris Cleansed', 'Mail_secretaris Comment']] = pd.DataFrame(eb['Mail_secretaris_EB'].astype(str).apply(helper.mail_cleansing).values.tolist(), columns=['mail_cleansed','comment'])

  eb[['Tel_secretaris 1', 'Tel_secretaris 2', 'Tel_secretaris Comment']] = pd.DataFrame(eb['Tel_secretaris_EB'].astype(str).apply(helper.telephone_number_cleansing).values.tolist(), columns=['telephone_number_1', 'telephone_number_2', 'comment'])

  eb['Type Helft Cleansed secretaris'] = eb['Grote helft/kleine helft secretaris'].replace('Onbekend', np.nan) 

  eb['Naam_Lid4 Cleansed'] = eb['Naam_Lid4'].str.replace('<br>', '').str.strip()
  
  eb[['Naam_Lid4 First', 'Naam_Lid4 Last', 'Naam_Lid4 Comment']] = pd.DataFrame(eb['Naam_Lid4 Cleansed'].astype(str).apply(helper.splitname, args=(first_names,)).values.tolist(), columns=['first', 'last', 'comment'])

  eb['Naam_Lid4 First'] = eb['Naam_Lid4 First'].str.strip()

  eb['Naam_Lid4 Last'] = eb['Naam_Lid4 Last'].str.strip()
  
  eb['Naam_Lid5 Cleansed'] = eb['Naam_Lid5'].str.replace('<br>', ' ').str.strip()
  
  eb[['Naam_Lid5 First', 'Naam_Lid5 Last', 'Naam_Lid5 Comment']] = pd.DataFrame(eb['Naam_Lid5 Cleansed'].astype(str).apply(helper.splitname, args=(first_names,)).values.tolist(), columns=['first', 'last', 'comment'])

  eb['Naam_Lid5 First'] = eb['Naam_Lid5 First'].str.strip()

  eb['Naam_Lid5 Last'] = eb['Naam_Lid5 Last'].str.strip()
  
  eb['Datum verkiezing Lid4'] = eb['Datum verkiezing lid 4']

  eb['Type Helft Cleansed Lid4'] = eb['Grote helft/kleine helft lid 4'].replace('Onbekend', np.nan)

  eb['Datum verkiezing Lid5'] = eb['Datum verkiezing lid 5']

  eb['Type Helft Cleansed Lid5'] = eb['Grote helft/kleine helft lid 5'].replace('Onbekend', np.nan)

  return eb