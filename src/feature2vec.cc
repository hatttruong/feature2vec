/**
 * Copyright (c) 2016-present, Facebook, Inc.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

#include "feature2vec.h"

#include <iostream>
#include <sstream>
#include <iomanip>
#include <thread>
#include <string>
#include <vector>
#include <algorithm>
#include <stdexcept>
#include <numeric>


namespace feature2vec {

constexpr int32_t FEATURE2VEC_VERSION = 1;
constexpr int32_t FEATURE2VEC_FILEFORMAT_MAGIC_INT32 = 793712314;

Feature2Vec::Feature2Vec() {}

void Feature2Vec::trainThread(int32_t threadId) {
  std::ifstream ifs(args_->input);
  utils::seek(ifs, threadId * utils::size(ifs) / args_->thread);

  Model model(input_, output_, args_, threadId);
  model.setTargetCounts(dict_->getCounts());

  const int64_t nevents = dict_->nevents();
  int64_t localEventCount = 0;
  std::vector<int32_t> events; // list of events of one admission
  while (eventCount_ < args_->epoch * nevents) {
    real progress = real(eventCount_) / (args_->epoch * nevents);
    real lr = args_->lr * (1.0 - progress);
    if (args_->model == model_name::cbow) {
      localEventCount += dict_->getEvents(ifs, events, model.rng);
      cbow(model, lr, events);
    } else if (args_->model == model_name::sg) {
      localEventCount += dict_->getEvents(ifs, events, model.rng);
      // skipgram(model, lr, events);
    }
    if (localEventCount > args_->lrUpdateRate) {
      eventCount_ += localEventCount;
      localEventCount = 0;
      if (threadId == 0 && args_->verbose > 1)
        loss_ = model.getLoss();
    }
  }
  if (threadId == 0)
    loss_ = model.getLoss();
  ifs.close();
}

void Feature2Vec::train(const Args args) {
  args_ = std::make_shared<Args>(args);
  dict_ = std::make_shared<Dictionary>(args_);

  // count number of tokens
  std::ifstream ifs(args_->input);
  if (!ifs.is_open()) {
    throw std::invalid_argument(args_->input + " cannot be opened for training!");
  }
  dict_->readFromFile(ifs);
  ifs.close();

  input_ = std::make_shared<Matrix>(dict_->nfeatures() + args_->bucket, args_->dim);
  input_->uniform(1.0 / args_->dim);

  output_ = std::make_shared<Matrix>(dict_->nfeatures(), args_->dim);

  output_->zero();
  startThreads();
  model_ = std::make_shared<Model>(input_, output_, args_, 0);
  model_->setTargetCounts(dict_->getCounts());

}

void Feature2Vec::startThreads() {
  start_ = std::chrono::steady_clock::now();
  eventCount_ = 0;
  loss_ = -1;
  std::vector<std::thread> threads;
  for (int32_t i = 0; i < args_->thread; i++) {
    threads.push_back(std::thread([ = ]() { trainThread(i); }));
  }
  const int64_t nevents = dict_->nevents();
  // Same condition as trainThread
  while (eventCount_ < args_->epoch * nevents) {
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    if (loss_ >= 0 && args_->verbose > 1) {
      real progress = real(eventCount_) / (args_->epoch * nevents);
      std::cerr << "\r";
      printInfo(progress, loss_, std::cerr);
    }
  }
  for (int32_t i = 0; i < args_->thread; i++) {
    threads[i].join();
  }
  if (args_->verbose > 0) {
    std::cerr << "\r";
    printInfo(1.0, loss_, std::cerr);
    std::cerr << std::endl;
  }
}

void Feature2Vec::printInfo(real progress, real loss, std::ostream& log_stream) {
  std::chrono::steady_clock::time_point end = std::chrono::steady_clock::now();
  double t = std::chrono::duration_cast<std::chrono::duration<double>> (end - start_).count();
  double lr = args_->lr * (1.0 - progress);
  double wst = 0;

  int64_t eta = 2592000; // Default to one month in seconds (720 * 3600)

  if (progress > 0 && t >= 0) {
    progress = progress * 100;
    eta = t * (100 - progress) / progress;
    wst = double(eventCount_) / t / args_->thread;
  }
  int32_t etah = eta / 3600;
  int32_t etam = (eta % 3600) / 60;

  log_stream << std::fixed;
  log_stream << "Progress: ";
  log_stream << std::setprecision(1) << std::setw(5) << progress << "%";
  log_stream << " features/sec/thread: " << std::setw(7) << int64_t(wst);
  log_stream << " lr: " << std::setw(9) << std::setprecision(6) << lr;
  log_stream << " loss: " << std::setw(9) << std::setprecision(6) << loss;
  log_stream << " ETA: " << std::setw(3) << etah;
  log_stream << "h" << std::setw(2) << etam << "m";
  log_stream << std::flush;
}


void Feature2Vec::cbow(Model& model, real lr,
                       const std::vector<int32_t>& events) {
  std::vector<int32_t> bow;
  std::uniform_int_distribution<> uniform(1, args_->ws);
  // for (int32_t w = 0; w < events.size(); w++) {
  //   int32_t boundary = uniform(model.rng);
  //   bow.clear();
  //   for (int32_t c = -boundary; c <= boundary; c++) {
  //     if (c != 0 && w + c >= 0 && w + c < events.size()) {
  //       const std::vector<int32_t>& ngrams = dict_->getSubwords(events[w + c]);
  //       bow.insert(bow.end(), ngrams.cbegin(), ngrams.cend());
  //     }
  //   }
  //   model.update(bow, events[w], lr);
  // }
}

void Feature2Vec::skipgram(Model& model, real lr,
                           const std::vector<int32_t>& events) {
  std::uniform_int_distribution<> uniform(1, args_->ws);
  // for (int32_t w = 0; w < events.size(); w++) {
  //   int32_t boundary = uniform(model.rng);
  //   const std::vector<int32_t>& ngrams = dict_->getSubwords(events[w]);
  //   for (int32_t c = -boundary; c <= boundary; c++) {
  //     if (c != 0 && w + c >= 0 && w + c < events.size()) {
  //       model.update(ngrams, events[w + c], lr);
  //     }
  //   }
  // }
}

}
