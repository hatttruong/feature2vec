/**
 * This source code, based on FastText source code, is modified to fit my
 * application
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

void Feature2Vec::addInputVector(Vector& vec, int32_t ind) const {
  vec.addRow(*input_, ind);
}

void Feature2Vec::trainThread(int32_t threadId) {
  std::ifstream ifs(args_->input);
  int64_t start_pos = dict_->getAdmissionPosition(threadId, args_->thread);
  utils::seek(ifs, start_pos);

  Model model(input_, output_, args_, threadId);
  model.setTargetCounts(dict_->getCounts());

  const int64_t nevents = dict_->nevents();
  int64_t localEventCount = 0;
  std::vector<event_entry> events; // list of events of one admission
  while (eventCount_ < args_->epoch * nevents) {
    real progress = real(eventCount_) / (args_->epoch * nevents);
    real lr = args_->lr * (1.0 - progress);
    if (args_->model == model_name::cbow) {
      localEventCount += dict_->getEvents(ifs, events, model.rng);
      cbow(model, lr, events);
    } else if (args_->model == model_name::sg) {
      localEventCount += dict_->getEvents(ifs, events, model.rng);
      skipgram(model, lr, events);
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


// events: vector<event_entry> which order by minutes_ago
// Model::update(const std::vector<int32_t>& input, int32_t target, real lr)
// In CBOW model, input is bounded events, target is the current event
// TODO: mutiply boundary with a constant because there are many events happen
// at the same time
void Feature2Vec::cbow(Model& model, real lr,
                       const std::vector<event_entry>& events) {
  // bow: contains index of events (themself and their segments, separately)
  std::vector<int32_t> bow;
  std::uniform_int_distribution<> uniform(1, args_->ws);
  int32_t boundary;
  for (int32_t i = 0; i < events.size(); i++) {
    boundary = uniform(model.rng);
    bow.clear();
    for (int32_t c = -boundary; c <= boundary; c++) {
      if (c != 0 && i + c >= 0 && i + c < events.size()) {
        const std::vector<int32_t>& nsegments = dict_->getSegments(events[i + c].idx);
        bow.insert(bow.end(), nsegments.cbegin(), nsegments.cend());
      }
    }
    model.update(bow, events[i].idx, lr);
  }
}


// events: vector<event_entry> which is sorted by minutes_ago ASC
//         static events have minutes_ago = -1
// Model::update(const std::vector<int32_t>& input, int32_t target, real lr)
// In Skipgram model:
//    input is current events (vector of segments)
//    target is index of bounded event
// Modification:
// (1) mutiply boundary with a constant because there are many events happen
// at the same time
// (2) seperate updating model between static and non-static events
void Feature2Vec::skipgram(Model& model, real lr,
                           const std::vector<event_entry>& events) {
  std::uniform_int_distribution<> uniform(1, args_->ws * args_->multiEvents);

  // specify number of static features
  int32_t nb_static = 0;
  for (int32_t i = args_->maxStatic - 1; i >= 0; i--) {
    if (events[i].minutes_ago == -1) {
      nb_static = i + 1;
      break;
    }
  }

  std::uniform_int_distribution<> uniform_st(0, nb_static - 1);
  std::uniform_int_distribution<> uniform_nst(nb_static, events.size() - 1);

  // update static features with non-static feature context
  int32_t c_idx;
  for (int32_t i = 0; i < nb_static; i++) {
    const std::vector<int32_t>& nsegments = dict_->getSegments(events[i].idx);

    // update with context of a half number of non-static features
    for (int32_t j = 0; j < (events.size() - nb_static) * args_->ps; j++) {
      c_idx = uniform_nst(model.rng);
      model.update(nsegments, events[c_idx].idx, lr);
    }
  }

  // update non-static features with static and other non-static features in boundary
  int32_t boundary;
  int32_t below_mins_ago;
  int32_t above_mins_ago;
  for (int32_t i = nb_static; i < events.size(); i++) {
    const std::vector<int32_t>& nsegments = dict_->getSegments(events[i].idx);

    // STATIC CONTEXT
    // update with context of a half number of static features
    for (int32_t j = 0; j < nb_static * args_->ps; j++) {
      c_idx = uniform_st(model.rng);
      model.update(nsegments, events[c_idx].idx, lr);
    }

    // NONE-STATIC context
    below_mins_ago = events[i].minutes_ago - args_->ws;
    above_mins_ago = events[i].minutes_ago + args_->ws;
    boundary = uniform(model.rng);
    for (int32_t c = - boundary; c <= + boundary; c++) {
      if (c != 0 && i + c >= nb_static && i + c < events.size()) {

        if (events[i + c].minutes_ago >= below_mins_ago
            && events[i + c].minutes_ago <= above_mins_ago) {
          model.update(nsegments, events[i + c].idx, lr);
        }
      }
    }
  }
}

void Feature2Vec::getFeatureVector(Vector & vec, const int32_t idx) const {
  const std::vector<int32_t>& nsegments = dict_->getSegments(idx);
  sumAndNormalizeNSegments(vec, nsegments);
}

void Feature2Vec::getFeatureVector(Vector & vec, const int32_t conceptid,
                                   const std::string & value) const {
  const std::vector<int32_t>& nsegments = dict_->getSegments(conceptid, value);
  sumAndNormalizeNSegments(vec, nsegments);
}

void Feature2Vec::sumAndNormalizeNSegments(Vector & vec,
    const std::vector<int32_t>& nsegments) const {
  vec.zero();
  for (int i = 0; i < nsegments.size(); i++) {
    addInputVector(vec, nsegments[i]);
  }
  if (nsegments.size() > 0) {
    vec.mul(1.0 / nsegments.size());
  }
}

void Feature2Vec::saveModel() {
  std::string fn(args_->output);
  fn += ".bin";
  saveModel(fn);
}

void Feature2Vec::saveModel(const std::string path) {
  std::ofstream ofs(path, std::ofstream::binary);
  if (!ofs.is_open()) {
    throw std::invalid_argument(path + " cannot be opened for saving!");
  }
  signModel(ofs);
  args_->save(ofs);
  dict_->save(ofs);
  input_->save(ofs);
  output_->save(ofs);
  ofs.close();
}

bool Feature2Vec::checkModel(std::istream & in) {
  int32_t magic;
  in.read((char*) & (magic), sizeof(int32_t));
  if (magic != FEATURE2VEC_FILEFORMAT_MAGIC_INT32) {
    return false;
  }
  in.read((char*) & (version), sizeof(int32_t));
  if (version > FEATURE2VEC_VERSION) {
    return false;
  }
  return true;
}

void Feature2Vec::signModel(std::ostream & out) {
  const int32_t magic = FEATURE2VEC_FILEFORMAT_MAGIC_INT32;
  const int32_t version = FEATURE2VEC_VERSION;
  out.write((char*) & (magic), sizeof(int32_t));
  out.write((char*) & (version), sizeof(int32_t));
}

void Feature2Vec::saveVectors() {
  std::ofstream ofs(args_->output + ".vec");
  if (!ofs.is_open()) {
    throw std::invalid_argument(
      args_->output + ".vec" + " cannot be opened for saving vectors!");
  }
  ofs << dict_->nfeatures() << " " << args_->dim << std::endl;
  Vector vec(args_->dim);
  for (int32_t i = 0; i < dict_->nfeatures(); i++) {
    entry f = dict_->getFeature(i);
    getFeatureVector(vec, i);
    ofs << f.conceptid << "," <<  f.value << "," << vec << std::endl;
  }
  ofs.close();
}

void Feature2Vec::saveOutput() {
  std::ofstream ofs(args_->output + ".output");
  if (!ofs.is_open()) {
    throw std::invalid_argument(
      args_->output + ".output" + " cannot be opened for saving vectors!");
  }

  int32_t n = dict_->nfeatures();
  ofs << n << " " << args_->dim << std::endl;
  Vector vec(args_->dim);
  for (int32_t i = 0; i < n; i++) {
    entry f = dict_->getFeature(i);
    vec.zero();
    vec.addRow(*output_, i);
    ofs << f.conceptid << "," <<  f.value << "," << vec << std::endl;
  }
  ofs.close();
}

void Feature2Vec::loadModel(const std::string & filename) {
  std::ifstream ifs(filename, std::ifstream::binary);
  if (!ifs.is_open()) {
    throw std::invalid_argument(filename + " cannot be opened for loading!");
  }
  if (!checkModel(ifs)) {
    throw std::invalid_argument(filename + " has wrong file format!");
  }
  loadModel(ifs);
  ifs.close();
}

void Feature2Vec::loadModel(std::istream & in) {
  args_ = std::make_shared<Args>();
  input_ = std::make_shared<Matrix>();
  output_ = std::make_shared<Matrix>();
  args_->load(in);
  dict_ = std::make_shared<Dictionary>(args_, in);

  input_->load(in);
  output_->load(in);

  model_ = std::make_shared<Model>(input_, output_, args_, 0);
  model_->setTargetCounts(dict_->getCounts());
}

int Feature2Vec::getDimension() const {
  return args_->dim;
}

}
