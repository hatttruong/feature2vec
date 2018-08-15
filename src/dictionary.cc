/**
 * Copyright (c) 2016-present, Facebook, Inc.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

#include "dictionary.h"
#include <vector>
#include <string>
#include <sstream>
#include <assert.h>
#include <iostream>
#include <fstream>
#include <algorithm>
#include <iterator>
#include <cmath>
#include <stdexcept>
#include <map>
#include "json/json.h"

namespace feature2vec {

Dictionary::Dictionary(std::shared_ptr<Args> args) :
  args_(args), size_(0), nfeatures_def_(0), nfeatures_(0), ntokens_(0) {
  init();
}

void Dictionary::init() {
  // load feature definition from json
  std::ifstream in(args_->dict);
  if (!in.is_open()) {
    throw std::invalid_argument(args_->dict + " cannot be opened for load feature definition!");
  }

  Json::Reader reader;
  Json::Value obj;
  int32_t numeric_value;
  int32_t id;
  reader.parse(in, obj); // reader can also read strings
  if (args_->verbose > 0) {
    std::cerr << "Number of features:  " << obj.size() << std::endl;
  }
  for (int i = 0; i < obj.size(); i++) {
    feature_definition f;
    f.itemid = obj[i]["itemid"].asInt64();
    if (obj[i]["type"].asInt64() == 0) {
      f.type = feature_type::numeric;
    } else {
      f.type = feature_type::category;
    }

    f.min_value = obj[i]["min_value"].asInt64();
    f.max_value = obj[i]["max_value"].asInt64();
    f.multiply = obj[i]["multiply"].asInt64();

    // array of data
    const Json::Value& data = obj[i]["data"];
    for (int j = 0; j < data.size(); j++) {
      if (f.type == feature_type::numeric) {
        numeric_value = data[j]["value"].asInt64();
      } else {
        numeric_value = hash(data[j]["value"].asString());
        // std::cerr << "Hash value of '" << data[j]["value"].asString() << "' is: " << numeric_value << std::endl;
      }
      // id = data[j]["id"].asInt64();
      f.values[numeric_value] = -1;
      // if (features_.find(id) == features_.end()) {
      //   entry e;
      //   e.itemid = f.itemid;
      //   e.id = id;
      //   e.count = 0;
      //   features_[id] = e;
      // } else {
      //   std::cerr << "ERROR: itemid=" << f.itemid << ": value='" << numeric_value << "' with id=" << id << " is duplicated" << std::endl;
      //   throw std::invalid_argument("ERROR: id is duplicated");
      // }

    }

    // array of segments, it only applies for numeric features
    const Json::Value& segments = obj[i]["segments"];
    for (int j = 0; j < segments.size(); j++) {
      if (f.type == feature_type::numeric) {
        numeric_value = segments[j]["value"].asInt64();
        // id = segments[j]["id"].asInt64();
        f.segments[numeric_value] = -1;
      }
    }
    features_def_[f.itemid] = f;
    nfeatures_def_ += 1;
  }

  if (args_->verbose > 0) {
    std::cerr << "Number of feature definitions: " << nfeatures_def_ << std::endl;
  }
  in.close();
}

int32_t Dictionary::nfeatures() const {
  return nfeatures_;
}


int64_t Dictionary::ntokens() const {
  return ntokens_;
}

void Dictionary::countTokens(std::istream& ifs) {

  ntokens_ = std::count(std::istreambuf_iterator<char>(ifs),
                        std::istreambuf_iterator<char>(), '\n') - 1;
  if (args_->verbose > 0) {
    std::cerr << "Number of tokens: " << ntokens_ << std::endl;
  }
}

void Dictionary::readFromFile(std::istream& in) {

  std::string::size_type sz;   // alias of size_t
  int32_t id;
  bool is_first_row = true;
  std::streambuf& sb = *in.rdbuf();
  std::string temp_word;
  std::vector<std::string> v;
  int c;
  while ((c = sb.sbumpc()) != EOF) {

    if (c == ',' || c == '\n') {
      v.push_back(temp_word);
      temp_word.clear();

      if (c == '\n') {
        if (is_first_row == true) {
          is_first_row = false;
          v.clear();
          continue;
        }

        if (v.size() >= 3) {
          id = std::stoi(v[2], &sz);
          features_[id].count += 1;
          ntokens_ += 1;
        }
        v.clear();
      }
    } else {
      temp_word.push_back(c);
    }
  }

  // remove features with number of entries is zero
  for (auto const& x : features_)
  {
    if (x.second.count > 0) {
      std::cout << "id=" << x.first << ", itemid=" << x.second.itemid << ", count=" << x.second.count << std::endl;
      nfeatures_ += 1;
    } else {
      features_.erase(x.first);
    }
  }
  std::cerr << "Number of features: " << nfeatures_ << std::endl;
  std::cerr << "Number of tokens: " << ntokens_ << std::endl;
}

// read line by line, each line is a chartevent
// read until finish an admission (train data is sorted by hadm_id, minutes_ago)
//
int32_t Dictionary::getAdmission(std::istream & in,
                                 std::vector<int32_t>& features,
                                 std::minstd_rand & rng) const {
  std::uniform_real_distribution<> uniform(0, 1);
  std::string token;
  int32_t ntokens = 0;

  // parse itemid to check if it is numeric or category
  // parse value and look up in features_ to get its value's index

  // reset(in);
  // features.clear();
  // while (readWord(in, token)) {
  //   int32_t h = find(token);
  //   int32_t fid = features2int_[h];
  //   if (fid < 0) continue;

  //   ntokens++;
  //   features.push_back(fid);

  //   if (ntokens > MAX_EVENTS_SIZE) break;
  // }
  return 2;
}

uint32_t Dictionary::hash(const std::string & str) const {
  uint32_t h = 2166136261;
  for (size_t i = 0; i < str.size(); i++) {
    h = h ^ uint32_t(int8_t(str[i]));
    h = h * 16777619;
  }
  return h;
}

std::vector<int64_t> Dictionary::getCounts() const {
  std::vector<int64_t> counts;
  for (size_t i = 0; i < features_.size(); i++) {
    counts.push_back(features_[i].count);
  }
  return counts;
}

// int32_t Dictionary::getId(const int32_t itemid, const std::string& value) const {
//   int32_t id;
//   if (features_[itemid].type == feature_type::numeric) {
//     // multiply with *multiply, convert to int
//     features_[itemid]
//   } else {
//     uint32_t h = hash(value);
//   }
//   int32_t id = find(w, h);
//   return id;
// }

// int32_t Dictionary::getId(const int32_t itemid, const std::string& value) const {
//   int32_t id = -1;
//   if (features_[itemid].type == feature_type::category) {
//     uint32_t h = hash(value);
//     id = features_[itemid].values[h];
//   } else {

//   }
//   return id;
// }

}
