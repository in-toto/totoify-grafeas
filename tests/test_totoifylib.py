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
    #create_grafeas_occurrence_from_in_toto_link,
    #create_in_toto_link_from_grafeas_occurrence,
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
    grafeas_occurrence = GrafeasInTotoOccurrence.load("occurrences/clone_occurrence.json")
    in_toto_link = grafeas_occurrence.to_link("clone-step-name")
    assert isinstance(in_toto_link, Metablock)

class TestCreateOccurranceFromInTotoLink(unittest.TestCase):
  """Tests conversion of a in-toto link to a Grafeas occurrence."""
  def test_create_grafeas_occurrence_from_in_toto_link(self):
    in_toto_link = Metablock.load("links/clone_link.json")
    grafeas_occurrence = GrafeasInTotoOccurrence.from_link(in_toto_link, "clone-step", "clone-resource-uri")

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

    # Create layout
    self.layout = Layout.read({
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
          },{
            "name": "update-version",
            "expected_materials": [["MATCH", "demo-project/*", "WITH", "PRODUCTS",
                                  "FROM", "clone"], ["DISALLOW", "*"]],
            "expected_products": [["ALLOW", "demo-project/foo.py"], ["DISALLOW", "*"]],
            "pubkeys": [self.key_bob["keyid"]],
            "expected_command": [],
            "threshold": 1,
          },{
            "name": "package",
            "expected_materials": [
              ["MATCH", "demo-project/*", "WITH", "PRODUCTS", "FROM",
               "update-version"], ["DISALLOW", "*"],
            ],
            "expected_products": [
                ["CREATE", "demo-project.tar.gz"], ["DISALLOW", "*"],
            ],
            "pubkeys": [self.key_carl["keyid"]],
            "expected_command": [
                "tar",
                "--exclude",
                ".git",
                "-zcvf",
                "demo-project.tar.gz",
                "demo-project",
            ],
            "threshold": 1,
          }],
        "inspect": [],
    })

    self.metadata = Metablock(signed=self.layout)
    self.metadata.sign(self.key_alice)

    # Create the public key dict
    self.layout_key_dict = {}
    self.layout_key_dict.update(interface.import_publickeys_from_file(["keys/alice.pub"]))

  def tearDown(self):
    try:
      os.remove("in-toto-verify-links/clone.776a00e2.link")
    except OSError:
      pass
    try:
      os.remove("in-toto-verify-links/update-version.776a00e2.link")
    except OSError:
      pass
    try:
      os.remove("in-toto-verify-links/package.2f89b927.link")
    except OSError:
      pass

  def test_grafeas_occurrence_to_in_toto_link_verify(self): # invalidly signed
    """Test in-toto-verify on in-toto link generated from Grafeas occurrence."""
    # Clone Step
    grafeas_occurrence_clone = GrafeasInTotoOccurrence.load("occurrences/clone_occurrence.json")
    in_toto_link_clone = grafeas_occurrence_clone.to_link("clone")
    in_toto_link_clone.dump("in-toto-verify-links/clone.776a00e2.link")

    # Update Step
    grafeas_occurrence_update = GrafeasInTotoOccurrence.load("occurrences/update_occurrence.json")
    in_toto_link_update = grafeas_occurrence_update.to_link("update-version")
    in_toto_link_update.dump("in-toto-verify-links/update-version.776a00e2.link")
    
    # Package Step
    grafeas_occurrence_package = GrafeasInTotoOccurrence.load("occurrences/package_occurrence.json")
    in_toto_link_package = grafeas_occurrence_package.to_link("package")
    in_toto_link_package.dump("in-toto-verify-links/package.2f89b927.link")

    in_toto_verify(self.metadata, self.layout_key_dict, link_dir_path="in-toto-verify-links")

  #def test_link_occurrence_link_verify(self): # nonetype bug
  #  """Test in-toto-verify on in-toto link converted to Grafeas occurrence
  #  and back to an in-toto link."""
  #  # Clone Step
  #  in_toto_link_clone = Metablock.load("clone_link.json")
  #  grafeas_occurrence_clone = GrafeasInTotoOccurrence.from_link(in_toto_link_clone, "clone-step-name", "demo-project/foo.py")
  #  new_in_toto_link_clone = grafeas_occurrence_clone.to_link("clone-step-name")
  #  new_in_toto_link_clone.dump("in-toto-verify-links/clone.776a00e2.link")

  #  in_toto_verify(self.layout_metablock_clone, self.layout_key_dict,
  #    link_dir_path="in-toto-verify-links")

  #  # Update Step
  #  in_toto_link_update = Metablock.load("update_link.json")
  #  grafeas_occurrence_update = GrafeasInTotoOccurrence.from_link(in_toto_link_update, "update-step-name", "demo-project/foo.py")
  #  new_in_toto_link_update = grafeas_occurrence_update.to_link("update-step-name")
  #  new_in_toto_link_update.dump("in-toto-verify-links/update-version.776a00e2.link")

  #  in_toto_verify(self.layout, self.layout_key_dict, link_dir_path="in-toto-verify-links")
  #  
  #  # Package Step
  #  in_toto_link_package = Metablock.load("package_link.json")
  #  grafeas_occurrence_update = GrafeasInTotoOccurrence.from_link(in_toto_link_update, "package-step-name", "demo-project/foo.py")
  #  new_in_toto_link_update = grafeas_occurrence_update.to_link("package-step-name")
  #  new_in_toto_link_update.dump("in-toto-verify-links/package.2f89b927.link")

  #  in_toto_verify(self.layout, self.layout_key_dict, link_dir_path="in-toto-verify-links")

if __name__ == "__main__":
  unittest.main()
