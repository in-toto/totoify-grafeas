"""
<Program Name>
  totoifylib.py
<Author>
  Aditya Sirish <aditya@saky.in>
  Kristel Fung <kristelfung@berkeley.edu>

<Started>
  Sep 5, 2020

<Copyright>
  See LICENSE for licensing information.

<Purpose>
  Conversion library for Grafeas occurrences and and in-toto link metadata.
"""

import json

from in_toto.models.link import Link
from in_toto.models.metadata import Metablock


class InvalidInput(Exception):
  pass


class GrafeasInTotoOccurrence:
  """Wrapper to hold a Grafeas occurrence complete with in-toto metadata.

  Provides methods to dump occurrence fields into a json string, and to load
  the occurrence file into the class.

  Attributes:
    note_name: A string of the name of the note.
    kind: Set to the string "INTOTO" to indicate the type of occurrence.
    resource: A dict of resource uri.
    intoto: A dictionary corresponding to an in-toto link.
  """

  def __init__(self, intoto, note_name, resource_uri):
    """Initalizes a Grafeas in-toto occurrence."""
    self.intoto = intoto
    self.note_name = note_name
    self.resource = {
        "uri": resource_uri
    }
    self.kind = "INTOTO"  # this can be hard-coded as it's fixed in Grafeas

  def to_dict(self):
    """Returns a dictionary representation of GrafeasInTotoOccurrence."""
    return {
      "resource": self.resource,
      "noteName": self.note_name,
      "kind": self.kind,
      "intoto": {
        "signatures": self.intoto["signatures"],
        "signed": self.intoto["signed"]
      }
    }

  def to_json(self, file_path=None):
    """Returns the JSON string representation. If file_path is provided,
    a .json file is ALSO created at that location.
    """
    dict_repr = self.to_dict()
    if file_path:
      with open(file_path, "w") as fp:
        json.dump(dict_repr, fp, indent=4)

    return json.dumps(dict_repr)

  @classmethod
  def load(cls, path):
    """Given a path, loads the occurrence.json into GrafeasInTotoOccurrence
    class.
    """
    with open(path, "r") as occ_f:
      occ_json = json.load(occ_f)

    return cls(intoto=occ_json["intoto"],
               resource_uri=occ_json["resource"]["uri"],
               note_name=occ_json["noteName"])

  @classmethod
  def from_link(cls, in_toto_link, step_name, resource_uri):
    """Returns a GrafeasInTotoOccurrence class from an in-toto Metablock,
    stepname, and resource uri."""
    # TODO: set step_name from link if None

    if not isinstance(in_toto_link, Metablock):
      raise InvalidInput(
          "in_toto_link is not of type in_toto.models.metadata.Metablock")

    in_toto_link.validate()

    intoto = {}
    intoto["signatures"] = in_toto_link.signatures

    grafeas_link = {
        "materials": [],
        "products": [],
        "command": [],
        "byproducts": {"custom_values": {}},
        "environment": {"custom_values": {}}
    }

    for item in in_toto_link.signed.materials:
      grafeas_link["materials"].append({
        "resource_uri": item,
        "hashes": in_toto_link.signed.materials[item]
      })

    for item in in_toto_link.signed.products:
      grafeas_link["products"].append({
        "resource_uri": item,
        "hashes": in_toto_link.signed.products[item]
      })

    grafeas_link["command"] = in_toto_link.signed.command

    for key, value in in_toto_link.signed.byproducts.items():
      if key == "return-value":
        # This highlights a special case - in-toto's reference implementations
        # store return value as an integer while Grafeas allows only strings.
        # As noted above, Grafeas stores in-toto's byproducts and environment
        # in a "custom_values" subfield.
        grafeas_link["byproducts"]["custom_values"][key] = str(value)
      else:
        grafeas_link["byproducts"]["custom_values"][key] = value

    for key, value in in_toto_link.signed.environment.items():
      grafeas_link["environment"]["custom_values"][key] = value

    intoto["signed"] = grafeas_link

    return cls(intoto=intoto, resource_uri=resource_uri, note_name=step_name)

  def to_link(self, step_name):
    """Returns an in-toto link Metablock class from a GrafeasInTotoOccurrence
    class.
    """
    materials = {}
    products = {}
    command = []
    byproducts = {}
    environment = {}

    for item in self.intoto["signed"]["materials"]:
      materials[item["resource_uri"]] = item["hashes"]

    for item in self.intoto["signed"]["products"]:
      products[item["resource_uri"]] = item["hashes"]

    command = self.intoto["signed"]["command"]

    for key, value in self.intoto["signed"]["byproducts"].items():
      if key != "custom_values":
        byproducts[key] = value
    if "custom_values" in self.intoto["signed"]["byproducts"]:
      for key, value in \
          self.intoto["signed"]["byproducts"]["custom_values"].items():
        if key == "return-value":
          # This highlights a special case - in-toto's reference implementations
          # store return value as an integer while Grafeas allows only strings
          byproducts[key] = int(value)
        else:
          byproducts[key] = value

    for key, value in self.intoto["signed"]["environment"].items():
      if key != "custom_values":
        environment[key] = value
    if "custom_values" in self.intoto["signed"]["environment"]:
      for key, value in \
          self.intoto["signed"]["environment"]["custom_values"].items():
        environment[key] = value

    return Metablock(
        signed=Link(
            name=step_name,
            materials=materials,
            products=products,
            command=command,
            byproducts=byproducts,
            environment=environment
        ),
        signatures=self.intoto["signatures"])
