#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

"""
Test "--help"
"""


def test_explicit(cli):
    code, out, err = cli.run(args=['--help'])
    assert code == 0
    assert len(err) == 0
    assert len(out) > 10
    assert re.match('Usage: .+', out[0])


def test_implicit_if_no_arguments(cli):
    code, out, err = cli.run(args=[])
    assert code == 0
    assert len(err) == 0
    assert len(out) > 10
    assert re.match('Usage: .+', out[0])


def test_implicit_if_passing_invalid_argument(cli):
    code, out, err = cli.run(args=['--invalid_argument'])
    assert code == 1
    assert len(err) > 0
    assert re.match('Unknown option .+', err[0])
    assert len(out) > 5
    assert re.match('Usage: .+', out[0])
