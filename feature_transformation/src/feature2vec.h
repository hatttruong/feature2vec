/**
 * This source code, based on FastText source code, is modified to fit my
 * application
 */

#pragma once

#include <time.h>

#include <atomic>
#include <memory>
#include <set>
#include <chrono>
#include <iostream>
#include <queue>
#include <tuple>

#include "args.h"
#include "dictionary.h"
#include "matrix.h"
#include "model.h"
#include "real.h"
#include "utils.h"
#include "vector.h"

namespace feature2vec {

class Feature2Vec {
protected:
  std::shared_ptr<Args> args_;
  std::shared_ptr<Dictionary> dict_;

  std::shared_ptr<Matrix> input_;
  std::shared_ptr<Matrix> output_;

  std::shared_ptr<Model> model_;

  std::atomic<int64_t> eventCount_;
  std::atomic<real> loss_;

  std::chrono::steady_clock::time_point start_;
  void signModel(std::ostream&);
  bool checkModel(std::istream&);

  int32_t version;

  void startThreads();

public:
  Feature2Vec();

  // int32_t getWordId(const std::string&) const;
  // int32_t getSubwordId(const std::string&) const;
  void sumAndNormalizeNSegments(Vector&, const std::vector<int32_t>&) const;
  void getFeatureVector(Vector&, const int32_t) const;
  void getFeatureVector(Vector&, const int32_t, const std::string&) const;
  // void getVector(Vector&, const std::string&) const;
  // void getSubwordVector(Vector&, const std::string&) const;
  void addInputVector(Vector&, int32_t) const;
  // inline void getInputVector(Vector& vec, int32_t ind) {
  //   vec.zero();
  //   addInputVector(vec, ind);
  // }

  // const Args getArgs() const;
  // std::shared_ptr<const Dictionary> getDictionary() const;
  // std::shared_ptr<const Matrix> getInputMatrix() const;
  // std::shared_ptr<const Matrix> getOutputMatrix() const;
  void saveVectors();
  void saveModel(const std::string);
  void saveModel();
  void loadModel(std::istream&);
  void loadModel(const std::string&);
  void printInfo(real, real, std::ostream&);


  void train(const Args);
  void cbow(Model&, real, const std::vector<event_entry>&);
  void skipgram(Model&, real, const std::vector<event_entry>&);
  // void precomputeWordVectors(Matrix&);
  // void ngramVectors(std::string);
  // std::vector<int32_t> selectEmbeddings(int32_t) const;
  int getDimension() const;
  void trainThread(int32_t);
  // void loadVectors(std::string);

  // unused methods:


  // void getSentenceVector(std::istream&, Vector&);
  // void quantize(const Args);
  // std::tuple<int64_t, double, double> test(std::istream&, int32_t, real = 0.0);
  // void predict(std::istream&, int32_t, bool, real = 0.0);
  // void predict(
  //     std::istream&,
  //     int32_t,
  //     std::vector<std::pair<real, std::string>>&,
  //     real = 0.0) const;

  // void findNN(
  //     const Matrix&,
  //     const Vector&,
  //     int32_t,
  //     const std::set<std::string>&,
  //     std::vector<std::pair<real, std::string>>& results);
  // void analogies(int32_t);

  // bool isQuant() const;
};
}
