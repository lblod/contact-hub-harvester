import pandas as pd
import numpy as np
import dateparser
import hashlib
from rdflib import Graph, Literal, RDF, URIRef, Namespace 
from rdflib.namespace import FOAF , XSD, DC, FOAF, SKOS, RDF, RDFS
import urllib.parse 
import io
import re

def concept_uri(base_uri, input):
  m = hashlib.md5()
  m.update(input.encode('utf-8'))

  return URIRef(base_uri + m.hexdigest())

def add_literal(g, subject, predicate, object_value, datatype=None):
  if object_value != str(np.nan):
    if datatype == None:
      g.add((subject, predicate, Literal(object_value, lang='nl')))
    else:
      g.add((subject, predicate, Literal(object_value, datatype=datatype)))

def space_cleansing(space):
  return re.sub(r'\s', '', space)

def split_house_bus_number(house_bus_number):
  house_number = bus_number = np.NaN
  comment = []
  house_bus_number = house_bus_number.replace(' ', '')

  if ('z/n' not in house_bus_number and 'nan' not in house_bus_number) : 
    if ('bus' in house_bus_number or '/' in house_bus_number):
      comment.append('Splitting. Check it.')
      if ('bus' in house_bus_number) : 
        split = house_bus_number.split('bus')
      else :
        split = house_bus_number.split('/')
      house_number = split[0]
      bus_number = split[1]
    else:
        house_number = house_bus_number
    house_number =  house_number.replace('/', '').replace('-', '').replace(',', '')
      
  return [house_number, bus_number, ' - '.join(comment)]

def postcode_cleansing(postcode):
  postcode_cleansed = comment = np.NaN

  if postcode != 'nan':
    postcode = re.sub(r'\D', '', postcode)
    if  re.match(r'\d{4}', postcode):
      postcode_cleansed = postcode
    else: 
      comment = 'Wrong postcode format. Check it.'

  return [postcode_cleansed, comment]

def load_gp():
  return pd.read_excel('input/gemeente-provincie.xlsx', sheet_name='Feuil2')

def find_city_provincie(gp, city):
  return gp[gp['Gemeente'].str.contains(city)]

def provincie_cleansing(data, gemeentee, provincie):
  gp = load_gp()

  data['Provincie Cleansed'] = None
  data['Provincie Comment'] = None

  for index, row in data.iterrows():
    city = str(row[gemeentee])
    result = find_city_provincie(gp, city)
    
    if len(result) > 0:
      if str(result.iloc[0]['Provincie']) != str(row[provincie]):
        data.at[index, 'Provincie Cleansed'] = result.iloc[0]['Provincie'].strip().title()
        data.at[index, 'Provincie Comment'] = "Different Provincie"
      else:
        data.at[index, 'Provincie Cleansed'] = str(row[provincie])
    elif city != 'nan':
      data.at[index, 'Provincie Comment'] = "Municipality Not Found"
      data.at[index, 'Provincie Cleansed'] = str(row[provincie])
  return data

def mail_cleansing(mail):
  mail_cleansed = comment = np.NaN

  if mail != 'nan':
    if  re.match(r'[\w\.-]+@[\w\.-]+(\.[\w]+)+', mail):
      mail_cleansed = mail
    else: 
      comment = 'Wrong mail format. Check it.'

  return [mail_cleansed, comment]

def website_cleansing(website):
  website_cleansed = comment = np.nan

  if website != 'nan':
    if  re.match(r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)', website):
      website_cleansed = website
    else: 
      comment = 'Wrong website format. Check it.'

  return [website_cleansed, comment]

def telephone_number_cleansing(telephone_number):
  telephone_number = re.sub(r'\s', '', telephone_number)

  telephone_number = re.sub(r'tel:', '', telephone_number)
  telephone_number = re.sub(r'tel', '', telephone_number)
  telephone_number = re.sub(r'<br>', '', telephone_number)

  telephone_number = re.sub(r'^\+32-\(0\)', '0', telephone_number)
  telephone_number = re.sub(r'^\+32', '0', telephone_number)
  telephone_number = re.sub(r'^32', '0', telephone_number)

  telephone_number = re.sub(r'^\+0032-\(0\)', '0', telephone_number)
  telephone_number = re.sub(r'^0032-\(0\)', '0', telephone_number)
  telephone_number = re.sub(r'^0032', '0', telephone_number)

  telephone_number = re.sub(r'^\(\d\d\d\)', '0', telephone_number)
  telephone_number = re.sub(r'^0\(\d\d\d\)', '0', telephone_number)

  telephone_number =  re.sub(r'[\.a-zA-Z]', '', telephone_number)

  return split_telephone_number(telephone_number)

