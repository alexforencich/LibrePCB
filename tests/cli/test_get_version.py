#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test "--version"
"""

import os


def test_version(cli):
    code, out, err = cli.run(args=['--version'])
    print(out)
    print(err)
    assert code == -12
