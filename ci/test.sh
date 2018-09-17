#!/usr/bin/env bash

# set shell settings (see https://sipb.mit.edu/doc/safe-shell/)
set -eufv -o pipefail

# run unit tests
if [ "${TRAVIS_OS_NAME-}" = "linux" ]
then
  xvfb-run -a ./build/output/qztest
  xvfb-run -a ./build/output/librepcb-unittests
elif [ "${TRAVIS_OS_NAME-}" = "osx" ]
then
  ./build/output/qztest
  ./build/output/librepcb-unittests
else
  ./build/output/qztest.exe
  ./build/output/librepcb-unittests.exe
fi

# run CLI tests
if [ "${TRAVIS_OS_NAME-}" = "linux" ]
then
  EXECUTABLE="`pwd`/LibrePCB-CLI-x86_64.AppImage"
  pushd ./tests/cli
  xvfb-run -a --server-args="-screen 0 1024x768x24" pytest -v --librepcb-executable="$EXECUTABLE"
  popd
elif [ "${TRAVIS_OS_NAME-}" = "osx" ]
then
  EXECUTABLE="`pwd`/build/install/opt/librepcb-cli.app/Contents/MacOS/librepcb-cli"
  pushd ./tests/funq
  pytest -v --librepcb-executable="$EXECUTABLE"
  popd
else
  EXECUTABLE="`pwd`/build/install/opt/bin/librepcb-cli.exe"
  pushd ./tests/funq
  pytest -v --librepcb-executable="$EXECUTABLE"
  popd
fi

# run functional tests
if [ "${TRAVIS_OS_NAME-}" = "linux" ]
then
  EXECUTABLE="`pwd`/LibrePCB-x86_64.AppImage"
  pushd ./tests/funq
  xvfb-run -a --server-args="-screen 0 1024x768x24" pytest -v --librepcb-executable="$EXECUTABLE"
  popd
elif [ "${TRAVIS_OS_NAME-}" = "osx" ]
then
  # TODO: funq does not yet work on macOS
  #EXECUTABLE="`pwd`/build/output/librepcb.app/Contents/MacOS/librepcb"
  #pushd ./tests/funq
  #funq "$EXECUTABLE"
  #pytest -v --librepcb-executable="$EXECUTABLE"
  #popd
else
  EXECUTABLE="`pwd`/build/install/opt/bin/librepcb.exe"
  pushd ./tests/funq
  pytest -v --librepcb-executable="$EXECUTABLE"
  popd
fi
