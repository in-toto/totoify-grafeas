#!/usr/bin/env python
"""
  <Name>
    grafeas-verify

  <Description>
    Fetches a named supply chain, as well as it's ocurrences for verification

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
import in_toto.verifylib as verifylib
import in_toto.util as util
import in_toto.models.layout as layout
import in_toto.models.metadata as metadata

from pprint import pprint
THIS_OPERATION='a40f2623-986b-4ed8-9022-a3f78a57b8c6'

def parse_arguments():
  parser = argparse.ArgumentParser()
  grafeas_run_args = parser.add_argument_group("grafeas-run options")
  grafeas_run_args.add_argument("-t", "--target", help="the grafeas server url",
      dest="host", default="http://localhost:8080")
  grafeas_run_args.add_argument("-k", "--key", help="key used for verification")
  grafeas_run_args.add_argument("-n", "--name", help="the named operation")

  return parser.parse_args()


def fetch_layout(name, project_id, api_instance):
  """
    <Description>
      Auxiliary method to obtain a layout from a target server
  """
  grafeas_operation = api_instance.get_operation(project_id, name)
  with open('root.layout', 'wt') as fp:
    layout_json = fp.write(grafeas_operation.metadata['in-toto'])
  layout = metadata.Metablock.load('root.layout')
  return layout

def fetch_ocurrence(project_id, name, key_prefix, api_instance):
  """
    <Description>
      Auxiliary method to fetch an ocurrence for a specific in-toto step
  """
  link_name = "{}-{}".format(name, key_prefix)
  occurrence = api_instance.get_occurrence(projects_id, link_name)
  return occurrence.link_metadata

def serialize_occurrence(link_metadata, name, key_prefix):
  link_name = "{}-{}".format(name, key_prefix)
  with open("{}.link".format(link_name), "wt"):
    json.dumps(link, fp)


args = parse_arguments()
args.name = THIS_OPERATION

# configure our instance of the grafeas api
swagger_client.configuration.host = args.host
api_instance = swagger_client.GrafeasApi()

# let's create an note on a test proejct here
projects_id = 'projects_id_example' # str | Part of `parent`. This field contains the projectId for example: \"project/{project_id}

try:
  key = {}
  if 'key' in args:
    this_key = util.import_rsa_key_from_file(args.key)
    
  key[this_key['keyid']] = this_key
  layout = fetch_layout(args.name, projects_id, api_instance)  

except Exception as e:
  print("Exception when fetching the in-toto layout".format(e))
  raise

# fetch the link metadata for every step
for step in layout.signed.steps:
  for keyid in step.pubkeys:
    import pdb; pdb.set_trace()
    try:
      occurrence = fetch_ocurrence(projects_id, step.name, keyid[:], api_instance)
      serialize_occurrence(occurrence, step.name, keyid[:])
    except ApiException as e:
      pass

verifylib.in_toto(layout, key)
