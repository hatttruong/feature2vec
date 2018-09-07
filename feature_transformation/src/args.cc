/**
 * Copyright (c) 2016-present, Facebook, Inc.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

#include "args.h"

#include <stdlib.h>

#include <iostream>
#include <stdexcept>

namespace feature2vec {

Args::Args() {
  lr = 0.05;
  dim = 100;
  ws = 60;            // context size of non-static event in minutes
  multiEvents =  30;  // average number of events happening at the same time
  maxStatic = 4;      // max number of static events
  ps = 0.5;           // context size of static event in faction of 1
  epoch = 5;
  minCount = 5;
  neg = 5;
  loss = loss_name::ns;
  model = model_name::sg;
  bucket = 2000000;
  thread = 12;
  lrUpdateRate = 100;
  t = 1e-4;
  verbose = 2;
  pretrainedVectors = "";
  saveOutput = false;

}

std::string Args::lossToString(loss_name ln) const {
  switch (ln) {
  case loss_name::hs:
    return "hs";
  case loss_name::ns:
    return "ns";
  case loss_name::softmax:
    return "softmax";
  }
  return "Unknown loss!"; // should never happen
}

std::string Args::boolToString(bool b) const {
  if (b) {
    return "true";
  } else {
    return "false";
  }
}

std::string Args::modelToString(model_name mn) const {
  switch (mn) {
  case model_name::cbow:
    return "cbow";
  case model_name::sg:
    return "sg";
  }
  return "Unknown model name!"; // should never happen
}

void Args::parseArgs(const std::vector<std::string>& args) {
  std::string command(args[1]);
  if (command == "cbow") {
    model = model_name::cbow;
  }

  for (int ai = 2; ai < args.size(); ai += 2) {
    if (args[ai][0] != '-') {
      std::cerr << "Provided argument without a dash! Usage:" << std::endl;
      printHelp();
      exit(EXIT_FAILURE);
    }
    try {
      if (args[ai] == "-h") {
        std::cerr << "Here is the help! Usage:" << std::endl;
        printHelp();
        exit(EXIT_FAILURE);
      } else if (args[ai] == "-dict") {
        dict = std::string(args.at(ai + 1));
      } else if (args[ai] == "-input") {
        input = std::string(args.at(ai + 1));
      } else if (args[ai] == "-output") {
        output = std::string(args.at(ai + 1));
      } else if (args[ai] == "-lr") {
        lr = std::stof(args.at(ai + 1));
      } else if (args[ai] == "-lrUpdateRate") {
        lrUpdateRate = std::stoi(args.at(ai + 1));
      } else if (args[ai] == "-dim") {
        dim = std::stoi(args.at(ai + 1));
      } else if (args[ai] == "-ws") {
        ws = std::stoi(args.at(ai + 1));
      } else if (args[ai] == "-multiEvents") {
        multiEvents = std::stoi(args.at(ai + 1));
      } else if (args[ai] == "-maxStatic") {
        maxStatic = std::stoi(args.at(ai + 1));
      } else if (args[ai] == "-ps") {
        ps = std::stof(args.at(ai + 1));
      } else if (args[ai] == "-epoch") {
        epoch = std::stoi(args.at(ai + 1));
      } else if (args[ai] == "-minCount") {
        minCount = std::stoi(args.at(ai + 1));
      } else if (args[ai] == "-neg") {
        neg = std::stoi(args.at(ai + 1));
      } else if (args[ai] == "-loss") {
        if (args.at(ai + 1) == "hs") {
          loss = loss_name::hs;
        } else if (args.at(ai + 1) == "ns") {
          loss = loss_name::ns;
        } else if (args.at(ai + 1) == "softmax") {
          loss = loss_name::softmax;
        } else {
          std::cerr << "Unknown loss: " << args.at(ai + 1) << std::endl;
          printHelp();
          exit(EXIT_FAILURE);
        }
      } else if (args[ai] == "-bucket") {
        bucket = std::stoi(args.at(ai + 1));
      } else if (args[ai] == "-thread") {
        thread = std::stoi(args.at(ai + 1));
      } else if (args[ai] == "-t") {
        t = std::stof(args.at(ai + 1));
      } else if (args[ai] == "-verbose") {
        verbose = std::stoi(args.at(ai + 1));
      } else if (args[ai] == "-pretrainedVectors") {
        pretrainedVectors = std::string(args.at(ai + 1));
      } else if (args[ai] == "-saveOutput") {
        saveOutput = true;
        ai--;
      } else {
        std::cerr << "Unknown argument: " << args[ai] << std::endl;
        printHelp();
        exit(EXIT_FAILURE);
      }
    } catch (std::out_of_range) {
      std::cerr << args[ai] << " is missing an argument" << std::endl;
      printHelp();
      exit(EXIT_FAILURE);
    }
  }
  if (dict.empty() || input.empty() || output.empty()) {
    std::cerr << "Empty dict or input or output path." << std::endl;
    printHelp();
    exit(EXIT_FAILURE);
  }

}

void Args::printHelp() {
  printBasicHelp();
  printDictionaryHelp();
  printTrainingHelp();
}


void Args::printBasicHelp() {
  std::cerr
      << "\nThe following arguments are mandatory:\n"
      << "  -dict               dictionary file path\n"
      << "  -input              training file path\n"
      << "  -output             output file path\n"
      << "\nThe following arguments are optional:\n"
      << "  -verbose            verbosity level [" << verbose << "]\n";
}

void Args::printDictionaryHelp() {
  std::cerr
      << "\nThe following arguments for the dictionary are optional:\n"
      << "  -minCount           minimal number of feature occurences [" << minCount << "]\n"
      << "  -bucket             number of buckets [" << bucket << "]\n"
      << "  -t                  sampling threshold [" << t << "]\n";
}

void Args::printTrainingHelp() {
  std::cerr
      << "\nThe following arguments for training are optional:\n"
      << "  -lr                 learning rate [" << lr << "]\n"
      << "  -lrUpdateRate       change the rate of updates for the learning rate [" << lrUpdateRate << "]\n"
      << "  -dim                size of feature vectors [" << dim << "]\n"
      << "  -ws                 context size of non-static event in minutes [" << ws << "]\n"
      << "  -multiEvents        average number of events happening at the same time [" << multiEvents << "]\n"
      << "  -maxStatic          max number of static events [" << maxStatic << "]\n"
      << "  -ps                 context size of static event in in faction of 1 [" << ps << "]\n"
      << "  -epoch              number of epochs [" << epoch << "]\n"
      << "  -neg                number of negatives sampled [" << neg << "]\n"
      << "  -loss               loss function {ns, hs, softmax} [" << lossToString(loss) << "]\n"
      << "  -thread             number of threads [" << thread << "]\n"
      << "  -pretrainedVectors  pretrained feature vectors for supervised learning [" << pretrainedVectors << "]\n"
      << "  -saveOutput         whether output params should be saved [" << boolToString(saveOutput) << "]\n";
}


void Args::save(std::ostream& out) {
  out.write((char*) & (dim), sizeof(int));
  out.write((char*) & (ws), sizeof(int));
  out.write((char*) & (multiEvents), sizeof(int));
  out.write((char*) & (maxStatic), sizeof(int));
  out.write((char*) & (ps), sizeof(double));
  out.write((char*) & (epoch), sizeof(int));
  out.write((char*) & (minCount), sizeof(int));
  out.write((char*) & (neg), sizeof(int));
  out.write((char*) & (loss), sizeof(loss_name));
  out.write((char*) & (model), sizeof(model_name));
  out.write((char*) & (bucket), sizeof(int));
  out.write((char*) & (lrUpdateRate), sizeof(int));
  out.write((char*) & (t), sizeof(double));

  // save dictionary path
  out.write(dict.data(), dict.size() * sizeof(char));
  out.put(0);
}

void Args::load(std::istream& in) {
  in.read((char*) & (dim), sizeof(int));
  in.read((char*) & (ws), sizeof(int));
  in.read((char*) & (multiEvents), sizeof(int));
  in.read((char*) & (maxStatic), sizeof(int));
  in.read((char*) & (ps), sizeof(double));
  in.read((char*) & (epoch), sizeof(int));
  in.read((char*) & (minCount), sizeof(int));
  in.read((char*) & (neg), sizeof(int));
  in.read((char*) & (loss), sizeof(loss_name));
  in.read((char*) & (model), sizeof(model_name));
  in.read((char*) & (bucket), sizeof(int));
  in.read((char*) & (lrUpdateRate), sizeof(int));
  in.read((char*) & (t), sizeof(double));

  // load dictionary path
  char c;
  while ((c = in.get()) != 0) {
    dict.push_back(c);
  }

}

void Args::dump(std::ostream& out) const {
  out << "dim" << " " << dim << std::endl;
  out << "ws" << " " << ws << std::endl;
  out << "multiEvents" << " " << multiEvents << std::endl;
  out << "maxStatic" << " " << maxStatic << std::endl;
  out << "ps" << " " << ws << std::endl;
  out << "epoch" << " " << epoch << std::endl;
  out << "minCount" << " " << minCount << std::endl;
  out << "neg" << " " << neg << std::endl;
  out << "loss" << " " << lossToString(loss) << std::endl;
  out << "model" << " " << modelToString(model) << std::endl;
  out << "bucket" << " " << bucket << std::endl;
  out << "lrUpdateRate" << " " << lrUpdateRate << std::endl;
  out << "t" << " " << t << std::endl;
}

}
