/**
 * Unit test for dictionary, feature2vec
 */

#include <time.h>

#include <vector>
#include <atomic>
#include <memory>
#include <set>
#include <chrono>
#include <iostream>
#include <queue>
#include <tuple>
#include <stdexcept>

#include "test.h"
#include "args.h"
#include "dictionary.h"
// #include "feature2vec.h"


namespace feature2vec {

UnitTest::UnitTest() {
  std::cerr << "Init class UnitTest" << std::endl;
  args_ = std::make_shared<Args>();
}

void UnitTest::prepareTest() {
  std::cerr << "prepare test cases" << std::endl;

  args_->dict = "test_data/feature_definition.json";
  args_->input = "test_data/sample_train.json";
  args_->output = "test_data/feature2vec";
}

void UnitTest::addResult(const std::string& testcase, bool passed,
                         const std::string& expected,
                         const std::string& actual) {
  test_result r;
  r.testcase = testcase.c_str();
  r.passed = passed;
  r.expected = expected.c_str();
  r.actual = actual.c_str();
  results_.push_back(r);
}

void UnitTest::printSummary() {
  std::cerr << "================================================" << std::endl;
  std::cerr << "Print summary result:" << std::endl;
  std::cerr << "Total test cases: " << results_.size() << std::endl;
  std::cerr << "================================================" << std::endl;
  int nfailed = 0;
  std::cerr << "Failed test cases: " << std::endl;
  for (size_t i = 0; i < results_.size(); i++) {
    if (results_[i].passed == false) {
      std::cerr << "\t" << results_[i].testcase;
      std::cerr << ": expected=" << results_[i].expected;
      std::cerr << ", actual=" << results_[i].actual << std::endl;
      nfailed++;
    }
  }

  std::cerr << "\nFailed: " << nfailed << std::endl;
}
void UnitTest::run() {
  std::cerr << "Start to run test cases" << std::endl;
  testInitDictionary();
  testHash();
  testFindFeature();
  testReadFromFile();
  testReadFeature();
  testGetFeature();
  testGetEvents();
  testComputeSegments();
  testGetSegments();
  testGetCounts();

  // test cases of feature2vec class
  testGetFeatureVector()  ;
  std::cerr << "Done." << std::endl;

  printSummary();
}

void UnitTest::testInitDictionary() {
  std::string testname = __FUNCTION__;
  std::cerr << "Test case: " << testname << std::endl;
  prepareTest();

  // Test load dictionary
  std::shared_ptr<Dictionary> dict = std::make_shared<Dictionary>(args_);

  // check number of definitions
  int32_t expected_ndefinition = 14;
  addResult(testname + "::number of definitions",
            dict->ndefinitions() == expected_ndefinition,
            std::to_string(expected_ndefinition),
            std::to_string(dict->ndefinitions()));

  // check if id of values and segments are unique
  std::map<int32_t, feature_definition> definitions = dict->definitions();
  std::set<int> ids;
  int32_t expected_nvalues = 1941;
  int32_t actual_nvalues = 0;
  int32_t expected_nsegments = 1214;
  int32_t actual_nsegments = 0;
  for (auto const& d : definitions) {
    // loop through value
    for (auto const&  value2id :  d.second.value2id)  {
      if (ids.count(value2id.second) > 0) {
        addResult(testname + "::duplicate id (value)", false, "not duplicate",
                  "duplicate(itemid=" + std::to_string(d.second.itemid)
                  + ", id=" + std::to_string(value2id.second)
                  + ", value=" + std::to_string(value2id.first));
      } else {
        ids.insert(value2id.second);
      }
      actual_nvalues++;
    }

    // loop through segments
    for (auto const&  segment2id :  d.second.segment2id)  {
      if (ids.count(segment2id.second) > 0) {
        addResult(testname + "::duplicate id (segments)", false, "not duplicate",
                  "duplicate(itemid=" + std::to_string(d.second.itemid)
                  + ", id=" + std::to_string(segment2id.second)
                  + ", value=" + std::to_string(segment2id.first) + ")");
      } else {
        ids.insert(segment2id.second);
      }
      actual_nsegments++;
    }
  }

  addResult(testname + "::number values",
            actual_nvalues == expected_nvalues,
            std::to_string(expected_nvalues),
            std::to_string(actual_nvalues));

  addResult(testname + "::number segments",
            actual_nsegments == expected_nsegments,
            std::to_string(expected_nsegments),
            std::to_string(actual_nsegments));
}

void UnitTest::testHash() {
  std::string testname = __FUNCTION__;
  std::cerr << "Test case: " << testname << std::endl;
  prepareTest();

  std::shared_ptr<Dictionary> dict = std::make_shared<Dictionary>(args_);

  std::string token = "Runs Vtach";
  int32_t expected_h = 111;
  int32_t actual_h = dict->hash(token);
  addResult(testname + "::hash['" + token + "']",
            actual_h == expected_h,
            std::to_string(expected_h),
            std::to_string(actual_h));

}

void UnitTest::testFindFeature() {
  std::cerr << "Test case: testFindFeature" << std::endl;
  prepareTest();

  std::shared_ptr<Dictionary> dict = std::make_shared<Dictionary>(args_);

  // find hash by item id and numeric value (in range)
  // find hash by item id and numeric value less than min value
  // find hash by item id and numeric value greater than max value
  // find hash by item id and category value
  // addResult(__FUNCTION__, false, "expected=, actual=");
}

void UnitTest::testReadFromFile() {
  std::cerr << "Test case: testReadFromFile" << std::endl;
  prepareTest();
  // addResult("testReadFromFile", false, "expected=, actual=");
}

void UnitTest::testReadFeature()  {
  std::cerr << "Test case: testReadFeature" << std::endl;
  prepareTest();
  // addResult("testReadFeature", false, "expected=, actual=");
}

void UnitTest::testGetFeature() {
  std::cerr << "Test case: testGetFeature" << std::endl;
  prepareTest();
  // addResult("testGetFeature", false, "expected=, actual=");
}

void UnitTest::testGetEvents()  {
  std::cerr << "Test case: testGetEvents" << std::endl;
  prepareTest();
  // addResult("testGetEvents", false, "expected=, actual=");
}

void UnitTest::testComputeSegments() {
  std::cerr << "Test case: testComputeSegments" << std::endl;
  prepareTest();
  // addResult("testComputeSegments", false, "expected=, actual=");
}

void UnitTest::testGetSegments() {
  std::cerr << "Test case: testGetSegments" << std::endl;
  prepareTest();
  // addResult("testGetSegments", false, "expected=, actual=");
}

void UnitTest::testGetCounts() {
  std::cerr << "Test case: testGetCounts" << std::endl;
  prepareTest();
  // addResult("testGetCounts", false, "expected=, actual=");
}

// test cases of feature2vec class
void UnitTest::testGetFeatureVector() {
  std::cerr << "Test case: testGetFeatureVector" << std::endl;
  prepareTest();
  // addResult("testGetFeatureVector", false, "expected=, actual=");
}

}