import helper.functions as helper
import pandas as pd
import numpy as np

def main(orgs):
  orgs[['KBOnr_cleansed', 'KBOnr_comment']] = pd.DataFrame(orgs['KBOnr'].astype(str).apply(helper.kbo_cleansing).values.tolist(), columns=['kbo_cleansed','comment'])
  
  orgs['organisation_id'] = orgs['KBOnr_cleansed'].fillna(orgs['Unieke Naam'])

  orgs[['Website Cleansed', 'Website Comment']] = pd.DataFrame(orgs['Website'].astype(str).apply(helper.website_cleansing).values.tolist(), columns=['website_cleansed','comment'])

  orgs[['Huisnr_cleansed', 'Busnr_new', 'Huisnr_comment']] = pd.DataFrame(orgs['Huisnr'].astype(str).apply(helper.split_house_bus_number).values.tolist(), columns=['house_number', 'bus_number', 'comment'])

  orgs['Postcode van de organisatie_cleansed'] = orgs['Postcode van de organisatie'].astype(str).str.replace('\.0', '').replace('nan', np.nan)

  orgs['NIScode_cleansed'] = orgs['NIScode'].astype(str).str.replace('\.0', '').replace('nan', np.nan)

  return orgs