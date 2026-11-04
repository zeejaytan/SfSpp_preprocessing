#!/bin/bash
# preflight303.sh -- build the pristine objects once and compile the instrumented
# shim, INSIDE the SIF, before spending the arm loop. Runs in $WORK (=/panel).
# Mirrors arm67.sh:31-59 for one arm so a compile error surfaces in minutes.
# Usage: bash /panel/preflight303.sh INCDIR
set -uo pipefail
INC=$1
BUILD=/panel/build
D=$BUILD/CMakeFiles/Hierarchy-Clear.dir
if [ ! -f $BUILD/CMakeCache.txt ]; then
  echo "--- pristine objects: cold build"
  mkdir -p $BUILD
  cd $BUILD
  cmake /opt/sfs-pristine -DCMAKE_BUILD_TYPE=Release > /panel/logs/cmake.log 2>&1 || { echo "!!!! cmake failed"; exit 1; }
  make -j8 > /panel/logs/make.log 2>&1 || { echo "!!!! make failed"; exit 1; }
else
  echo "--- pristine objects: reusing $BUILD"
fi
cd $BUILD
DEFS=$(grep "^CXX_DEFINES" $D/flags.make | cut -d= -f2- | tr " " "\n" | grep -v GOOGLE_GLOG_DLL_DECL | tr "\n" " ")
INCS=$(grep "^CXX_INCLUDES" $D/flags.make | cut -d= -f2-)
FLAGS=$(grep "^CXX_FLAGS" $D/flags.make | cut -d= -f2-)
g++ -I$INC $DEFS $INCS $FLAGS -I/opt/sfs-pristine -I/opt/sfs-pristine/class -c /panel/shim/GA.cpp -o $D/shim_PREFLIGHT.o
RC=$?
echo "--- preflight compile rc=$RC"
if [ $RC -ne 0 ]; then echo "!!!! instrumented shim does not compile"; exit 1; fi
rm -f $D/shim_PREFLIGHT.o
echo "--- preflight OK"
exit 0
