#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

"""
Test "--version"
"""


def test_valid_call(cli):
    code, out, err = cli.run(args=['--version'])
    assert code == 0
    assert len(err) == 0
    assert len(out) == 4
    assert re.match('LibrePCB CLI Version \d+\.\d+\.\d+$', out[0])
    assert re.match('Git Revision .+', out[1])
    assert re.match('Qt Version .+', out[2])
    assert re.match('Built at .+', out[3])
