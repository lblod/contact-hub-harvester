import helper.functions as helper
import pandas as pd
import numpy as np

def main(ckb):
  ckb['Status_CKB_cleansed'] = ckb['Status_CKB'].replace(to_replace='Niet actief - niet van toepassing', value='Niet actief - Niet van toepassing')

  ckb['KBO_CKB_cleansed'] = ckb['KBO_CKB'].str.replace(r'\D', '')

  ckb[['KBO_CKB_cleansed', 'KBO_CKB_comment']] = pd.DataFrame(ckb['KBO_CKB'].astype(str).apply(helper.kbo_cleansing).values.tolist(), columns=['kbo_cleansed','comment'])

  ckb['organization_id'] = ckb['KBO_CKB_cleansed'].fillna(ckb['Titel'])

  ckb[['Huisnr_CKB_Cleansed', 'Busnummer_CKB_Cleansed', 'Huisnr_CKB_Comment']] = pd.DataFrame(ckb['Huisnr_CKB'].astype(str).apply(helper.split_house_bus_number).values.tolist(), columns=['house_number', 'bus_number', 'comment'])

  ckb['Naam_Voorzitter_CKB_cleansed'] = ckb['Naam_Voorzitter_CKB'].str.replace('<br>', '').str.strip()
  ckb['Naam_secretaris_CKB_cleansed'] = ckb['Naam_secretaris_CKB'].str.replace('<br>', '').str.strip()

  ckb[['Naam_Voorzitter_CKB_first', 'Naam_Voorzitter_CKB_last', 'Naam_Voorzitter_CKB_comment']] = pd.DataFrame(ckb['Naam_Voorzitter_CKB_cleansed'].astype(str).apply(helper.splitname).values.tolist(), columns=['first', 'last', 'comment'])

  ckb[['Naam_secretaris_CKB_first', 'Naam_secretaris_CKB_last', 'Naam_secretaris_CKB_comment']] = pd.DataFrame(ckb['Naam_secretaris_CKB_cleansed'].astype(str).apply(helper.splitname).values.tolist(), columns=['first', 'last', 'comment'])

  ckb[['Naam_Voorzitter_CKB_first', 'Naam_Voorzitter_CKB_last', 'Naam_Voorzitter_CKB_comment']] = pd.DataFrame(ckb['Naam_Voorzitter_CKB_cleansed'].astype(str).apply(helper.splitname).values.tolist(), columns=['first', 'last', 'comment'])

  ckb[['Naam_Voorzitter_CKB', 'Naam_Voorzitter_CKB_first', 'Naam_Voorzitter_CKB_last', 'Naam_Voorzitter_CKB_comment', 'Naam_secretaris_CKB', 'Naam_secretaris_CKB_first', 'Naam_secretaris_CKB_last', 'Naam_secretaris_CKB_comment']]

  ckb[['Mail_CKB_Cleansed', 'Mail_CKB_Comment']] = pd.DataFrame(ckb['Mail_CKB'].astype(str).apply(helper.mail_cleansing).values.tolist(), columns=['mail_cleansed','comment'])

  ckb[['Tel_CKB_voorzitter_1', 'Tel_CKB_voorzitter_2', 'Tel_CKB_voorzitter_Comment']] = pd.DataFrame(ckb['Tel_CKB_voorzitter'].astype(str).apply(helper.telephone_number_cleansing).values.tolist(), columns=['telephone_number_1', 'telephone_number_2', 'comment'])

  ckb[['Tel_CKB_secretaris_1', 'Tel_CKB_secretaris_2', 'Tel_CKB_secretaris_Comment']] = pd.DataFrame(ckb['Tel_CKB_secretaris'].astype(str).apply(helper.telephone_number_cleansing).values.tolist(), columns=['telephone_number_1', 'telephone_number_2', 'comment'])


  return ckb