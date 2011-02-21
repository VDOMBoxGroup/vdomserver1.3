#!/usr/bin/python

"""
UUID generation utility
"""

import sys

sys.path.append("../src")

import xml.dom
import utils.uuid

print utils.uuid.uuid4()
