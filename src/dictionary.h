/**
 * Copyright (c) 2016-present, Facebook, Inc.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

#pragma once

#include <vector>
#include <string>
#include <istream>
#include <ostream>
#include <random>
#include <memory>
#include <unordered_map>
#include <map>

#include "args.h"
// #include "real.h"

namespace feature2vec {

typedef int32_t id_type;
enum class feature_type : int8_t {numeric = 0, category = 1};

struct feature_definition {
  int32_t itemid;
  feature_type type;
  int32_t min_value;
  int32_t max_value;
  int32_t multiply;
  // key: value (int) if feature is numeric, hash(value) if feature is category
  // value: unique id
  std::map<int32_t, int32_t> value2id;
  std::map<int32_t, int32_t> id2value; // conversed of values
  std::map<int32_t, int32_t> segment2id;
};

struct entry {
  int32_t id; // hash of (itemid, value)
  int32_t itemid;
  std::string value; // actual value in string
  int64_t count;
  std::vector<int32_t> segments;  // index of segment in input_
};

struct event_entry {
  int32_t minutes_ago;
  int32_t idx;  // index of feature value in input_
};

class Dictionary {
protected:
  static const int32_t MAX_FEATURE_SIZE = 30000000;
  static const int32_t MAX_EVENTS_SIZE = 1000000;

  std::shared_ptr<Args> args_;
  std::map<int32_t, feature_definition> definition_;  // key: itemid
  // index: hash of (itemid, value), value: index of features_
  std::vector<int32_t> feature2int_;
  std::vector<entry> features_;

  int32_t size_;
  int32_t ndefinition_;
  int32_t nfeatures_;
  int64_t nevents_;

  int32_t find(const int32_t, const std::string&) const;
  void initDefinition();
  void initSegments();

public:
  explicit Dictionary(std::shared_ptr<Args>);
  explicit Dictionary(std::shared_ptr<Args>, std::istream&);
  int32_t nfeatures() const;
  int64_t nevents() const;
  void countEvents(std::istream&);
  void readFromFile(std::istream&);
  bool readFeature(std::istream&, std::vector<std::string>&) const;
  entry getFeature(int32_t) const;
  void add(const int32_t, const std::string&);
  int32_t getEvents(
    std::istream&,
    std::vector<event_entry>&,
    std::minstd_rand&) const;
  void computeSegments(
    const int32_t,
    const int32_t,
    std::vector<int32_t>&) const;
  const std::vector<int32_t>& getSegments(int32_t) const;
  uint32_t hash(const std::string& str) const;
  std::vector<int64_t> getCounts() const;
  void save(std::ostream&) const;
};

}
