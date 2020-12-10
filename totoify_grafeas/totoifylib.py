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

from in_toto.models.link import Link
from in_toto.models.metadata import Metablock
import requests
import json


class GrafeasLink:
  """Wrapper for in-toto 'signed' fields.

  Used in the GrafeasInTotoOccurrence class to organize in-toto "signed"
  attributes (corresponding to in_toto.models.link.Link).

  Attributes:
    command: A list of arguments used in the link's command.
    environment: A dict of the environment where the command was executed.
    byproducts: A dict containing byproducts of the command.
    materials: A list of materials used in the command.
    products: A list of dicts containing resource URI and hashes.
  """

  materials = None
  products = None
  command = None
  byproducts = None
  environment = None

  def __init__(self, materials=None, products=None, command=None,
      byproducts=None, environment=None):
    """Takes in materials, products, command, byproducts and initalizes
    to the GrafeasLink fields."""

    if materials is None:
      self.materials = []
    elif isinstance(materials, list):
      self.materials = materials

    if products is None:
      self.products = []
    elif isinstance(products, list):
      self.products = products

    if command is None:
      self.command = []
    elif isinstance(command, list):
      self.command = command

    if byproducts is None:
      self.byproducts = {"custom_values": {}}
    elif isinstance(byproducts, dict):
      self.byproducts = byproducts

    if environment is None:
      self.environment = {"custom_values": {}}
    elif isinstance(environment, dict):
      self.environment = environment

  @staticmethod
  def from_link(link):
    link.validate()

    grafeas_link = GrafeasLink()

    # materials and products
    for item in link.materials:
      grafeas_link.materials.append({"resource_uri": item, "hashes": link.materials[item]})

    for item in link.products:
      grafeas_link.products.append({"resource_uri": item, "hashes": link.products[item]})

    grafeas_link.command = link.command

    for key, value in link.byproducts.items():
      if key == "return-value":
        grafeas_link.byproducts["custom_values"][key] = str(value)
      else:
        grafeas_link.byproducts["custom_values"][key] = value

    for key, value in link.environment.items():
      grafeas_link.environment["custom_values"][key] = value

    return grafeas_link

  def __repr__(self):
    return json.dumps({
        "command": self.command,
        "materials": self.materials,
        "products": self.products,
        "environment": self.environment,
        "byproducts": self.byproducts
    })

  def to_dict(self):
    return {
        "command": self.command,
        "materials": self.materials,
        "products": self.products,
        "environment": self.environment,
        "byproducts": self.byproducts
      }


class GrafeasInTotoOccurrence:
  """Wrapper to hold a Grafeas occurrence complete with in-toto metadata.

  Provides methods to dump occurrence fields into a json string, and to load
  the occurrence file into the class.

  Attributes:
    note_name: A string of the name of the note.
    kind: Set to the string "INTOTO" to indicate the type of occurrence.
    resource: A dict of resource uri.
    intoto: A dictionary with key "signatures", a list of signatures consisting
        of key id and signature hash, and key "signed", the GrafeasLink class.
  """
  note_name = None
  kind = "INTOTO"
  resource = {
    "uri": None
  }
  intoto = {
    "signatures":  [],
    "signed": None
  }

  def __init__(self, in_toto_link=None, note_name=None, resource_uri=None):
    """Initalizes intoto "signed" fields with a GrafeasLink."""
    if in_toto_link:
      self.intoto["signed"] = GrafeasLink.from_link(in_toto_link.signed)
      self.intoto["signatures"] = []
      for signature in in_toto_link.signatures:
        self.intoto["signatures"].append({"keyid": signature["keyid"], "signature": signature["sig"]})

    self.note_name = note_name

    self.resource["uri"] = resource_uri

  def to_json(self, file_path=None):
    """Returns the JSON string representation."""
    if file_path:
      with open(file_path, "w") as fp:
        json.dump({
            "resource": self.resource,
            "noteName": self.note_name,
            "kind": self.kind,
            "intoto": {
              "signatures": self.intoto["signatures"],
              "signed": self.intoto["signed"].to_dict()
            }
          }, fp, indent=4)
    else:
      return json.dumps({
          "resource": self.resource,
          "noteName": self.note_name,
          "kind": self.kind,
          "intoto": {
            "signatures": self.intoto["signatures"],
            "signed": self.intoto["signed"].to_dict()
          }
        }
      )

  @staticmethod
  def load(path):
    """Given a path, loads the occurrence.json into GrafeasInTotoOccurrence class."""
    with open(path, "r") as occ_f:
      occ_json = json.load(occ_f)

    grafeas_occurrence = GrafeasInTotoOccurrence()
    grafeas_occurrence.intoto['signed'] = GrafeasLink(occ_json['intoto']['signed']['materials'],
                                                      occ_json['intoto']['signed']['products'],
                                                      occ_json['intoto']['signed']['command'],
                                                      occ_json['intoto']['signed']['byproducts'],
                                                      occ_json['intoto']['signed']['environment'])
    grafeas_occurrence.intoto['signatures'] = occ_json['intoto']['signatures']
    grafeas_occurrence.resource['uri'] = occ_json['resource']['uri']
    grafeas_occurrence.noteName = occ_json['noteName']
    return grafeas_occurrence
  
  @staticmethod
  def from_link(in_toto_link, step_name, resource_uri):
    """Returns a GrafeasInTotoOccurrence class from an In-toto Metablock,
    stepname, and resource uri."""
    # TODO: set step_name from link if None
    return GrafeasInTotoOccurrence(in_toto_link, step_name, resource_uri)
  
  def to_link(self, step_name):
    """Returns an in-toto link Metablock class from a GrafeasInTotoOccurrence class."""
    materials = {}
    products = {}
    command = []
    byproducts = {}
    environment = {}
    
    for item in self.intoto["signed"].materials:
      materials[item["resource_uri"]] = item["hashes"]

    for item in self.intoto["signed"].products:
      products[item["resource_uri"]] = item["hashes"]

    command = self.intoto["signed"].command

    for key, value in self.intoto["signed"].byproducts.items():
      if key == "custom_values":
        continue
      byproducts[key] = value

    if "custom_values" in self.intoto["signed"].byproducts:
      for key, value in self.intoto["signed"].byproducts["custom_values"].items():
        if key == "return-value":
          byproducts[key] = int(value)  # cast return-value back to int
        else:
          byproducts[key] = value

    for key, value in self.intoto["signed"].environment.items():
      if key == "custom_values":
        continue
      environment[key] = value

    if "custom_values" in self.intoto["signed"].environment:
      for key, value in self.intoto["signed"].environment["custom_values"].items():
        environment[key] = value

    in_toto_link = Link(name=step_name, materials=materials, products=products, byproducts=byproducts, command=command, environment=environment)

    signatures = []
    for signature in self.intoto["signatures"]:
      if "sig" not in signature:
        signatures.append({"keyid": signature["keyid"], "sig": signature["signature"]})
      else:
        signatures.append(signature)

    return Metablock(signed=in_toto_link, signatures=signatures)


class GrafeasInTotoTransport:
  server_url = None

  def __init__(self, server_url):
    self.server_url = server_url

  def dispatch(self, in_toto_link, note_name, resource_uri):
    grafeas_occurrence = GrafeasInTotoOccurrence(
        in_toto_link, note_name, resource_uri)

    response = requests.post(self.server_url, data=grafeas_occurrence.to_json())
