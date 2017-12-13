#!/usr/bin/env python
"""
  <Name>
    grafeas-verify

  <Description>
    Fetches a named supply chain, as well as it's occurrences for verification

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

from constants import SERVER_URL, LAYOUT_OPERATION_ID

# in-toto specific imports
import in_toto.verifylib as verifylib
import in_toto.util as util
import in_toto.models.metadata as metadata
import in_toto.models.link

from pprint import pprint


def parse_arguments():
  parser = argparse.ArgumentParser()
  parser.add_argument("-t", "--target", help="grafeas server url",
      dest="target", default=SERVER_URL, metavar="<server url>")
  parser.add_argument("-i", "--id", help="project id used to load the layout",
      required=True, dest="project_id", metavar="<project id>")
  parser.add_argument("-k", "--key", help="pubkey used for verification",
      required=True, metavar="<public key>")

  return parser.parse_args()


def fetch_layout(project_id, api_instance):
  """
    <Description>
      Auxiliary method to obtain a layout from a target server
  """
  grafeas_operation = api_instance.get_operation(project_id,
      LAYOUT_OPERATION_ID)

  with open('root.layout', 'wt') as fp:
    layout_json = fp.write(grafeas_operation.metadata['in-toto'])
  layout = metadata.Metablock.load('root.layout')
  return layout


def fetch_occurrence(project_id, name, keyid, api_instance):
  """
    <Description>
      Auxiliary method to fetch an occurrence for a specific in-toto step
  """
  occurrence_id = "{}-{}".format(name, keyid[:8])
  occurrence = api_instance.get_occurrence(project_id, occurrence_id)

  link_file_name = in_toto.models.link.FILENAME_FORMAT.format(
      step_name=name, keyid=keyid)

  ##########################################
  # BEGIN FIXME: Fix deserialization
  # Some fields don't get deserialized properly.
  # Below code is really really hackyish.
  # Santiago, please fix, Santiago! :P
  import ast
  cmd = occurrence.link_metadata.signed.command
  cmd_list = ast.literal_eval(cmd)
  occurrence.link_metadata.signed.command = cmd_list

  occurrence.link_metadata.signed.byproducts["return-value"] = \
    int(occurrence.link_metadata.signed.byproducts["return-value"])

  if not occurrence.link_metadata.signed.materials:
    occurrence.link_metadata.signed.materials = {}

  if not occurrence.link_metadata.signed.products:
    occurrence.link_metadata.signed.products = {}

  ########### END FIXME: Fix deserialization
  ##########################################

  with open(link_file_name, "wt") as fp:
    json.dump(occurrence.link_metadata.to_dict(), fp)

def main():
  args = parse_arguments()

  # configure our instance of the grafeas api
  swagger_client.configuration.host = args.target
  api_instance = swagger_client.GrafeasApi()

  try:
    pubkey = util.import_rsa_public_keys_from_files_as_dict([args.key])
    layout = fetch_layout(args.project_id, api_instance)

  except Exception as e:
    print("Exception when fetching the in-toto layout\n{}: {}"
        .format(type(e).__name__, e))
    sys.exit(1)


  # fetch the link metadata for every step
  for step in layout.signed.steps:
    for keyid in step.pubkeys:
      try:
        fetch_occurrence(args.project_id, step.name, keyid, api_instance)
      except ApiException as e:
        raise e
        pass

  try:
    verifylib.in_toto_verify(layout, pubkey)
  except Exception as e:
    print("Exception when verifying the supply chain\n{}: {}"
        .format(type(e).__name__, e))
    sys.exit(1)

if __name__ == "__main__":
  main()
