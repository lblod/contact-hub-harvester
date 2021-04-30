import pandas as pd
import numpy as np
from datetime import datetime
import dateparser
import hashlib
from cleansing import central, contact, organization, worship
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import SKOS
import re

def concept_uri(base_uri, input):
  m = hashlib.md5()
  m.update(input.encode('utf-8'))

  return (URIRef(base_uri + m.hexdigest()), m.hexdigest())

def add_literal(g, subject, predicate, object_value, datatype=None):
  if object_value != str(np.nan):
    if datatype == None:
      g.add((subject, predicate, Literal(object_value, lang='nl')))
    else:
      g.add((subject, predicate, Literal(object_value, datatype=datatype)))

def status_mapping_central(status):
  status_dict = {'Operationeel': 'Actief', 'Niet actief - Samengevoegd n.a.v. een gemeentefusie': 'Niet Actief', 
                 'Operationeel – nieuw CKB n.a.v. gemeentefusie': 'Actief', 'Niet actief - opgeheven': 'Niet Actief',
                 'Niet actief - Niet van toepassing': 'Niet Actief', 'Niet actief - ontbreekt': 'Niet actief - ontbreekt'}

  return status_dict[status]

def status_mapping_worship(status):
  status_dict = {'Erkenningsaanvraag in behandeling': 'In oprichting', 'Operationeel': 'Actief', 'Niet actief - Samengevoegd (overgenomen)': 'Niet Actief',
                 'Operationeel - Samengevoegd (met behoud van naam)': 'Actief', 'Niet actief - Samengevoegd (nieuwe entiteit)': 'Niet Actief',
                 'Operationeel - Samengevoegd (met nieuwe naam)': 'Actief', 'Niet actief - Erkenning niet toegestaan': 'Niet Actief',
                 'Operationeel - Samenvoeging lopende':	'Actief', 'Niet actief - Ingetrokken': 'Niet Actief', 'Operationeel - Intrekkingsaanvraag lopende':	'Actief'}

  return status_dict[status]

def status_mapping_org(status):
  status_dict = {'Actief': 'Actief', 'Afgesloten (Vereffend)':  'Niet actief', 'Bijna Afgesloten (In ontbinding, ontbonden of in vereffening)': 'Niet actief',
                 'Formeel opgericht maar nog niet operationeel': 'Niet actief', 'gefusioneerd': 'Niet actief', 'In oprichting': 'Niet actief'}

  return status_dict[status]

def bestuursorgaan_mapping_central(type):
  bestuursorgaan_dict = {'Rooms-Katholiek': 'Centraal kerkbestuur', 'Orthodox': 'Centraal kerkbestuur', 'Islamitisch': 'Centraal bestuur'}

  return bestuursorgaan_dict[type]

def bestuursorgaan_mapping_worship(type):
  bestuursorgaan_dict = {'Rooms-Katholiek': 'Kerkraad', 'Rooms-Katholiek Kathedraal': 'Kathedrale kerkraad', 'Protestants': 'Bestuursraad', 'Orthodox': 'Kerkfabriekraad',
                         'Islamitisch': 'Comité', 'Israëlitisch': 'Bestuursraad', 'Anglicaans': 'Kerkraad', 'nan': 'nan'}

  return bestuursorgaan_dict[type]

def bestuurseenheid_mapping_org(type):
  bestuurseenheid_dict = {'AGB': 'Autonoom gemeentebedrijf', 'APB': 'Autonoom provinciebedrijf', 'HVZ': 'Hulpverleningszone', 'PZ': 'Politiezone', 
                          'IGS_PV': 'Projectvereniging', 'IGS_DV': 'Dienstverlenende vereniging', 'IGS_OV': 'Opdrachthoudende vereniging'}

  return bestuurseenheid_dict[type]
  
def load_graph(name):
  cl = Graph()

  cl.parse(f'input/codelists/{name}.ttl', format='ttl')

  return cl

def get_concept_id(graph, label):
  
  qres = graph.query('SELECT ?concept WHERE { ?concept skos:prefLabel ?label .}',
          initNs = { "skos": SKOS }, initBindings={'label': Literal(label)})
  
  return qres.bindings[0]['concept']

def get_label_role(role):
  label_role_dict = {'voorzitter worship':'Voorzitter van het bestuur van de eredienst', 'voorzitter central': 'Voorzitter van het centraal bestuur van de eredienst', 
  'secretaris worship': 'Secretaris van het bestuur van de eredienst', 'secretaris central': 'Secretaris van het centraal bestuur van de eredienst', 
  'penningmeester worship': 'Penningmeester van het bestuur van de eredienst', 'lid worship': 'Bestuurslid van het bestuur van de eredienst', 
  'lid central': 'Bestuurslid van het centraal bestuur van de eredienst'}

  return label_role_dict[role]

