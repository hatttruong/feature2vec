/**
 * This source code, based on FastText source code, is modified to fit my
 * application
 */

#include <iostream>
#include <fstream>
#include <queue>
#include <iomanip>
#include "feature2vec.h"
#include "args.h"
#include "dictionary.h"
#include "test.h"

using namespace feature2vec;

void printUsage() {
  std::cerr
      << "usage: feature2vec <command> <args>\n\n"
      << "The commands supported by feature2vec are:\n\n"
      << "  skipgram                train a feature2vec model using skipgram\n"
      << "  cbow                    train a feature2vec model using cbow\n"
      << "  test                    test a feature2vec model\n"
      // << "  print-feature-vectors   print feature vectors given a trained model\n"
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
  UnitTest ut = UnitTest();
  ut.run();
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
