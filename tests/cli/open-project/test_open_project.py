#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test command "open-project"
"""


def test_help(cli):
    code, out, err = cli.run(args=['open-project', '--help'])
    assert code == 0
    assert len(err) == 0
    assert len(out) > 20


def test_open_empty_project_absolute_path(cli):
    path = cli.abspath('data/Empty Project/Empty Project.lpp')
    code, out, err = cli.run(args=['open-project', path])
    assert code == 0
    assert len(err) == 0
    assert len(out) > 0
    assert out[-1] == 'SUCCESS'


def test_open_empty_project_relative_path(cli):
    path = 'data/Empty Project/Empty Project.lpp'
    code, out, err = cli.run(args=['open-project', path])
    assert code == 0
    assert len(err) == 0
    assert len(out) > 0
    assert out[-1] == 'SUCCESS'
