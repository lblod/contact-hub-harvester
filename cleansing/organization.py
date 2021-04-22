import helper.functions as helper
import pandas as pd
import numpy as np

def main(orgs):
  orgs = orgs[orgs['Organisatiestatus'] != 'Valt niet meer onder Vlaams toezicht']

  orgs['Organisatiestatus cleansed'] = pd.DataFrame(orgs['Organisatiestatus'].astype(str).apply(helper.status_mapping_org).values.toList(), colums=['status_mapped'])

  orgs[['KBOnr_cleansed', 'KBOnr_comment']] = pd.DataFrame(orgs['KBOnr'].astype(str).apply(helper.kbo_cleansing).values.tolist(), columns=['kbo_cleansed','comment'])
  
  orgs['organisation_id'] = orgs['KBOnr_cleansed'].fillna(orgs['Unieke Naam'])

  orgs[['Website Cleansed', 'Website Comment']] = pd.DataFrame(orgs['Website'].astype(str).apply(helper.website_cleansing).values.tolist(), columns=['website_cleansed','comment'])

  orgs[['Huisnr Cleansed', 'Busnummer Cleansed', 'Huisnr_comment']] = pd.DataFrame(orgs['Huisnr'].astype(str).apply(helper.split_house_bus_number).values.tolist(), columns=['house_number', 'bus_number', 'comment'])

  orgs = helper.provincie_cleansing(orgs, 'Gemeente van de organisatie', 'Provincie van de organisatie')

  orgs['Gemeente Cleansed'] = orgs['Gemeente van de organisatie'].str.strip().title()

  orgs['Postcode Cleansed'] = orgs['Postcode van de organisatie'].astype(str).str.replace('\.0', '').replace('nan', np.nan)

  orgs['NIScode_cleansed'] = orgs['NIScode'].astype(str).str.replace('\.0', '').replace('nan', np.nan)

  orgs[~orgs['organisation_id'].isnull()]

  return orgs