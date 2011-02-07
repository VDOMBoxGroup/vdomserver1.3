#!/usr/bin/python

"""
UUID generation utility
"""

import sys

sys.path.append("..")

import xml.dom
import src.util.uuid

print src.util.uuid.uuid4()
