/**
 * Copyright (c) 2016-present, Facebook, Inc.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

#include <iostream>
#include <fstream>
#include <queue>
#include <iomanip>
#include "feature2vec.h"
#include "args.h"
#include "dictionary.h"

using namespace feature2vec;

void printUsage() {
  std::cerr
      << "usage: feature2vec <command> <args>\n\n"
      << "The commands supported by feature2vec are:\n\n"
      << "  train                   train a feature2vec model\n"
      << "  print-feature-vectors   print feature vectors given a trained model\n"
      << std::endl;
}


void printFeatureVectorsUsage() {
  std::cerr
      << "usage: feature2vec print-word-vectors <model>\n\n"
      << "  <model>      model filename\n"
      << std::endl;
}


// void printFeatureVectors(const std::vector<std::string> args) {
//   if (args.size() != 3) {
//     printFeatureVectorsUsage();
//     exit(EXIT_FAILURE);
//   }
//   Feature2Vec feature2vec;
//   feature2vec.loadModel(std::string(args[2]));
//   std::string word;
//   Vector vec(feature2vec.getDimension());
//   while (std::cin >> word) {
//     feature2vec.getWordVector(vec, word);
//     std::cout << word << " " << vec << std::endl;
//   }
//   exit(0);
// }


void train(const std::vector<std::string> args) {
  Args a = Args();
  a.parseArgs(args);
  Feature2Vec feature2vec;
  std::ofstream ofs(a.output + ".bin");
  if (!ofs.is_open()) {
    throw std::invalid_argument(a.output + ".bin cannot be opened for saving.");
  }
  ofs.close();
  feature2vec.train(a);
  feature2vec.saveModel();
  feature2vec.saveVectors();
  if (a.saveOutput) {
    feature2vec.saveOutput();
  }
}

void test(const std::vector<std::string> args) {
  Args a = Args();
  a.parseArgs(args);

  // Test dictionary
  std::shared_ptr<Args> args_;
  args_ = std::make_shared<Args>(a);
  std::shared_ptr<Dictionary> dict_;
  dict_ = std::make_shared<Dictionary>(args_);
  std::string token = "Runs Vtach";
  dict_->hash(token);
}


int main(int argc, char** argv) {
  std::vector<std::string> args(argv, argv + argc);
  if (args.size() < 2) {
    printUsage();
    exit(EXIT_FAILURE);
  }
  std::string command(args[1]);
  if (command == "test") {
    test(args);
  } else if (command == "skipgram" || command == "cbow") {
    train(args);
  } else {
    printUsage();
    exit(EXIT_FAILURE);
  }
  return 0;
}
