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
      << "  print-feature-vectors   print feature vectors given a trained model\n"
      << std::endl;
}


void printFeatureVectorsUsage() {
  std::cerr
      << "usage: feature2vec print-word-vectors <model> <test_file> <output>\n\n"
      << "  <model>      model filename\n"
      << "  <test_file>  test file, each line includes <conceptid>,<value>\n"
      << "  <output>     output filename contains vectors\n"
      << std::endl;
}


// read line and split it by ','
// return a vector of string
bool readLine(std::istream& in, std::vector<std::string>& v) {
  std::streambuf& sb = *in.rdbuf();
  int c;
  std::string temp_word;
  v.clear();
  while ((c = sb.sbumpc()) != EOF) {

    if (c == ',' || c == '\n') {
      v.push_back(temp_word);
      temp_word.clear();

      if (c == '\n') {
        return true;
      }
    } else {
      temp_word.push_back(c);
    }
  }
  return false;
}

void printFeatureVectors(const std::vector<std::string> args) {
  if (args.size() != 5) {
    printFeatureVectorsUsage();
    exit(EXIT_FAILURE);
  }

  Feature2Vec feature2vec;
  feature2vec.loadModel(std::string(args[2]));
  Vector vec(feature2vec.getDimension());

  // open queries file
  std::ifstream ifs(args[3]);
  if (!ifs.is_open()) {
    throw std::invalid_argument(args[3] + " cannot be opened for querying!");
  }

  // open output file
  std::ofstream ofs(args[4]);
  if (!ofs.is_open()) {
    throw std::invalid_argument(
      args[4] + " cannot be opened for saving vectors!");
  }

  std::string::size_type sz;   // alias of size_t
  std::vector<std::string> v;
  int32_t conceptid;
  while (readLine(ifs, v)) {
    // conceptid,value
    if (v.size() >= 2) {
      conceptid = std::stoi(v[0], &sz);
      std::cerr << "Data: conceptid=" << conceptid << ", value=" << v[1] << std::endl;
      feature2vec.getFeatureVector(vec, conceptid, v[1]);
      ofs << vec << std::endl;
    }
  }
  ofs.close();
  ifs.close();
  exit(0);
}


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
  UnitTest ut = UnitTest(a);
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
  }  else if (command == "print-feature-vectors") {
    printFeatureVectors(args);
  } else {
    printUsage();
    exit(EXIT_FAILURE);
  }
  return 0;
}
