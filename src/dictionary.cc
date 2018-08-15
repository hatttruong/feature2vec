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
  args_(args), feature2int_(MAX_FEATURE_SIZE, -1), size_(0), ndefinition_(0),
  nfeatures_(0), nevents_(0) {
  initDefinition();
}

void Dictionary::initDefinition() {
  // load feature definition from json
  std::ifstream in(args_->dict);
  if (!in.is_open()) {
    throw std::invalid_argument(args_->dict + " cannot be opened for load feature definition!");
  }
  // std::map<int32_t, std::string> hashTable; // TOBEREMOVE
  Json::Reader reader;
  Json::Value obj;
  reader.parse(in, obj); // reader can also read strings
  if (args_->verbose > 0) {
    std::cerr << "Number of features definitions in file:  " << obj.size() << std::endl;
  }

  int32_t n_values = 0; // count number of feature values
  int32_t n_segments = 0; // count number of segment values
  int32_t numeric_value; // contain value of features/segments
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
        // TOBEREMOVE
        // hashTable[numeric_value] = data[j]["value"].asString();
      }
      f.value2id[numeric_value] = n_values + n_segments;
      f.id2value[f.value2id[numeric_value]] = numeric_value;
      n_values++;
    }

    // array of segments, it only applies for numeric features
    const Json::Value& segments = obj[i]["segments"];
    for (int j = 0; j < segments.size(); j++) {
      if (f.type == feature_type::numeric) {
        numeric_value = segments[j]["value"].asInt64();
        f.segment2id[numeric_value] = n_values + n_segments;
        n_segments++;
      }
    }
    definition_[f.itemid] = f;
    ndefinition_ += 1;
  }

  if (n_segments > args_->bucket) {
    throw std::invalid_argument(
      args_->bucket + " is not enough.Total segments are " + n_segments);
  }
  if (args_->verbose > 0) {
    std::cerr << "Number of parsed feature definitions: " << ndefinition_ << std::endl;
    std::cerr << "Number of feature values: " << n_values << std::endl;
    std::cerr << "Number of feature segments: " << n_segments << std::endl;
  }
  in.close();

  // TOBEREMOVE: export hashTable to file
  // std::ofstream ofs;
  // ofs.open ("hash_test.txt");
  // for (auto const& x : hashTable)
  // {
  //   ofs << x.second << ","  << x.first <<"\n";
  //   ofs.write((char*)&x.first, sizeof(uint32_t));
  // }
  // ofs.close();
}

int32_t Dictionary::nfeatures() const {
  return nfeatures_;
}


int64_t Dictionary::nevents() const {
  return nevents_;
}

void Dictionary::countEvents(std::istream& ifs) {

  nevents_ = std::count(std::istreambuf_iterator<char>(ifs),
                        std::istreambuf_iterator<char>(), '\n') - 1;
  if (args_->verbose > 0) {
    std::cerr << "Number of events: " << nevents_ << std::endl;
  }
}

