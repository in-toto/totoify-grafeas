#!/usr/bin/env python
"""
  <Name>
    grafeas-run

  <Description>

    performs a supply chain step, gathers link metadata and submits it to the
    server in the form of an occurrence.

"""
import time
import sys
import json
import attr
import argparse
import shlex

# grafeas-specific client imports
import swagger_client
from swagger_client.rest import ApiException

# in-toto specific imports
import in_toto.runlib as runlib
import in_toto.util as util

from pprint import pprint


def parse_arguments():
  parser = argparse.ArgumentParser()
  grafeas_run_args = parser.add_argument_group("grafeas-run options")
  grafeas_run_args.add_argument("-t", "--target", help="the grafeas server url",
      dest="host", default="http://localhost:8080")
  grafeas_run_args.add_argument("-k", "--key", help="increase output verbosity")
  grafeas_run_args.add_argument("-n", "--name", help="the name for this step")
  grafeas_run_args.add_argument("link_cmd", nargs="*", 
      help="command to be executed with options and arguments")

  return parser.parse_args()


def link_to_ocurrence(name, link, project_id):
  """
    <Description>
      Auxiliary method to create an occurrence out of in-toto link metadata
  """
  if "-" in name:
    notename, _ = name.split("-", 1)
  else:
    notename = name

  in_toto_link = attr.asdict(link)
  in_toto_link['signed']['byproducts']['return-value'] = "ayylmao"
  signable = swagger_client.LinkSignable(**(in_toto_link['signed']))
  grafeas_link = swagger_client.LinkMetadata(signable, link.signatures)
  this_ocurrence = swagger_client.Occurrence()
  this_ocurrence.link_metadata = grafeas_link.to_dict()
  this_ocurrence.name = "projects/{}/ocurrences/{}".format(project_id, name)
  this_ocurrence.note_name = "projects/{}/notes/{}".format(project_id, notename)

  return this_ocurrence 


def main():
  args = parse_arguments()

  # configure our instance of the grafeas api
  swagger_client.configuration.host = args.host
  api_instance = swagger_client.GrafeasApi()

  # let's create an note on a test proejct here
  projects_id = 'projects_id_example' # str | Part of `parent`. This field contains the projectId for example: \"project/{project_id}

  try:
    key = False
    if 'key' in args:
      key = util.import_rsa_key_from_file(args.key)
    link = runlib.in_toto_run(args.name, ['.'], ['.'], args.link_cmd, key=key)
  except Exception as e:
    print("Exception when calling in-toto runlib: {}".format(e))
    sys.exit(1)

  # Submit the link metadata now
  occurrence_name = "{}-{}".format(args.name, link.signatures[0]['keyid'][:8])
  import pdb; pdb.set_trace()
  occurrence = link_to_ocurrence(occurrence_name, link, projects_id)
  try:
    api_response = api_instance.create_occurrence(projects_id, occurrence=occurrence)
    pprint(api_response)
    pass
  except ApiException as e:
    print("Exception when calling GrafeasApi->create_ocurrence: {}".format(e))
    sys.exit(1)

if __name__ == "__main__":
  main()
