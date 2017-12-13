#!/usr/bin/env python
"""
<Name>
  grafeas_load.py

<Description>
  Loads an in-toto layout and posts it to grafeas server as an
  *operation*, additionally creates a *note* for each step listed in the
  layout. The *notes* reference the *operation*.

<Usage>

  grafeas-load --id <project-id> --layout <path/to/root.layout> \
      [--target <grafeas server url>]

"""
import time
import sys
import json
import attr
import argparse

from constants import SERVER_URL, LAYOUT_OPERATION_ID

# grafeas-specific client imports
import swagger_client
from swagger_client.rest import ApiException

# in-toto models and classes
import in_toto.models.metadata
from pprint import pprint

def parse_arguments():
  parser = argparse.ArgumentParser()
  parser.add_argument("-t", "--target", help="grafeas server url",
      dest="target", default=SERVER_URL)
  parser.add_argument("-i", "--id", help="project id", required=True,
      dest="project_id")
  parser.add_argument("-l", "--layout", help="path to layout", required=True)

  return parser.parse_args()


def main():
  args = parse_arguments()

  # Load passed in-toto layout
  layout = in_toto.models.metadata.Metablock.load(args.layout)
  layout_json_string = json.dumps(attr.asdict(layout))

  # Configure our instance of the grafeas api
  swagger_client.configuration.host = args.target
  api_instance = swagger_client.GrafeasApi()

  # Pass these as args? Make constants?
  project_id = args.project_id
  operation_id = LAYOUT_OPERATION_ID
  operation_name = "projects/{}/operations/{}".format(project_id, operation_id)

  # Let's create an operation and post it to the server
  operation = swagger_client.Operation(name=operation_name,
      metadata={"in-toto": layout_json_string}, done=False)
  try:
    api_response = api_instance.create_operation(project_id,
        operation_id, operation=operation)
    pprint(api_response)

  except ApiException as e:
    print("Exception when calling GrafeasApi->create_operation: {}".format(e))
    sys.exit(1)


  # Create notes for every step in the loaded layout and post them to the
  # server
  for step in layout.signed.steps:
    note = swagger_client.Note()
    note.step = json.dumps(attr.asdict(step))
    note.name = "projects/{}/notes/{}".format(project_id, step.name)

    try:
      api_response = api_instance.create_note(project_id,
          note_id=step.name, note=note)
      pprint(api_response)

    except ApiException as e:
      print("Exception when calling GrafeasApi->create_note: {}".format(e))
      sys.exit(1)


if __name__ == "__main__":
  main()