def space_cleansing(space):
  return re.sub(r'\s', '', space)

def naam_contact_cleansing(naam_contact):
  naam_contact_cleansed = comment = np.nan

  if naam_contact != 'nan':
    naam_contact = naam_contact.strip().title()

    if re.match(r'^[a-zA-ZàáâäãåąčćęèéêëėįìíîïłńòóôöõøùúûüųūÿýżźñçčšžÀÁÂÄÃÅĄĆČĖĘÈÉÊËÌÍÎÏĮŁŃÒÓÔÖÕØÙÚÛÜŲŪŸÝŻŹÑßÇŒÆČŠŽ∂ð \'’-]+$', naam_contact):
      naam_contact_cleansed = naam_contact
    else: 
      comment = 'Wrong naam format. Check it.'

  return [naam_contact_cleansed, comment]

def referentieorganisatie_cleansing(referentieorganisatie):
  return re.sub(r'\s', '', referentieorganisatie)

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

  if str(postcode) != str(np.nan):
    if re.match(r'\w', postcode):
      postcode_extract = re.sub(r'\D', '', postcode)
      comment = "Wrong postcode format. Check it."
      postcode_cleansed = postcode_extract
    elif  re.match(r'\d{4}', postcode):
      postcode_cleansed = postcode
    else: 
      comment = 'Wrong postcode format. Check it.'

  return [postcode_cleansed, comment]

def load_gp():
  return pd.read_excel('input/gemeente-provincie.xlsx', sheet_name='Feuil2')

def find_city_provincie(gp, city):
  return gp[gp['Gemeente'].str.contains(city)]

def provincie_cleansing(data, gemeentee_col, provincie_col):
  gp = load_gp()

  data['Provincie Cleansed'] = None
  data['Provincie Comment'] = None

  for index, row in data.iterrows():
    city = str(row[gemeentee_col])
    result = find_city_provincie(gp, city)
    
    if len(result) > 0:
      if str(result.iloc[0]['Provincie']).lower().strip() != str(row[provincie_col]).lower().strip():
        data.at[index, 'Provincie Cleansed'] = result.iloc[0]['Provincie'].strip().title()
        data.at[index, 'Provincie Comment'] = "Different Provincie"
      else:
        data.at[index, 'Provincie Cleansed'] = str(row[provincie_col])
    elif city != 'nan':
      data.at[index, 'Provincie Comment'] = "Municipality Not Found"
      data.at[index, 'Provincie Cleansed'] = str(row[provincie_col])
    else:
      data.at[index, 'Provincie Cleansed'] = np.nan

  
  return data

def mail_cleansing(mail):
  mail_cleansed = comment = np.nan

  if str(mail) != 'nan':
    if  re.match(r'[\w\.-]+@[\w\.-]+(\.[\w]+)+', mail):
      mail_cleansed = mail
    else: 
      comment = 'Wrong mail format. Check it.'

  return [mail_cleansed, comment]

def split_mail(mail):
  mail_voorzitter = mail_voorzitter_comment = mail_secretaris = mail_secretaris_comment = np.nan

  mails = []
  if str(mail) != 'nan':
    if 'V:' in mail:
      mail_voorzitter = mail[mail.find("V")+2:mail.find("S")].strip()
      mail_secretaris = mail[mail.find("S")+2:].strip()
    if ';' in mail:
      mails = mail.split(';')
    elif ' ' in mail:
      mails = mail.split(' ')
    else:
      mail_voorzitter = mail

    if len(mails) > 0:
      mail_voorzitter = mails[0].strip()
      mail_secretaris = mails[1].strip()

      mail_voorzitter, mail_voorzitter_comment = mail_cleansing(mail_voorzitter)

      if str(mail_secretaris) != 'nan' or len(mail_secretaris) > 0:
        mail_secretaris, mail_secretaris_comment = mail_cleansing(mail_secretaris)

  return [mail_voorzitter, mail_voorzitter_comment, mail_secretaris, mail_secretaris_comment]

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
  telephone_number_1 = telephone_number_2 = np.nan
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

def kbo_cleansing(kbo):

  kbo_cleansed = comment = np.nan

  if str(kbo) != str(np.nan):
    kbo = re.sub(r'\D', '', kbo)
    if  re.match(r'\d{10}', kbo):
      kbo_cleansed = kbo
    elif re.match(r'\d{6,9}', kbo):
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

