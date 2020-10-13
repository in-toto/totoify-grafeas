from in_toto.models.link import Link
from in_toto.models.metadata import Metablock
import requests
import json


class GrafeasLink:
  command = []
  environment = {"custom_values": {}}
  byproducts = {"custom_values": {}}
  materials = []
  products = []

  def __init__(self, link_materials, link_products, link_command,
      link_byproducts, link_environment):

    if isinstance(link_materials, dict):
      for item in link_materials:
        self.materials.append(item)
    elif isinstance(link_materials, list):
      self.materials = link_materials
    # else raise exception

    if isinstance(link_products, dict):
      for item in link_products:
        self.products.append(item)
    elif isinstance(link_products, list):
      self.products = link_products
    # else raise exception

    self.command = link_command
    
    if "custom_values" in link_byproducts:
      # this could cause problems when "custom_values" is an actual field
      self.byproducts = link_byproducts
    else:
      for key, value in link_byproducts.items():
        self.byproducts["custom_values"][key] = value

    if "custom_values" in link_environment:
      # this could cause problems when "custom_values" is an actual field
      self.environment = link_environment
    else:
      for key, value in link_environment.items():
        self.environment["custom_values"][key] = value



class GrafeasInTotoOccurrence:
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
    if in_toto_link:
      self.intoto["signed"] = GrafeasLink(in_toto_link.signed["materials"],
                                          in_toto_link.signed["products"],
                                          in_toto_link.signed["command"],
                                          in_toto_link.signed["byproducts"],
                                          in_toto_link.signed["environment"])
      for signature in in_toto_link.signatures:
        self.intoto["signatures"].append({"keyid": signature["keyid"], "signature": signature["sig"]})

    self.note_name = note_name

    self.resource["uri"] = resource_uri

  def to_json(self):
    return json.dumps({
        "resource": self.resource,
        "noteName": self.note_name,
        "kind": self.kind,
        "intoto": self.intoto
      }
    )

  @staticmethod
  def load(path):
    """ Given a path, load the occurrence.json into GrafeasIntotoOccurrence class """
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
    

'''
accepts a link of type in_toto.models.metadata.Metablock (and we know that "signed" corresponds to an object of type in_toto.models.link.Link)
returns an object of GrafeasInTotoOccurrence
'''
def create_grafeas_occurrence_from_in_toto_link(in_toto_link, step_name, resource_uri):
  # TODO: set step_name from link if None
  return GrafeasInTotoOccurrence(in_toto_link, step_name, resource_uri)

'''
accepts a grafeas occurrence of type totoify_grafeas.GrafeasInTotoOccurrence
returns an object of type in_toto.models.metadata.Metablock (and again we know that "signed" corresponds to in_toto.models.link.Link)
'''

def create_in_toto_link_from_grafeas_occurrence(grafeas_occurrence, step_name):
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
