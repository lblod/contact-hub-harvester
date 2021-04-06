import sys

import mapping.organization as org
import mapping.contact as contact
import mapping.worship as worship
import mapping.central as central
import mapping.national as national

def main(input, type):
  if type == 'org':
    org.main(input)
  elif type == 'contact':
    contact.main(input)
  elif type == 'worship':
    worship.main(input)
  elif type == 'central':
    central.main(input)
  elif type == 'national':
    national.main(input)

if __name__ == '__main__':
  if len(sys.argv) > 1:
    file = sys.argv[1]
    type = sys.argv[2]
  
  main(file, type)
