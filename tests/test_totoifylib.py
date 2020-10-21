import unittest
import json
from totoify_grafeas.totoifylib import (
    create_grafeas_occurrence_from_in_toto_link,
    create_in_toto_link_from_grafeas_occurrence,
    GrafeasInTotoTransport,
    GrafeasInTotoOccurrence,
    GrafeasLink)
from in_toto.models.metadata import Metablock


#class TestCreateGrafeasOccurrenceFromInTotoLink(unittest.TestCase):
#  def test_create_grafeas_occurrence_from_in_toto_link(self):
#    in_toto_link = Metablock.load("tests/test-link.e3294129.link")
#    grafeas_occurrence = create_grafeas_occurrence_from_in_toto_link(in_toto_link, "test-link", "test-resource-uri")
#    assert isinstance(grafeas_occurrence, GrafeasInTotoOccurrence)

class TestCreateInTotoLinkFromOccurrence(unittest.TestCase):
  def test_create_in_toto_link_from_grafeas_occurrence(self):
    grafeas_occurrence = GrafeasInTotoOccurrence.load("occurrence_link.json")
    in_toto_link = create_in_toto_link_from_grafeas_occurrence(grafeas_occurrence, "test-step")
    assert isinstance(in_toto_link, Metablock)
    
class TestCreateOccurranceFromInTotoLink(unittest.TestCase):
  def test_create_grafeas_occurrence_from_in_toto_link(self):
    in_toto_link = Metablock.load("clone.776a00e2.link.backup")
    grafeas_occurrence = create_grafeas_occurrence_from_in_toto_link(in_toto_link, "test-step-name", "test-resource-uri")
    assert isinstance(grafeas_occurrence, GrafeasInTotoOccurrence)
    
class Hello(unittest.TestCase):
  def test_func(self):
    in_toto_link = Metablock.load("clone.776a00e2.link.backup")
    grafeas_occurrence = create_grafeas_occurrence_from_in_toto_link(in_toto_link, "test-step-name", "test-resource-uri")
    #import pdb; pdb.set_trace()
    in_toto_back_to_link = create_in_toto_link_from_grafeas_occurrence(grafeas_occurrence, "test-step")
    assert isinstance(in_toto_back_to_link, Metablock)
    
#class TestCreateInTotoLinkFromOccurrence(unittest.TestCase):
#  def test_intoto_verify_link_from_occurence(self):
#    """ Create link from occurrence and run in-toto verify """
#    with open("occurrence_link.json", "r") as occ_f:
#      occurrence_json = json.load(occ_f)
#    with open("note_reduced.json", "r") as note_f:
#      note_json = json.load(note_f)
#
#    occurrence = load(occurrence_json)
    # occ = create_in_toto_link_from_grafeas_occurrence(occurrence_json, "clone")
#    occ = GrafeasInTotoOccurrence(occurrence_json["intoto"],
#        note_json["intoto"]["step_name"],
#        occurrence_json["intoto"]["signed"]["products"][0]["resource_uri"])
#
#    link = create_in_toto_link_from_grafeas_occurrence(occ, note_json["intoto"]["step_name"])
    # run in-toto verify on this link - do I have to import intoto?


if __name__ == "__main__":
  unittest.main()
