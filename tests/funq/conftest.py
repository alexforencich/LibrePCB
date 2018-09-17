#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import pytest
import funq
from funq.client import ApplicationContext, ApplicationConfig


FUNQ_DIR = os.path.dirname(__file__)
TESTS_DIR = os.path.dirname(FUNQ_DIR)
REPO_DIR = os.path.dirname(TESTS_DIR)
DATA_DIR = os.path.join(TESTS_DIR, 'data')
FUNQ_DATA_DIR = os.path.join(DATA_DIR, 'funq')
FIXTURES_DATA_DIR = os.path.join(FUNQ_DATA_DIR, 'fixtures')


def pytest_addoption(parser):
    parser.addoption("--librepcb-executable",
                     action="store",
                     help="Path to librepcb executable to test")


class GlobalOptions:
    def __init__(self):
        self.funq_conf = 'funq.conf'
        self.funq_attach_exe = funq.tools.which('funq')
        self.funq_gkit = 'default'
        self.funq_gkit_file = os.path.join(os.path.dirname(os.path.realpath(funq.client.__file__)), 'aliases-gkits.conf')


class Application(object):
    def __init__(self, executable, env=None, args=()):
        super(Application, self).__init__()
        cfg = ApplicationConfig(executable=executable, args=args, cwd=os.getcwd(), env=env,
                                aliases=os.path.join(FUNQ_DIR, 'aliases'), global_options=GlobalOptions())
        self._context = ApplicationContext(cfg)

    def __enter__(self):
        return self._context.funq

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self._context


class LibrePcbFixture(object):
    def __init__(self, config, tmpdir):
        super(LibrePcbFixture, self).__init__()
        self.executable = os.path.abspath(config.getoption('--librepcb-executable'))
        if not os.path.exists(self.executable):
            raise Exception("Executable '{}' not found. Please pass it with "
                            "'--librepcb-executable'.".format(self.executable))
        self.tmpdir = tmpdir
        # Copy test data to temporary directory to avoid modifications in original data
        self.data_dir = os.path.join(self.tmpdir, 'data')
        shutil.copytree(FUNQ_DATA_DIR, self.data_dir)
        # Init members to default values
        self.workspace_path = os.path.join(self.data_dir, 'fixtures', 'Empty Workspace')
        self.project_path = None

    def abspath(self, relpath):
        return os.path.join(self.tmpdir, relpath)

    def set_workspace(self, path):
        if not os.path.isabs(path):
            path = self.abspath(path)
        self.workspace_path = path

    def set_project(self, path):
        if not os.path.isabs(path):
            path = self.abspath(path)
        self.project_path = path

    def open(self):
        self._create_application_config_file()
        return Application(self.executable, env=self._env(), args=self._args())

    def _create_application_config_file(self):
        config_dir = os.path.join(self.tmpdir, 'config', 'LibrePCB')
        config_ini = os.path.join(config_dir, 'LibrePCB.ini')
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        with open(config_ini, 'w') as f:
            if self.workspace_path:
                f.write("[workspaces]\n")
                f.write("most_recently_used=\"{}\"\n".format(self.workspace_path.replace('\\', '/')))

    def _args(self):
        args = []
        if self.project_path:
            args.append(self.project_path)
        return args

    def _env(self):
        env = os.environ
        # Make GUI independent from the system's language
        env['LC_ALL'] = 'C'
        # Override configuration location to make tests independent of existing configs
        env['LIBREPCB_CONFIG_DIR'] = os.path.join(self.tmpdir, 'config')
        # Use a neutral username
        env['USERNAME'] = 'testuser'
        # Force LibrePCB to use Qt-style file dialogs because native dialogs don't work
        env['LIBREPCB_DISABLE_NATIVE_DIALOGS'] = '1'
        return env


@pytest.fixture(scope="session")
def librepcb_server():
    """
    Fixture which provides a HTTP server at localhost:8080

    All tests should use this server instead of the official LibrePCB API server
    or GitHub for downloading libraries.
    """
    import time
    import threading
    import socket
    import socketserver
    import http.server

    class Handler(http.server.SimpleHTTPRequestHandler, object):
        def translate_path(self, path):
            path = super(Handler, self).translate_path(path)
            relpath = os.path.relpath(path, os.curdir)
            return os.path.join(FIXTURES_DATA_DIR, 'server', relpath)

    # Set SO_REUSEADDR option to avoid "port already in use" errors
    httpd = socketserver.TCPServer(("", 50080), Handler, bind_and_activate=False)
    httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    httpd.server_bind()
    httpd.server_activate()
    thread = threading.Thread(target=httpd.serve_forever)
    thread.daemon = True
    thread.start()
    time.sleep(0.2)  # wait a bit to make sure the server is ready


@pytest.fixture
def create_librepcb(request, tmpdir, librepcb_server):
    """
    Fixture allowing to create multiple application instances
    """
    def _create():
        return LibrePcbFixture(request.config, str(tmpdir))
    return _create


@pytest.fixture
def librepcb(create_librepcb):
    """
    Fixture allowing to create one application instance
    """
    yield create_librepcb()
