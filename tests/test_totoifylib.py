"""
<Program Name>
  test_totoifylib.py

<Author>
  Kristel Fung <kristelfung@berkeley.edu>
  Aditya Sirish <aditya@saky.in>

<Started>
  Sep 23, 2020

<Copyright>
  See LICENSE for licensing information.

<Purpose>
  Test totoify-grafeas library.
"""

import unittest
import os
import json
from totoify_grafeas.totoifylib import (
    create_grafeas_occurrence_from_in_toto_link,
    create_in_toto_link_from_grafeas_occurrence,
    GrafeasInTotoTransport,
    GrafeasInTotoOccurrence,
    GrafeasLink)
from in_toto.models.metadata import Metablock
from in_toto.verifylib import in_toto_verify
from in_toto.models.layout import Layout
from securesystemslib import interface


class TestCreateInTotoLinkFromOccurrence(unittest.TestCase):
  """Tests conversion of a Grafeas occurrence to an in-toto link."""
  def test_create_in_toto_link_from_grafeas_occurrence(self):
    grafeas_occurrence = GrafeasInTotoOccurrence.load("clone_occurrence.json")
    in_toto_link = create_in_toto_link_from_grafeas_occurrence(grafeas_occurrence, "clone-step-name")
    assert isinstance(in_toto_link, Metablock)

class TestCreateOccurranceFromInTotoLink(unittest.TestCase):
  """Tests conversion of a in-toto link to a Grafeas occurrence."""
  def test_create_grafeas_occurrence_from_in_toto_link(self):
    in_toto_link = Metablock.load("clone_link.json")
    grafeas_occurrence = create_grafeas_occurrence_from_in_toto_link(in_toto_link, "clone-step-name", "clone-resource-uri")
    assert isinstance(grafeas_occurrence, GrafeasInTotoOccurrence)

class TestInTotoVerify(unittest.TestCase):
  """Runs in-toto verify on generated in-toto links."""
  def setUp(self):
    """Imports keys, generates layout and layout_key_dict for the clone,
    update-version, and package step."""
    self.key_alice = interface.import_rsa_privatekey_from_file("keys/alice")
    # Fetch and load Bob's and Carl's public keys
    # to specify that they are authorized to perform certain step in the layout
    self.key_bob = interface.import_rsa_publickey_from_file("keys/bob.pub")
    self.key_carl = interface.import_rsa_publickey_from_file("keys/carl.pub")
    
    # Create the clone step layout
    self.layout_clone = Layout.read({
        "_type": "layout",
        "keys": {
            self.key_bob["keyid"]: self.key_bob,
            self.key_carl["keyid"]: self.key_carl,
        },
        "steps": [{
            "name": "clone",
            "expected_materials": [],
            "expected_products": [["CREATE", "demo-project/foo.py"], ["DISALLOW", "*"]],
            "pubkeys": [self.key_bob["keyid"]],
            "expected_command": [
                "git",
                "clone",
                "https://github.com/in-toto/demo-project.git"
            ],
            "threshold": 1,
        }],
        "inspect": [],
    })
    
    self.layout_clone_metablock = Metablock(signed=self.layout_clone)
    self.layout_clone_metablock.sign(self.key_alice)
    
    # TODO: Create update step layout
    
    # TODO: Create the package step layout
    
    # Create the public key dict
    self.layout_key_dict = {}
    self.layout_key_dict.update(interface.import_publickeys_from_file(["keys/alice.pub"]))

  def tearDown(self):
    try:
      os.remove("in-toto-verify-links/clone.776a00e2.link")
    except OSError:
      pass

  def test_grafeas_occurrence_to_in_toto_link_verify(self):
    """Test in-toto-verify on in-toto link generated from Grafeas occurrence."""
    # Clone Step
    grafeas_occurrence = GrafeasInTotoOccurrence.load("clone_occurrence.json")
    in_toto_link = create_in_toto_link_from_grafeas_occurrence(grafeas_occurrence, "clone")
    in_toto_link.dump("in-toto-verify-links/clone.776a00e2.link")
    in_toto_verify(self.layout_clone_metablock, self.layout_key_dict, link_dir_path="in-toto-verify-links")
    
    #in_toto_verify(self.layout_update_metablock, self.layout_key_dict,
      #link_dir_path="in-toto-verify-links")
    
  def test_link_occurrence_link_verify(self):
    """Test in-toto-verify on in-toto link converted to Grafeas occurrence
    and back to an in-toto link."""
    in_toto_link = Metablock.load("clone_link.json")
    grafeas_occurrence = create_grafeas_occurrence_from_in_toto_link(in_toto_link, "clone", "demo-project/foo.py")
    new_in_toto_link = create_in_toto_link_from_grafeas_occurrence(grafeas_occurrence, "clone")
    new_in_toto_link.dump("in-toto-verify-links/clone.776a00e2.link")

    in_toto_verify(self.layout_clone_metablock, self.layout_key_dict,
      link_dir_path="in-toto-verify-links")

if __name__ == "__main__":
  unittest.main()