bool Dictionary::readFeature(std::istream& in, std::vector<std::string>& v) const {
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

void Dictionary::readFromFile(std::istream& in) {

  std::string::size_type sz;   // alias of size_t
  int32_t itemid;
  std::vector<std::string> v;
  while (readFeature(in, v)) {
    // hadm_id,minutes_ago,itemid,value
    if (v.size() >= 4) {
      // std::cerr << "Data: hadm_id=" << v[0] << ", minutes_ago=" << v[1];
      // std::cerr << ", itemid=" << v[2] << ", value=" << v[3] << std::endl;
      itemid = std::stoi(v[2], &sz);
      add(itemid, v[3]);
    }
  }

  initSegments();

  nfeatures_ = features_.size();

  if (args_->verbose > 0) {
    std::cerr << "Number of features: " << nfeatures_ << std::endl;
    std::cerr << "Number of events: " << nevents_ << std::endl;
  }

  if (size_ == 0) {
    throw std::invalid_argument(
      "Empty vocabulary. Try a smaller -minCount value.");
  }
}

void Dictionary::add(const int32_t itemid, const std::string& value) {
  int32_t h = find(itemid, value);
  nevents_++;
  if (feature2int_[h] == -1) {
    entry e;
    e.id = h;
    e.itemid = itemid;
    e.value = value.c_str();
    e.count = 1;
    features_.push_back(e);
    feature2int_[h] = size_++;
  } else {
    features_[feature2int_[h]].count++;
  }
}


int32_t Dictionary::find(const int32_t itemid, const std::string& value) const {
  int32_t id = -1;

  struct feature_definition f = definition_.at(itemid);
  if (f.type == feature_type::numeric) {
    // convert value to int
    std::string::size_type sz;   // alias of size_t
    int32_t int_value = std::stoi(value, &sz);
    if (int_value < f.min_value) {
      id = f.value2id[f.min_value - 1];
    } else if (int_value > f.max_value) {
      id = f.value2id[f.max_value + 1];
    } else {
      id = f.value2id[int_value];
    }
  } else {
    // hash value and look up id
    id = f.value2id[hash(value)];
  }
  return id;
}

// hash category feature to int
uint32_t Dictionary::hash(const std::string & str) const {
  uint32_t h = 2166136261;
  for (size_t i = 0; i < str.size(); i++) {
    //TOBEREMOVE
    // std::cerr << str[i] << "=" << uint32_t(int8_t(str[i])) << std::endl;
    h = h ^ uint32_t(int8_t(str[i]));
    //TOBEREMOVE
    // std::cerr << "h^ = " << h << std::endl;
    h = h * 16777619;
    //TOBEREMOVE
    // std::cerr << "h * = " << h << std::endl;
    // std::cerr << std::endl;
  }
  return h;
}

// initSegments applied for numeric features only
// input_ has size of nfeatures_ + args_-> bucket
// index of segment in input_ vector is specified by this formular:
// nfeatures_ + definitions_[itemid].segments[xx] % args_-> bucket
void Dictionary::initSegments() {
  int32_t itemid;
  int32_t value;
  for (size_t i = 0; i < size_; i++) {
    features_[i].segments.clear();
    // add itself
    features_[i].segments.push_back(i);

    // compute its segments
    itemid = features_[i].itemid;
    if (definition_[itemid].type == feature_type::numeric) {
      value = definition_[itemid].id2value[features_[i].id];
      computeSegments(itemid, value, features_[i].segments);
    }
  }
}

void Dictionary::computeSegments(const int32_t itemid, const int32_t value,
                                 std::vector<int32_t>& nsegments) const {
  int32_t h;
  int32_t seg_idx;

  // -1 in order to add value below min_value
  int32_t min_value = definition_.at(itemid).min_value - 1;
  // + 1 in order to add value greater than max_value
  int32_t max_value = definition_.at(itemid).max_value + 1;

  for (size_t i = min_value; i <= max_value; i++) {
    if (i > value) {
      break;
    }
    seg_idx = definition_.at(itemid).segment2id.at(i);
    h = seg_idx % args_->bucket;
    nsegments.push_back(h);
  }
}

std::vector<int64_t> Dictionary::getCounts() const {
  std::vector<int64_t> counts;
  for (size_t i = 0; i < features_.size(); i++) {
    counts.push_back(features_[i].count);
  }
  return counts;
}

// read line by line, each line is a chartevent
// read until finish an admission (train data is sorted by hadm_id, minutes_ago)
// return: number of events
int32_t Dictionary::getEvents(std::istream & in,
                              std::vector<event_entry>& events,
                              std::minstd_rand & rng) const {
  std::uniform_real_distribution<> uniform(0, 1);
  std::string::size_type sz;   // alias of size_t
  int32_t nevents = 0;

  int32_t cur_hadm_id = -1;
  int32_t new_hadm_id;
  std::vector<std::string> v;
  int32_t itemid;
  int32_t h;
  int32_t minutes_ago;
  int32_t pos = 0;
  events.clear();
  while (readFeature(in, v)) {
    // hadm_id,minutes_ago,itemid,value
    if (v.size() >= 4) {
      new_hadm_id = std::stoi(v[0], &sz);

      // for the first event of admission
      if (cur_hadm_id == -1) {
        cur_hadm_id = new_hadm_id;
      }

      if (cur_hadm_id != new_hadm_id) {
        // move cursor to begining of line
        in.seekg(pos);
        break;
      }
      // record the position
      pos = in.tellg();

      itemid = std::stoi(v[2], &sz);
      h = find(itemid, v[3]);
      if (h < 0) continue;

      // TOBEREMOVE
      // std::cerr << "Data: hadm_id=" << v[0] << ", minutes_ago=" << v[1];
      // std::cerr << ", itemid=" << v[2] << ", value=" << v[3];
      // std::cerr << ", fid=" << fid << std::endl;
      nevents++;
      minutes_ago = std::stoi(v[1], &sz);

      // create event_entry object
      event_entry ee;
      ee.minutes_ago = minutes_ago;
      ee.idx = feature2int_[h];
      events.push_back(ee);

      if (nevents > MAX_EVENTS_SIZE) break;
    }
  }
  return nevents;
}

// get segments by index of feature value
const std::vector<int32_t>& Dictionary::getSegments(int32_t i) const {
  assert(i >= 0);
  assert(i < nfeatures_);
  return features_[i].segments;
}

entry Dictionary::getFeature(int32_t id) const {
  assert(id >= 0);
  assert(id < size_);
  return features_[id];
}

void Dictionary::save(std::ostream& out) const {
  out.write((char*) &size_, sizeof(int32_t));
  out.write((char*) &nfeatures_, sizeof(int32_t));
  out.write((char*) &nevents_, sizeof(int64_t));

  for (int32_t i = 0; i < size_; i++) {
    entry e = features_[i];
    out.write((char*) & (e.id), sizeof(int32_t));
    out.write((char*) & (e.itemid), sizeof(int32_t));
    out.write(e.value.data(), e.value.size() * sizeof(char));
    out.put(0);
    out.write((char*) & (e.count), sizeof(int64_t));
  }
}

}