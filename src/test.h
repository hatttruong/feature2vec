/**
 * Unit test for dictionary, feature2vec
 */
#pragma once

#include <time.h>

#include <vector>
#include <atomic>
#include <memory>
#include <set>
#include <chrono>
#include <iostream>
#include <queue>
#include <tuple>

#include "args.h"
// #include "dictionary.h"
// #include "feature2vec.h"


namespace feature2vec {

struct test_result {
  std::string testcase;
  bool passed;
  std::string expected;
  std::string actual;
};


class UnitTest {

protected:
  std::shared_ptr<Args> args_;
  std::vector<test_result> results_;

  void prepareTest();
  void addResult(const std::string&, bool, const std::string&,
    const std::string&);
  void printSummary();

  // test cases of dictionary class
  void testInitDictionary();
  void testHash();
  void testFindFeature();
  void testReadFromFile();
  void testReadFeature();
  void testGetFeature();
  void testGetEvents();
  void testComputeSegments();
  void testGetSegments();
  void testGetCounts();
  void testTrainModel();

  // test cases of feature2vec class
  void testGetFeatureVector();

public:
  UnitTest();
  void run();
};

}
