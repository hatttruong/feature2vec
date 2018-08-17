/**
 * Unit test for dictionary, feature2vec
 */

#include <time.h>
#include <assert.h>

#include <atomic>
#include <memory>
#include <set>
#include <chrono>
#include <iostream>
#include <queue>
#include <tuple>

#include "test.h"
#include "args.h"
#include "dictionary.h"
// #include "feature2vec.h"


namespace feature2vec {

UnitTest::UnitTest() {
  std::cerr << "Init class UnitTest" << std::endl;
  args_ = std::make_shared<Args>();
}

void UnitTest::prepareTest() const{
  std::cerr << "prepare test cases" << std::endl;

  args_->dict = "output/feature_definition.json";
  args_->input = "output/sample_train.json";
  args_->output = "output/feature2vec";
}

void UnitTest::run() const{
  std::cerr << "Start to run test cases" << std::endl;
  testInitDictionary();
  std::cerr << "Done." << std::endl;
}

void UnitTest::testInitDictionary() const{
  std::cerr << "Test case: testInitDictionary" << std::endl;
  prepareTest();

  // Test load dictionary
  std::shared_ptr<Dictionary> dict = std::make_shared<Dictionary>(args_);
  std::string token = "Runs Vtach";
  int32_t id = dict->hash(token);
  assert(id == 1);
}

}