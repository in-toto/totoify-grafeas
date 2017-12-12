#!/usr/bin/env python
"""
  <Name>
    grafeas-load 

  <Description>

    Loads an in-toto layout and submits it into the grafeas server as an
    operation.


"""
import time
import sys
import json
import attr

# grafeas-specific client imports
import swagger_client
from swagger_client.rest import ApiException

# in-toto models and classes
from create_layout import create_layout

from pprint import pprint

# configure our instance of the grafeas api
swagger_client.configuration.host='http://localhost:8080'

def step_to_note(step, project_id):
  """
    <Description>
      Auxiliary method to create a note out of in-toto step metadata
  """

  this_note = swagger_client.Note()
  this_note.step = json.dumps(attr.asdict(step))
  this_note.name = "projects/{}/notes/{}".format(project_id, step.name)

  return this_note

api_instance = swagger_client.GrafeasApi()

# let's create an note on a test proejct here
projects_id = 'projects_id_example' # str | Part of `parent`. This field contains the projectId for example: \"project/{project_id}
note_id = 'note_id_example' # str | The ID to use for this note. (optional)
note = swagger_client.Note() # Note | The Note to be inserted (optional)
note.name = 'projects/{}/notes/{}'.format(projects_id, note_id)

# let's load our in-toto layout now
layout = create_layout()
layout_payload = json.dumps(attr.asdict(layout))


# if we succeeded (this means their api is still wroking :) ), let's create an operation
operation = swagger_client.Operation(name='kek', 
    metadata={"in-toto": layout_payload}, done=False)


try:
  # fixme, check how the create operation is done in the server side.
  api_response = api_instance.create_operation(projects_id, "toto_grafeas_1.0", 
      operation=operation)
  pprint(api_response)
  pass
except ApiException as e:
  print("Exception when calling GrafeasApi->create_note: {}".format(e))
  sys.exit(1)

# try to serialize all of the steps as notes
for step in layout.signed.steps:
  note = step_to_note(step, projects_id)
  try:
    api_response = api_instance.create_note(projects_id, note_id=step.name, note=note)
    pprint(api_response)
  except ApiException as e:
    pass
    print("Exception when calling GrafeasApi->create_note: {}".format(e))
    sys.exit(1)


