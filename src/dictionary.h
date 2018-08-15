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
  // value: unique id, greater than or equal zero (-1 at initilization)
  std::map<int32_t, int32_t> values;
  std::map<int32_t, int32_t> segments;
};

struct entry {
  int32_t id;
  int32_t itemid;
  int32_t value; // actual value if numeric, hash(value) if category
  int64_t count;
  std::vector<int32_t> segments;
};

class Dictionary {
protected:
  static const int32_t MAX_FEATURE_SIZE = 30000000;
  static const int32_t MAX_EVENTS_SIZE = 1000000;

  std::shared_ptr<Args> args_;
  std::map<int32_t, feature_definition> features_def_;  // key: itemid
  std::map<int32_t, entry> features_; // key: id

  int32_t size_;
  int32_t nfeatures_def_;
  int32_t nfeatures_;
  int64_t ntokens_;

  void init();

public:
  explicit Dictionary(std::shared_ptr<Args>);
  explicit Dictionary(std::shared_ptr<Args>, std::istream&);
  int32_t nfeatures() const;
  int64_t ntokens() const;
  void countTokens(std::istream&);
  // int32_t getId(const int32_t, const std::string&) const;


  void readFromFile(std::istream&);
  int32_t getAdmission(std::istream&, std::vector<int32_t>&,
                       std::minstd_rand&) const;
  // hash category feature to int
  uint32_t hash(const std::string& str) const;
  std::vector<int64_t> getCounts() const;
};

}
