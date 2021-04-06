import helper.functions as helper
import pandas as pd

def main(orgs):
  orgs[['KBOnr_cleansed', 'KBOnr_comment']] = pd.DataFrame(orgs['KBOnr'].astype(str).apply(helper.kbo_cleansing).values.tolist(), columns=['kbo_cleansed','comment'])
  
  return orgs