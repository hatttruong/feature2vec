/**
 * Unit test for dictionary, feature2vec
 */
#pragma once

#include <time.h>

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

class UnitTest {

protected:
  std::shared_ptr<Args> args_;

  void prepareTest() const;
  void testInitDictionary() const;

public:
  UnitTest();
  void run() const;
};

}
