import helper.functions as helper
import pandas as pd
import re

def main(ckb):
  ckb['Status_CKB'] = ckb['Status_CKB'].replace('Niet actief - niet van toepassing', 'Niet actief - Niet van toepassing').replace('Niet actief – Opgeheven (door MB)', 'Niet actief - opgeheven')

  ckb['Status_CKB_cleansed'] = pd.Series(ckb['Status_CKB'].astype(str).apply(helper.status_mapping_central).values)
  
  ckb['Bestuursorgaan Type'] = pd.Series(ckb['Type_eredienst_CKB'].astype(str).apply(helper.bestuursorgaan_mapping_central).values)
  
  ckb['KBO_CKB_cleansed'] = ckb['KBO_CKB'].replace(r'\D', '')

  ckb[['KBO_CKB_cleansed', 'KBO_CKB_comment']] = pd.DataFrame(ckb['KBO_CKB'].astype(str).apply(helper.kbo_cleansing).values.tolist(), columns=['kbo_cleansed','comment'])

  ckb['Straat'] = ckb['Straat_CKB'].str.strip().str.title().str.replace('--', 'nan') 

  ckb[['Huisnr Cleansed', 'Busnummer Cleansed', 'Huisnr_CKB_Comment']] = pd.DataFrame(ckb['Huisnr_CKB'].astype(str).apply(helper.split_house_bus_number).values.tolist(), columns=['house_number', 'bus_number', 'comment'])

  ckb[['Provincie Cleansed', 'Provincie Comment']] = pd.DataFrame(ckb[['Gemeente_CKB', 'Provincie_CKB']].astype(str).apply(helper.provincie_cleansing, axis=1).values.tolist(), columns=['provincie_cleansed', 'comment'])

  ckb[['Postcode Cleansed', 'Postcode_CKB Comment']] = pd.DataFrame(ckb['Postcode_CKB'].astype(str).apply(helper.postcode_cleansing).values.tolist(), columns=['postcode_cleansed','comment'])
  
  ckb['Gemeente Cleansed'] = ckb['Gemeente_CKB'].str.strip().str.title()

  ckb[['Verkiezingen17_Opmerkingen Cleansed', 'Verkiezingen17_Opmerkingen Comment']] = pd.DataFrame(ckb['Verkiezingen17_Opmerkingen'].astype(str).apply(helper.voting_cleansing).values.tolist(), columns=['date_election','comment'])

  ckb[['Verkiezingen2020_Opmerkingen Cleansed', 'Verkiezingen2020_Opmerkingen Comment']] = pd.DataFrame(ckb['Verkiezingen2020_Opmerkingen'].astype(str).apply(helper.voting_cleansing).values.tolist(), columns=['date_election','comment'])

  ckb[['Opmerkingen_CKB Date', 'Opmerkingen_CKB Comment']] = pd.DataFrame(ckb['Opmerkingen_CKB'].astype(str).apply(helper.voting_cleansing).values.tolist(), columns=['date','comment'])

  ckb['Representatief orgaan'] = pd.Series(ckb[['Type_eredienst_CKB','Provincie Cleansed','Gemeente Cleansed']].astype(str).apply(helper.worship_link_ro, axis=1).values)

  ckb['Naam_voorzitter Cleansed'] = ckb['Naam_Voorzitter_CKB'].replace('<br>', '').str.strip()
  ckb['Naam_secretaris Cleansed'] = ckb['Naam_secretaris_CKB'].replace('<br>', '').str.strip()

  first_names = helper.load_possible_first_names()

  ckb[['Naam_voorzitter First', 'Naam_voorzitter Last', 'Naam_voorzitter Comment']] = pd.DataFrame(ckb['Naam_voorzitter Cleansed'].astype(str).apply(helper.splitname, args=(first_names,)).values.tolist(), columns=['first', 'last', 'comment'])

  ckb[['Naam_secretaris First', 'Naam_secretaris Last', 'Naam_secretaris Comment']] = pd.DataFrame(ckb['Naam_secretaris Cleansed'].astype(str).apply(helper.splitname, args=(first_names,)).values.tolist(), columns=['first', 'last', 'comment'])
  
  ckb[['Mail_voorzitter Cleansed', 'Mail_voorzitter Comment', 'Mail_secretaris Cleansed', 'Mail_secretaris Comment']] = pd.DataFrame(ckb['Mail_CKB'].astype(str).apply(helper.split_mail).values.tolist(), columns=['mail_voorzitter', 'mail_voorzitter_comment', 'mail_secretaris', 'mail_secretaris_comment'])

  ckb['Tel_voorzitter'] = ckb['Tel_CKB'].str.extract(r'([\d/ ]*)\s*\(\s*voorzitter\s*\)', flags=re.IGNORECASE) \
  .fillna(ckb['Tel_CKB'].str.extract(r'Voorzitter\s*:\s*([\d/ ]*)', flags=re.IGNORECASE)) \
  .fillna(ckb['Tel_CKB'].str.extract(r'V\s*:\s*([\d/ ]*)', flags=re.IGNORECASE)) \
  .fillna(ckb['Tel_CKB'].str.extract(r'([\d/ ]*)', flags=re.IGNORECASE))

  ckb['Tel_secretaris'] = ckb['Tel_CKB'].str.extract(r'([\d/ ]*)\s*\(\s*secretaris\s*\)', flags=re.IGNORECASE) \
  .fillna(ckb['Tel_CKB'].str.extract(r'Secretaris\s*:\s*([\d/ ]*)', flags=re.IGNORECASE)) \
  .fillna(ckb['Tel_CKB'].str.extract(r'S\s*:\s*([\d/ ]*)', flags=re.IGNORECASE)) \
  .fillna(ckb['Tel_CKB'].str.extract(r'([\d/ ]*)', flags=re.IGNORECASE))

  ckb[['Tel_voorzitter 1', 'Tel_voorzitter 2', 'Tel_voorzitter Comment']] = pd.DataFrame(ckb['Tel_voorzitter'].astype(str).apply(helper.telephone_number_cleansing).values.tolist(), columns=['telephone_number_1', 'telephone_number_2', 'comment'])

  ckb[['Tel_secretaris 1', 'Tel_secretaris 2', 'Tel_secretaris Comment']] = pd.DataFrame(ckb['Tel_secretaris'].astype(str).apply(helper.telephone_number_cleansing).values.tolist(), columns=['telephone_number_1', 'telephone_number_2', 'comment'])

  ckb = ckb[ckb['Status_CKB_cleansed'] != 'DELETE RECORD']

  return ckb