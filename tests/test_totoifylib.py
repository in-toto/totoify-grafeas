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

from in_toto.models.layout import Layout
from in_toto.models.metadata import Metablock
from in_toto.verifylib import in_toto_verify
from securesystemslib import interface

from totoify_grafeas.totoifylib import GrafeasInTotoOccurrence


class TestCreateInTotoLinkFromOccurrence(unittest.TestCase):
  """Tests conversion of a Grafeas occurrence to an in-toto link."""
  def test_create_in_toto_link_from_grafeas_occurrence(self):
    grafeas_occurrence = \
        GrafeasInTotoOccurrence.load("occurrences/clone.776a00e2.occurrence")
    in_toto_link = grafeas_occurrence.to_link("clone")
    self.assertIsInstance(in_toto_link, Metablock)

    in_toto_link_original = Metablock.load("links/clone.776a00e2.link")
    self.assertEqual(in_toto_link, in_toto_link_original)


class TestCreateOccurranceFromInTotoLink(unittest.TestCase):
  """Tests conversion of an in-toto link to a Grafeas occurrence."""
  def test_create_grafeas_occurrence_from_in_toto_link(self):
    in_toto_link = Metablock.load("links/clone.776a00e2.link")
    grafeas_occurrence = \
        GrafeasInTotoOccurrence.from_link(in_toto_link, "clone",
                                          "clone-resource-uri")

    self.assertIsInstance(grafeas_occurrence, GrafeasInTotoOccurrence)


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
            "expected_products": [["CREATE", "demo-project/foo.py"],
                                  ["DISALLOW", "*"]],
            "pubkeys": [self.key_bob["keyid"]],
            "expected_command": [
                "git",
                "clone",
                "https://github.com/in-toto/demo-project.git"
            ],
            "threshold": 1,
          }, {
            "name": "update-version",
            "expected_materials": [["MATCH", "demo-project/*", "WITH",
                                    "PRODUCTS", "FROM", "clone"],
                                   ["DISALLOW", "*"]],
            "expected_products": [["ALLOW", "demo-project/foo.py"],
                                  ["DISALLOW", "*"]],
            "pubkeys": [self.key_bob["keyid"]],
            "expected_command": [],
            "threshold": 1,
          }, {
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
    self.layout_key_dict.update(
        interface.import_publickeys_from_file(["keys/alice.pub"]))

  def tearDown(self):
    for f in os.listdir("in-toto-verify-links"):
      if f == ".keep":  # empty file to retain the directory in repository
        continue
      os.remove(os.path.join("in-toto-verify-links", f))

  def test_grafeas_occurrence_to_in_toto_link_verify(self):
    """Test in-toto-verify on in-toto link generated from Grafeas occurrence.
    """
    for f in os.listdir("occurrences"):
      occurrence = GrafeasInTotoOccurrence.load(os.path.join("occurrences", f))
      # this is hacky, yes, but since we control the test metadata...
      step_name, keyid, _ = f.split(".")
      in_toto_link = occurrence.to_link(step_name)
      in_toto_link.dump("in-toto-verify-links/{}.{}.link".format(step_name, keyid))

    # The test passes if in_toto_verify passes
    in_toto_verify(self.metadata,
                   self.layout_key_dict,
                   link_dir_path="in-toto-verify-links")


if __name__ == "__main__":
  unittest.main()
