#
# Copyright (c) 2016-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#

CXX = c++
CXXFLAGS = -pthread -std=c++0x -march=native -ljsoncpp
OBJS =  jsoncpp.o args.o dictionary.o matrix.o vector.o model.o utils.o feature2vec.o
INCLUDES = -I.

opt: CXXFLAGS += -O3 -funroll-loops
opt: feature2vec

debug: CXXFLAGS += -g -O0 -fno-inline
debug: feature2vec

jsoncpp.o: src/jsoncpp.cpp src/json/json.h
	$(CXX) $(CXXFLAGS) -c src/jsoncpp.cpp

args.o: src/args.cc src/args.h
	$(CXX) $(CXXFLAGS) -c src/args.cc

dictionary.o: src/dictionary.cc src/dictionary.h src/args.h src/json/json.h
	$(CXX) $(CXXFLAGS) -c src/dictionary.cc

matrix.o: src/matrix.cc src/matrix.h src/utils.h
	$(CXX) $(CXXFLAGS) -c src/matrix.cc

vector.o: src/vector.cc src/vector.h src/utils.h
	$(CXX) $(CXXFLAGS) -c src/vector.cc

model.o: src/model.cc src/model.h src/args.h
	$(CXX) $(CXXFLAGS) -c src/model.cc

utils.o: src/utils.cc src/utils.h
	$(CXX) $(CXXFLAGS) -c src/utils.cc

feature2vec.o: src/feature2vec.cc src/*.h
	$(CXX) $(CXXFLAGS) -c src/feature2vec.cc

feature2vec: $(OBJS) src/feature2vec.cc
	$(CXX) $(CXXFLAGS) $(OBJS) src/main.cc -o feature2vec

clean:
	rm -rf *.o feature2vec