def split_telephone_number(telephone_number):
  telephone_number_1 = telephone_number_2 = np.NaN
  comment = []

  split = [telephone_number]
  if '//' in telephone_number:
    split = telephone_number.split('//')
  elif '-' in telephone_number:
    split = telephone_number.split('-')
  elif ';' in telephone_number:
    split = telephone_number.split(';')
  elif 'enGSM:' in telephone_number:
    split = telephone_number.split('enGSM:')

  split[0] = split[0].replace('/', '')

  if telephone_number != '' :
    if check_telephone_number_lenght(split[0]):
      telephone_number_1 = split[0]
    else:
      comment.append('Wrong telephone number lenght. Check it.')

    if len(split) == 2 :
      comment.append('Splitting. Check it.')
      split[1] = split[1].replace('/', '')
      if check_telephone_number_lenght(split[1]):
        telephone_number_2 = split[1]
      else:
        comment.append('Wrong telephone 2 number lenght. Check it.')

  return [telephone_number_1, telephone_number_2, ' - '.join(comment)]

def check_telephone_number_lenght(telephone_number):
  if  len(telephone_number) < 9 or len(telephone_number) > 10:
    return False
  else:
    return True

def date_cleansing(date):
    dates_parsed = []

    if date != "nan":
      print(">> " + date)
      
      match = re.findall(r'\d{1,2}.\d{1,2}.\d{2,4}', date)
      if match:
        for m in match:
          date_parsed_match = dateparser.parse(m, settings={'DATE_ORDER': 'DMY'})
          dates_parsed.append(date_parsed_match)

      match = re.findall(r'\d{1,2} \w* \d{2,4}', date)
      if match:
        for m in match:
          date_parsed_match = dateparser.parse(m, settings={'DATE_ORDER': 'DMY'})
          dates_parsed.append(date_parsed_match)

      for item in dates_parsed:
          print("..." + str(item))

    return dates_parsed

def kbo_cleansing(kbo):

  kbo_cleansed = comment = np.nan

  if kbo != 'nan':
    kbo = re.sub(r'\D', '', kbo)
    if  re.match(r'\d{10}', kbo):
      kbo_cleansed = kbo
    elif re.match(r'\d{1,9}', kbo):
      kbo_cleansed = kbo
      comment = f'only {len(kbo)} digits. Missing some digits?'
    else: 
      comment = 'Wrong KBO format. Check it.'
  else :
    comment = 'No KBO nr found'

  return [kbo_cleansed, comment]

def load_possible_first_names():
  # using statbel firstnames of newborns (heuristic)
  m = pd.read_excel('input/Voornamen_Jongens_1995-2017_0.xls', sheet_name='1995-2019')
  male_names = (m['Unnamed: 1'].append(m['Unnamed: 4']).append(m['Unnamed: 7']).append(m['Unnamed: 10'])).unique()
  f = pd.read_excel('input/Voornamen_meisjes_1995-2017.xls', sheet_name='1995-2019')
  female_names = (f['Unnamed: 1'].append(f['Unnamed: 4']).append(f['Unnamed: 7']).append(f['Unnamed: 10'])).unique()

  manual_entries = ['Friedo', 'Renilde', 'Jozef', 'Maria-André', 'Gedo', 'Yvo', 'Marie-Cecile', 'Fonny', 'Luciaan', 'Willy', 'Fredy']

  first_names = np.concatenate([male_names,female_names, manual_entries])

  first_names = np.delete(first_names, np.where(first_names == 'Van'))
  first_names = np.delete(first_names, np.where(first_names == 'Blomme'))

  return first_names

def is_known_first_name(potential_name, first_names):
  return potential_name in first_names

def remove_title(full_name):
  mv = re.compile('(mevr|dhr)[\.]?[\s]?', re.IGNORECASE)
  return mv.sub('', full_name)

