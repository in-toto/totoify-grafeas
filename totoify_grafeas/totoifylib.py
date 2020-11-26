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
  command = []
  environment = {"custom_values": {}}
  byproducts = {"custom_values": {}}
  materials = []
  products = []

  def __init__(self, link_materials, link_products, link_command,
      link_byproducts, link_environment):
    """Takes in materials, products, command, byproducts and initalizes
    to the GrafeasLink fields."""

    if isinstance(link_materials, dict):
      for item in link_materials:
        self.materials.append({"resource_uri": item, "hashes": link_materials[item]})
    elif isinstance(link_materials, list):
      self.materials = link_materials
    # else raise exception

    if isinstance(link_products, dict):
      for item in link_products:
        self.products.append({"resource_uri": item, "hashes": link_products[item]})
    elif isinstance(link_products, list):
      self.products = link_products
    # else TODO: raise exception

    self.command = link_command

    if "custom_values" in link_byproducts:
      # this could cause problems when "custom_values" is an actual field
      self.byproducts = link_byproducts
    else:
      for key, value in link_byproducts.items():
        if key == "return-value":
          self.byproducts["custom_values"][key] = str(value)
        else:
          self.byproducts["custom_values"][key] = value

    if "custom_values" in link_environment:
      # this could cause problems when "custom_values" is an actual field
      self.environment = link_environment
    else:
      for key, value in link_environment.items():
        self.environment["custom_values"][key] = value

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
      self.intoto["signed"] = GrafeasLink(in_toto_link.signed.materials,
                                          in_toto_link.signed.products,
                                          in_toto_link.signed.command,
                                          in_toto_link.signed.byproducts,
                                          in_toto_link.signed.environment)
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



def create_grafeas_occurrence_from_in_toto_link(in_toto_link, step_name, resource_uri):
  """Creates a GrafeasInTotoOccurrence class from an in-toto link Metablock class.

  Arguments:
    in_toto_link: A link of type Metablock (and we know that "signed" corresponds
        to an object of type in_toto.models.link.Link)
    step_name: A string of the step name
    resource_uri: A string of the resource URI

  Raises:
    N/A

  Side Effects:
    N/A

  Returns:
    A GrafeasInTotoOccurrence object.
  """
  # TODO: set step_name from link if None
  return GrafeasInTotoOccurrence(in_toto_link, step_name, resource_uri)



def create_in_toto_link_from_grafeas_occurrence(grafeas_occurrence, step_name):
  """Creates an in-toto link Metablock class from a GrafeasInTotoOccurrence class.

  Arguments:
    grafeas_occurrence: An occurrence of type GrafeasInTotoOccurrence.
    step_name: A string of the step name.

  Raises:
    N/A

  Side Effects:
    N/A

  Returns:
    A Metablock object.
  """
  materials = {}
  products = {}
  command = []
  byproducts = {}
  environment = {}

  for item in grafeas_occurrence.intoto["signed"].materials:
    materials[item["resource_uri"]] = item["hashes"]

  for item in grafeas_occurrence.intoto["signed"].products:
    products[item["resource_uri"]] = item["hashes"]

  command = grafeas_occurrence.intoto["signed"].command

  for key, value in grafeas_occurrence.intoto["signed"].byproducts.items():
    if key == "custom_values":
      continue
    byproducts[key] = value

  for key, value in grafeas_occurrence.intoto["signed"].byproducts["custom_values"].items():
    if key == "return-value":
      byproducts[key] = int(value)  # cast return-value back to int
    else:
      byproducts[key] = value

  for key, value in grafeas_occurrence.intoto["signed"].environment.items():
    if key == "custom_values":
      continue
    environment[key] = value

  for key, value in grafeas_occurrence.intoto["signed"].environment["custom_values"].items():
    environment[key] = value

  in_toto_link = Link(name=step_name, materials=materials, products=products, byproducts=byproducts, command=command, environment=environment)

  signatures = []
  for signature in grafeas_occurrence.intoto["signatures"]:
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
