import helper.functions as helper
import pandas as pd

def main(worship):
  worship[['Titel Cleansed']] = pd.DataFrame(worship['Titel'].astype(str).apply(helper.space_cleansing).values.tolist())

  worship['Gemeente_EB Cleansed'] = worship['Gemeente_EB'].str.strip().str.title().replace('Antwerpen (Deurne', 'Antwerpen (Deurne)')

  worship[['KBOnr_cleansed', 'KBOnr_comment']] = pd.DataFrame(worship['KBOnr'].astype(str).apply(helper.kbo_cleansing).values.tolist(), columns=['kbo_cleansed','comment'])
  
  return worship