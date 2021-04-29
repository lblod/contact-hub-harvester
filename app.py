import sys

import mapping.organization as org
import mapping.contact as contact
import mapping.worship as worship
import mapping.central as central
import mapping.national as national

import mapping.codelist as codelist

def main(*args):  
  if args[0] == 'org':
    org.main(args[1], args[2])
  elif args[0] == 'contact':
    contact.main(args[1], args[2])
  elif args[0] == 'worship':
    worship.main(args[1], args[2])
  elif args[0] == 'central':
    central.main(args[1], args[2])
  elif args[0] == 'national':
    national.main(args[1], args[2])
  elif args[0] == 'codelist':
    codelist.main()

if __name__ == '__main__':
  args = sys.argv[1:]
  if len(args) > 0:
    main(*args)
