/**
 * Copyright (c) 2016-present, Facebook, Inc.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

#pragma once

#include <istream>
#include <ostream>
#include <string>
#include <vector>

namespace feature2vec {

enum class model_name : int { cbow = 1, sg};
enum class loss_name : int { hs = 1, ns, softmax };

class Args {
protected:
  std::string lossToString(loss_name) const;
  std::string boolToString(bool) const;
  std::string modelToString(model_name) const;

public:
  Args();
  std::string dict;
  std::string input;
  std::string output;
  double lr;
  int lrUpdateRate;
  int dim;
  int ws;
  int multiEvents;
  int maxStatic;
  double ps;
  int epoch;
  int minCount;
  int neg;
  loss_name loss;
  model_name model;
  int bucket;
  int thread;
  double t;
  int verbose;
  std::string pretrainedVectors;

  void parseArgs(const std::vector<std::string>& args);
  void printHelp();
  void printBasicHelp();
  void printDictionaryHelp();
  void printTrainingHelp();
  void save(std::ostream&);
  void load(std::istream&);
  void dump(std::ostream&) const;
};
}
