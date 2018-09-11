/**
 * This source code, based on FastText source code, is modified to fit my
 * application
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
#include "utils.h"

namespace feature2vec {

typedef int32_t id_type;
enum class feature_type : int8_t {numeric = 0, category = 1};

struct feature_definition {
  int32_t conceptid;
  feature_type type;
  int32_t min_value;
  int32_t max_value;
  int32_t multiply;
  // key: value (int) if feature is numeric, hash(value) if feature is category
  // value: unique id
  std::map<int32_t, int32_t> value2id;
  std::map<int32_t, int32_t> id2value; // conversed of values
  std::map<int32_t, int32_t> segment2id;
  std::map<std::string, int32_t> hashmaps;
};

struct entry {
  int32_t id; // hash of (conceptid, value)
  int32_t conceptid;
  int32_t value; // actual value if numeric, hash(value) if category
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
  // max number of events per admission
  static const int32_t MAX_EVENTS_SIZE = 1000000;

  std::shared_ptr<Args> args_;

  // key: conceptid, value: definition object which contains mapping between
  // each value to unique id and each segments to unique id
  std::map<int32_t, feature_definition> definitions_;

  // index: unique id of (conceptid, value), value: index of features_
  std::vector<int32_t> feature2int_;

  // index: value of feature2int_, value: entry object
  // entry.id = unique id of (conceptid, value)
  std::vector<entry> features_;

  // position of each admission in training file
  std::vector<int64_t> admissionPositions_;

  int32_t size_;
  int32_t ndefinitions_;
  int32_t nfeatures_;
  int64_t nevents_;

  int32_t find(const int32_t, const std::string&) const;
  int32_t find(const int32_t, const int32_t) const;
  void initDefinition();
  void initSegments();
  void reset(std::istream&) const;

public:
  explicit Dictionary(std::shared_ptr<Args>);
  explicit Dictionary(std::shared_ptr<Args>, std::istream&);
  int32_t nfeatures() const;
  int64_t nevents() const;

  // these functions are for testing
  int32_t ndefinitions() const;
  std::map<int32_t, feature_definition> definitions() const;  // key: conceptid

  // void countEvents(std::istream&);
  void readFromFile(std::istream&);
  bool readFeature(std::istream&, std::vector<std::string>&) const;
  entry getFeature(int32_t) const;
  void add(const int32_t, const int32_t);
  int32_t getEvents(
    std::istream&,
    std::vector<event_entry>&,
    std::minstd_rand&) const;
  void computeSegments(
    const int32_t,
    const int32_t,
    std::vector<int32_t>&) const;
  const std::vector<int32_t>& getSegments(int32_t) const;
  const std::vector<int32_t>& getSegments(int32_t, const std::string&) const;
  uint32_t hash(const std::string& str) const;
  std::vector<int64_t> getCounts() const;
  void save(std::ostream&) const;
  void load(std::istream&);
  int64_t getAdmissionPosition(int32_t, int32_t) const;

};

}
