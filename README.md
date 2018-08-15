# feature2vec


## Table of contents

* [Introduction](#introduction)
* [Requirements](#Requirements)
* [Build](#Build feature2vec)

## Introduction

Experiment transform numerical and categorical features to higher-dimension vector.

This source code based on implementation of FastText.


## Requirements

Generally, similar to **fastText** building on modern Mac OS and Linux distributions, **feature2vec** requires a compiler with good C++11 support, including:

* (g++-4.7.2 or newer) or (clang-3.3 or newer)

Compilation is carried out using a Makefile, so you will need to have a working **make**.

For more detail, please read at [Requirements of FastText](https://github.com/facebookresearch/fastText/blob/master/README.md#requirements)

* Other packages:
    - Json in C++: ```sudo apt-get install libjsoncpp-dev```

## Building feature2vec

- Definition of features in json format:
```
[{
    'itemid': 123, 'type': 0, 'min_value': 1, 'max_value': 99, 'step': 1,
    'data': [{'value': 3, 'id': 7}, {'value': 3, 'id': 100}], 
    'segments': [{'value': 0, 'id': 1}, {'value': 2, 'id': 2}]
}]
```
- Train data in plain text:
- Build

```
$ cd feature2vec
$ make
```

## Example use cases

```
$ ./fearture2vec test -input output/feature_definition.json -output model
```