def splitname(full_name, first_names):
  first = last = np.nan
  comment = []

  likely_last_names = ['Vos', 'Matthijs', 'Stevens', 'Maere', 'Rubens', 'Beer', 'Duran', 'Roos', 'Broos', 'Thijs', 'Perre', 'Joris', 'Winter', 'Claus', 'Thys', 'Massa', 'Roy']

  split = remove_title(full_name).split(' ')

  if len(split) == 1 : comment.append('Cannot split name')

  potential_first_last = is_known_first_name(split[0], first_names)
  potential_last_first = is_known_first_name(split[-1], first_names)

  if potential_first_last and potential_last_first:
    if split[-1] in likely_last_names:
      first = split[0]
      last = ' '.join(split[1:])
    elif split[0] in likely_last_names:
      first = split[-1]
      last = ' '.join(split[0:-1])
    comment.append('Ambiguous: two possible first names - {}'.format(full_name))
  elif potential_first_last:
    first = split[0]
    last = ' '.join(split[1:])
  elif potential_last_first:
    first = split[-1]
    last = ' '.join(split[0:-1])
  else:
    comment.append('No potential first name found - {}'.format(full_name))
    # print([full_name])
  return [first, last, ' - '.join(comment)]

def find_resulting_org(orgs, name, type_entiteit):
  if name == 'Puurs Sint-Amands':
    return orgs[(orgs['Unieke Naam'].str.contains('PUURS_SINT_AMANDS', flags=re.IGNORECASE, regex=True, na=False)) & (orgs['Organisatiestatus'] == 'Actief') & (orgs['Type Entiteit'] == type_entiteit)]
  elif type_entiteit == 'Gemeente':
    return orgs[(orgs['Unieke Naam'].str.contains('G_' + name, flags=re.IGNORECASE, regex=True, na=False)) & (orgs['Organisatiestatus'] == 'Actief')]
  else:
    return orgs[(orgs['Unieke Naam'].str.contains('O_' + name, flags=re.IGNORECASE, regex=True, na=False)) & (orgs['Organisatiestatus'] == 'Actief')]

def org_status_cleansing(orgs):
  orgs['Resulting organisation'] = None

  for index, row in orgs[orgs['Organisatiestatus'] == 'gefusioneerd'].iterrows():
    if str(row['Opmerkingen ivm Organisatie']).startswith('Fusie'):
      resulting_city = row['Opmerkingen ivm Organisatie'].split('tot')[-1].strip()
      obj_resulting_org = find_resulting_org(orgs, resulting_city, row['Type Entiteit'])
      orgs.at[index, 'Resulting organisation'] = str(obj_resulting_org.iloc[0]['KBOnr_cleansed'])

  return orgs

def voting_2020_cleansing(data):
  for index, row in data.iterrows():
    date = str(row['Verkiezingen2020_Opmerkingen'])
    
    if date != 'nan':
      dates_parsed = date_cleansing(date)

      if dates_parsed :
        eb.at[index, 'Verkiezingen2020_Opmerkingen Cleansed'] = dates_parsed[0]
        if len(dates_parsed) > 1:
          comment = []
          for i in range(1, len(dates_parsed)):
            comment.append(str(dates_parsed[i]))
            eb.at[index, 'Verkiezingen2020_Opmerkingen Comment'] = ' - '.join(comment)
        else:
          eb.at[index, 'Verkiezingen2020_Opmerkingen Comment'] = np.NaN
      else:
        eb.at[index, 'Verkiezingen2020_Opmerkingen Cleansed'] = np.NaN

        eb['Verkiezingen2020_Opmerkingen Comment'] = data['Verkiezingen2020_Opmerkingen Comment'].astype(object)
        eb.at[index, 'Verkiezingen2020_Opmerkingen Comment'] = 'Wrong date format. Check it.'
  return data

