# Some resource to learn C++

## 1.[Learn how to read/write json in C++](https://en.wikibooks.org/wiki/JsonCpp)

* Here is an example of reading Json file: [test_json.cc]()

* Install required package and build source code:

```
$ echo 'Install...'
$ sudo apt-get install libjsoncpp-dev

$ g++ -o test test_json.cc -ljsoncpp
$ echo 'Run...'
$ ./test
```

## 2. [Dictionary type](https://www.moderncplusplus.com/map/)

```
// a map where the keys are integers and the values are strings
std::map<int, std::string> userNameForUserID;
 
// insert a user
userNameForUserID[0] = std::string("John Doe");
 
// retrieve a user
std::cout << "User #0 is named: " << userNameForUserID.at(0) << std::endl;

// How to find if a given key exists in a C++ std::map
if ( userNameForUserID.count(10)) {
  // not found
} else {
  // found
}

// Iteration
for(auto& x : values)
{
    std::cout << x.first << "," << x.second << std::endl;
}
```

## 3. Class and functions:

* TODO