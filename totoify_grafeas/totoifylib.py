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

    for item in link_materials:
      self.materials.append(item)

    for item in link_products:
      self.products.append(item)
    self.command = link_command
    
    for key, value in link_byproducts.items():
      self.byproducts['custom_values'][key] = value

    for key, value in link_environment.items():
      self.environment['custom_values'][key] = value



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

  def __init__(self, in_toto_link, note_name, resource_uri):
    self.intoto["signed"] = GrafeasLink(in_toto_link.signed["materials"],
                                        in_toto_link.signed["products"],
                                        in_toto_link.signed["command"],
                                        in_toto_link.signed["byproducts"],
                                        in_toto_link.signed["environment"])

    self.intoto["signatures"] = in_toto_link.signatures

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

  def load(path):
    """ Given a path, load the occurrence.json into GrafeasIntotoOccurrence class """
    with open(path, "r") as occ_f:
      occ_json = json.load(occ_f)
    
    intoto_block = Metablock(signed=occ_json["intoto"]["signed"],
        signatures=occ_json["intoto"]["signatures"])
    
    return GrafeasInTotoOccurrence(intoto_block, "test-link", "test-resource-uri")
    

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

  #import pdb; pdb.set_trace()
  
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

  return Metablock(signed=in_toto_link, signatures=grafeas_occurrence.intoto["signatures"])


class GrafeasInTotoTransport:
  server_url = None

  def __init__(self, server_url):
    self.server_url = server_url

  def dispatch(self, in_toto_link, note_name, resource_uri):
    grafeas_occurrence = GrafeasInTotoOccurrence(
        in_toto_link, note_name, resource_uri)

    response = requests.post(self.server_url, data=grafeas_occurrence.to_json())