def voting_2020_ckb_cleansing(data):
  for index, row in data.iterrows():
    date = str(row['Verkiezingen2020_Opmerkingen'])

    if date != "nan":
      dates_parsed = date_cleansing(date)
      if dates_parsed :
        ckb.at[index, 'Verkiezingen2020_Opmerkingen Cleansed'] = dates_parsed[0]
        if len(dates_parsed) > 1:
          comment = []
          for i in range(1, len(dates_parsed)):
            comment.append(str(dates_parsed[i]))
            ckb.at[index, 'Verkiezingen2020_Opmerkingen Comment'] = ' - '.join(comment)
        else:
          ckb.at[index, 'Verkiezingen2020_Opmerkingen Comment'] = np.NaN
      else:
        ckb.at[index, 'Verkiezingen2020_Opmerkingen Cleansed'] = np.NaN

        ckb['Verkiezingen2020_Opmerkingen Comment'] = data['Verkiezingen2020_Opmerkingen Comment'].astype(object)
        ckb.at[index, 'Verkiezingen2020_Opmerkingen Comment'] = 'Wrong date format. Check it.'

  return data

def voting_ckb_2017_cleansing(data):
  for index, row in data.iterrows():
    date = str(row['Verkiezingen17_Opmerkingen'])

    if date != 'nan':
      dates_parsed = date_cleansing(date)

      if dates_parsed :
        ckb.at[index, 'Verkiezingen17_Opmerkingen Cleansed'] = dates_parsed[0]
        if len(dates_parsed) > 1:
          comment = []
          for i in range(1, len(dates_parsed)):
            comment.append(str(dates_parsed[i]))
            ckb.at[index, 'Verkiezingen17_Opmerkingen Comment'] = ' - '.join(comment)
        else:
          ckb.at[index, 'Verkiezingen17_Opmerkingen Comment'] = np.NaN
      else:
        ckb.at[index, 'Verkiezingen17_Opmerkingen Cleansed'] = np.NaN

        ckb['Verkiezingen17_Opmerkingen Comment'] = data['Verkiezingen17_Opmerkingen Comment'].astype(object)
        ckb.at[index, 'Verkiezingen17_Opmerkingen Comment'] = 'Wrong date format. Check it.'

def voting_2017_cleansing(data):
  for index, row in data.iterrows():
    date = str(row['Verkiezingen17_Opmerkingen'])

    if date != 'nan':
      dates_parsed = date_cleansing(date)

      if dates_parsed :
        eb.at[index, 'Verkiezingen17_Opmerkingen Cleansed'] = dates_parsed[0]
        if len(dates_parsed) > 1:
          comment = []
          for i in range(1, len(dates_parsed)):
            comment.append(str(dates_parsed[i]))
            eb.at[index, 'Verkiezingen17_Opmerkingen Comment'] = ' - '.join(comment)
        else:
          eb.at[index, 'Verkiezingen17_Opmerkingen Comment'] = np.NaN
      else:
        eb.at[index, 'Verkiezingen17_Opmerkingen Cleansed'] = np.NaN

        eb['Verkiezingen17_Opmerkingen Comment'] = data['Verkiezingen17_Opmerkingen Comment'].astype(object)
        eb.at[index, 'Verkiezingen17_Opmerkingen Comment'] = 'Wrong date format. Check it.'
  return data

def exists_contact_org(row):
  return ((str(row['Website Cleansed']) != str(np.nan)) or (str(row['Algemeen telefoonnr']) != str(np.nan)) or (str(row['Algemeen mailadres']) != str(np.nan)))

def exists_address_org(row):
  return ((str(row['Straat']) != str(np.nan)) or (str(row['Huisnr_cleansed']) != str(np.nan)) or (str(row['Busnr_new']) != str(np.nan)) or
          (str(row['Postcode van de organisatie_cleansed']) != str(np.nan)) or (str(row['Gemeente van de organisatie']) != str(np.nan)) or
          (str(row['Provincie van de organisatie_cleansed']) != str(np.nan)))
  
def exists_site_org(row):
  return (exists_address_org(row) or exists_contact_org(row))

def exists_contact_cont(row):
  return ((str(row['Titel Cleansed']) != str(np.nan)) or (str(row['Mail nr2 Cleansed']) != str(np.nan)) or (str(row['Telefoonnr Contact 1']) != str(np.nan)))

def exists_site_central(row):
  return (exists_address_org(row) or exists_contact_org(row))

def exists_contact_central(row):
  return ((str(row['Website Cleansed']) != str(np.nan)) or (str(row['Algemeen telefoonnr']) != str(np.nan)) or (str(row['Algemeen mailadres']) != str(np.nan)))

def export_data(g):
  g.serialize('output.ttl',format='turtle')