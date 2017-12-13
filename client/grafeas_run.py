#!/usr/bin/env python
"""
<Name>
  grafeas_run.py

<Description>
  Performs a supply chain step, gathers link metadata and submits it to the
  server in the form of an occurrence.

<Usage>
  Run git tag, generate in-toto metadata and send it to a server:

  grafeas-run --id test-project --key path/to/singing/key --name tag \
     --products . -- git tag v1.0



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

from constants import SERVER_URL

# in-toto specific imports
import in_toto.runlib as runlib
import in_toto.util as util

from pprint import pprint


def parse_arguments():
  parser = argparse.ArgumentParser()
  parser.add_argument("-t", "--target", help="grafeas server url",
      dest="target", default=SERVER_URL, metavar="<server url>")
  parser.add_argument("-i", "--id", help="project id", required=True,
      dest="project_id", metavar="<project id>")
  parser.add_argument("-k", "--key", help="link signing key", required=True,
      metavar="<path/to/signing/key>")
  parser.add_argument("-n", "--name", help="step name", required=True,
      metavar="<step name>")

  # Record nor materials/products per default
  parser.add_argument("-m", "--materials", help="materials to record",
      default=[], nargs="+", metavar="<material/path>")
  parser.add_argument("-p", "--products", help="products to record",
      default=[], nargs="+", metavar="<product/path>")

  parser.add_argument("link_cmd", nargs="*", metavar="<command to run>",
      help="command to be executed with options and arguments")

  return parser.parse_args()


def main():
  args = parse_arguments()

  # configure our instance of the grafeas api
  swagger_client.configuration.host = args.target
  api_instance = swagger_client.GrafeasApi()

  project_id = args.project_id

  try:
    # Create and return an unsigned link (not dumping to disk)
    link = runlib.in_toto_run(args.name, args.materials, args.products,
        args.link_cmd, key=None)

    # Now sign the link with the passed key
    key = util.import_rsa_key_from_file(args.key)
    link.sign(key)

  except Exception as e:
    print("Exception when calling in-toto runlib: {}".format(e))
    sys.exit(1)


  # Create an occurrence from the link
  link_dict = attr.asdict(link)

  # We need to cast return-value to string or else parsing breaks mysteriously
  link_dict["signed"]["byproducts"]["return-value"] = \
    str(link_dict["signed"]["byproducts"]["return-value"])

  # Create the in-toto link extended occurrence metadata
  signable = swagger_client.LinkSignable(**(link_dict["signed"]))
  grafeas_link = swagger_client.LinkMetadata(signable, link.signatures)

  # Create the occurrence object that is posted to the server
  occurrence = swagger_client.Occurrence()

  # Occurrences/links use the step name + signing keyid as id
  # There can be multiple occurrences per note (links per step)
  occurrence_id = "{}-{}".format(args.name, link.signatures[0]["keyid"][:8])
  occurrence_name = "projects/{}/occurrences/{}".format(project_id,
      occurrence_id)

  # Notes/steps only use the step name as id
  note_name = "projects/{}/notes/{}".format(project_id, args.name)

  occurrence.name = occurrence_name
  occurrence.note_name = note_name
  occurrence.link_metadata = grafeas_link


  try:
    api_response = api_instance.create_occurrence(project_id,
        occurrence=occurrence)
    pprint(api_response)

  except ApiException as e:
    print("Exception when calling GrafeasApi->create_occurrence: {}".format(e))
    sys.exit(1)

if __name__ == "__main__":
  main()
