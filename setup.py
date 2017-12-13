#!/usr/bin/env python
"""
<Program Name>
  setup.py
<Author>
  Santiago Torres <santiago@nyu.edu>
  Lukas Puehringer <lukas.puehringer@nyu.edu>

<Started>
 December 13, 2017

<Purpose>
  setup.py script to install in-toto enabled grafaes API client. To install
  dependencies and put the in-toto grafeas scripts on the path.

"""
from setuptools import setup, find_packages

setup(
  name="totoify-grafeas-client",
  version="0.1.0",
  author="New York University: Secure Systems Lab",
  author_email="in-toto-dev@googlegroups.com",
  url="https://github.com/in-toto/totoify-grafeas.git",
  packages=["client"],
  install_requires=["in-toto==0.1.1", "urllib3", "certifi"],
  entry_points={
    "console_scripts": [
      "grafeas-load = client.grafeas_load:main",
      "grafeas-run = client.grafeas_run:main",
      "grafeas-verify = client.grafeas_verify:main"
    ]
  }
)