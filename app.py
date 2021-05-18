import sys

import mapping.organization as org
import mapping.contact as contact
import mapping.worship as worship
import mapping.central as central
import mapping.national as national
import mapping.codelist as codelist
import mapping.vocabulary as vocab

import dummymapping.organization as dummyorg
import dummymapping.contact as dummycontact
import dummymapping.central as dummycentral

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
    codelist.main(args[1])
  elif args[0] == 'vocab':
    vocab.main(args[1])
  elif args[0] == 'dummyorg':
    dummyorg.main(args[1], args[2])
  elif args[0] == 'dummycontact':
    dummycontact.main(args[1], args[2])
  elif args[0] == 'dummycentral':
    dummycentral.main(args[1], args[2])

if __name__ == '__main__':
  args = sys.argv[1:]
  if len(args) > 0:
    main(*args)
