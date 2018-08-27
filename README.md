# feature2vec


## Table of contents

* [Introduction](#introduction)
* [Requirements](#requirements)
* [Builde Feature2vec](#building-feature2vec)
* [Example use cases](#example-use-cases)

## Introduction

Experiment transform numerical and categorical features to higher-dimension vector.

This source code based on implementation of FastText.


## Requirements

Generally, similar to **fastText** building on modern Mac OS and Linux distributions, **feature2vec** requires a compiler with good C++11 support, including:

* (g++-4.7.2 or newer) or (clang-3.3 or newer)

Compilation is carried out using a Makefile, so you will need to have a working **make**.

For more detail, please read at [Requirements of FastText](https://github.com/facebookresearch/fastText/blob/master/README.md#requirements)

**Packages specilized for Feature2Vec:**

*  Json in C++: ```sudo apt-get install libjsoncpp-dev```

## Build Feature2vec

- Definition of features in json format which is generated by `python` code:

```
[{
    'itemid': 123, 'type': 0, 'min_value': 1, 'max_value': 99, 'multiply': 1,
    'data': [{'value': 3}, {'value': 4}], 
    'segments': [{'value': 0}, {'value': 2}]
}]
```

- Train data in plain text which is also generated by `python` code:

- Build

```
$ cd feature2vec
$ make
```

## Example use cases

### Run test case

```
$ ./fearture2vec test -dict test_data/feature_definition.json -input test_data/sample_train.csv -output aaa
```

### Train features using CBOW

```
$ ./feature2vec cbow -dict output/feature_definition.json -input data/data_train_5.csv -output models/cbow_5 -verbose 2 -thread 1 -lrUpdateRate 5 -epoch 1
```

### Train features using Skipgram

```
$ ./feature2vec skipgram -dict output/feature_definition.json -input data/data_train_5.csv -output models/skipgram_5 -verbose 2 -thread 1 -lrUpdateRate 5 -epoch 1
```

### Print feature vector
Print feature vector by itemid and its value

```
$ ./feature2vec print-feature-vector -dict output/feature_definition.json -model xxxx.bin
```

### Train model PLOS