def decretale_functie_cleasing(decretale):
  decretale_functie = functionaris_status = np.nan

  if 'Waarnemend' in decretale:
    status = decretale[decretale.find("("):decretale.find(")")+1]
    decretale_functie = decretale.replace(status, '').strip()
    functionaris_status = 'Waarnemend'
  elif 'GEEN of ONBEKEND' in decretale:
    decretale_functie = np.nan
  else:
    decretale_functie = decretale.strip()
    functionaris_status = 'Effectief'

  return [decretale_functie, functionaris_status]

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

def date_cleansing(date):
    dates_parsed = []

    if str(date) != str(np.nan):      
      match = re.findall(r'\d{1,2}.\d{1,2}.\d{2,4}', date)
      if match:
        for m in match:
          date_parsed_match = dateparser.parse(m, settings={'DATE_ORDER': 'DMY'}).isoformat()
          dates_parsed.append(date_parsed_match)

      match = re.findall(r'\d{1,2} \w* \d{2,4}', date)
      if match:
        for m in match:
          date_parsed_match = dateparser.parse(m, settings={'DATE_ORDER': 'DMY'}).isoformat()
          dates_parsed.append(date_parsed_match)

    return dates_parsed

def voting_cleansing(data, col_name):
  data[f'{col_name} Comment'] = None
  data[f'{col_name} Cleansed'] = None

  for index, row in data.iterrows():
    date = str(row[col_name])
    
    if date != str(np.nan):
      dates_parsed = date_cleansing(date)

      if dates_parsed:
        data.at[index, f'{col_name} Cleansed'] = dates_parsed[0]
        if len(dates_parsed) > 1:
          data.at[index, f'{col_name} Comment'] = ' - '.join([str(date) for date in dates_parsed[1:]])
        else:
          data.at[index, f'{col_name} Comment'] = np.nan
      else:
        data.at[index, f'{col_name} Cleansed'] = np.nan
        data[f'{col_name} Comment'] = data[f'{col_name} Comment'].astype(object)
        data.at[index, f'{col_name} Comment'] = 'Wrong date format. Check it.'

  return data

def exists_contact_org(row):
  return ((str(row['Website Cleansed']) != str(np.nan)) or (str(row['Algemeen telefoonnr']) != str(np.nan)) or (str(row['Algemeen mailadres']) != str(np.nan)))
  
def exists_site_org(row):
  return (exists_address(row) or exists_contact_org(row))

def exists_contact_cont(row):
  return ((str(row['Titel Cleansed']) != str(np.nan)) or (str(row['Mail nr2 Cleansed']) != str(np.nan)) or (str(row['Telefoonnr Contact 1']) != str(np.nan)))

def exists_role(row, role):
  return (str(row[f'Naam_{role} First']) != str(np.nan)) or (str(row[f'Naam_{role} Last']) != str(np.nan))

def exists_address(row):
  return ((str(row['Straat']) != str(np.nan)) or (str(row['Huisnr Cleansed']) != str(np.nan)) or (str(row['Busnummer Cleansed']) != str(np.nan)) or
          (str(row['Postcode Cleansed']) != str(np.nan)) or (str(row['Gemeente Cleansed']) != str(np.nan)) or (str(row['Provincie Cleansed']) != str(np.nan)))

def exists_site_role(row, role):
  return exists_address_role(row, role) or exists_contact_role(row, role)

def exists_address_role(row, role):
  return (str(row[f'Adres_{role} Cleansed']) != str(np.nan))

def exists_contact_role(row, role):
  return ((str(row[f'Tel_{role} 1']) != str(np.nan)) or (str(row[f'Mail_{role} Cleansed']) != str(np.nan)))

def exists_bestuursperiode(row, roles):
  for role in roles:
    if exists_role(row, role):
      return True
  
  return False

def get_cleansed_data(file, type):
  try:
    data_cleansed = pd.read_excel(f'output/{type}_cleansed.xlsx')
  except FileNotFoundError:
    data_raw = pd.read_excel(file)
    
    print("########### Cleansing started #############")

    if type == 'worship':    
      data_cleansed = worship.main(data_raw)
    elif type == 'central':
      data_cleansed = central.main(data_raw)
    elif type == 'org':
      data_cleansed = organization.main(data_raw)
    else:
      data_cleansed = contact.main(data_raw)

    print("########### Cleansing finished #############")

    export_df(data_cleansed, type)    

  return data_cleansed

def export_data(g, type):
  now = datetime.now().strftime('%Y%m%d%H%M%S')
  g.serialize(f'output/{now}-{type}.ttl',format='turtle')

  f = open(f'output/{now}-{type}.graph', 'w')
  f.write("http://mu.semte.ch/graphs/public")
  f.close()

def export_df(data, type):
  data.to_excel(f'output/{type}_cleansed.xlsx', index=False)