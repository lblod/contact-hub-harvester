import helper.functions as helper
import pandas as pd
import numpy as np
import re

def main(ckb):
  ckb['Status_CKB'] = ckb['Status_CKB'].replace('Niet actief - niet van toepassing', 'Niet actief - Niet van toepassing').replace('Niet actief – Opgeheven (door MB)', 'Niet actief - opgeheven')
  
  #ckb = ckb.drop(ckb[ckb['Status_CKB'].str.contains('Niet actief - ontbreekt')].index.tolist())

  ckb['Status_CKB_cleansed'] = pd.Series(ckb['Status_CKB'].astype(str).apply(helper.status_mapping_central).values)
  
  ckb['Bestuursorgaan Type'] = pd.Series(ckb['Type_eredienst_CKB'].astype(str).apply(helper.bestuursorgaan_mapping_central).values)
  
  ckb['KBO_CKB_cleansed'] = ckb['KBO_CKB'].str.replace(r'\D', '')

  ckb[['KBO_CKB_cleansed', 'KBO_CKB_comment']] = pd.DataFrame(ckb['KBO_CKB'].astype(str).apply(helper.kbo_cleansing).values.tolist(), columns=['kbo_cleansed','comment'])

  ckb['Straat'] = ckb['Straat_CKB'].str.strip().str.title().str.replace('--', 'nan') 

  ckb[['Huisnr Cleansed', 'Busnummer Cleansed', 'Huisnr_CKB_Comment']] = pd.DataFrame(ckb['Huisnr_CKB'].astype(str).apply(helper.split_house_bus_number).values.tolist(), columns=['house_number', 'bus_number', 'comment'])

  ckb = helper.provincie_cleansing(ckb, 'Gemeente_CKB', 'Provincie_CKB')

  ckb[['Postcode Cleansed', 'Postcode_CKB Comment']] = pd.DataFrame(ckb['Postcode_CKB'].astype(str).apply(helper.postcode_cleansing).values.tolist(), columns=['postcode_cleansed','comment'])
  
  ckb['Gemeente Cleansed'] = ckb['Gemeente_CKB'].str.strip().str.title()

  ckb['Naam_voorzitter_cleansed'] = ckb['Naam_Voorzitter_CKB'].str.replace('<br>', '').str.strip()
  ckb['Naam_secretaris_cleansed'] = ckb['Naam_secretaris_CKB'].str.replace('<br>', '').str.strip()

  first_names = helper.load_possible_first_names()

  ckb[['Naam_voorzitter First', 'Naam_voorzitter Last', 'Naam_voorzitter Comment']] = pd.DataFrame(ckb['Naam_voorzitter_cleansed'].astype(str).apply(helper.splitname, args=(first_names,)).values.tolist(), columns=['first', 'last', 'comment'])

  ckb[['Naam_secretaris First', 'Naam_secretaris Last', 'Naam_secretaris Comment']] = pd.DataFrame(ckb['Naam_secretaris_cleansed'].astype(str).apply(helper.splitname, args=(first_names,)).values.tolist(), columns=['first', 'last', 'comment'])
  
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