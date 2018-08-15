## Some resource to learn C++

1. [Learn how to read/write json in C++](https://en.wikibooks.org/wiki/JsonCpp)

```
g++ -o test test_json.cc -ljsoncpp
```

2. [Dictionary] (https://www.moderncplusplus.com/map/)

```
// a map where the keys are integers and the values are strings
std::map<int, std::string> userNameForUserID;
 
// insert a user
userNameForUserID[0] = std::string("John Doe");
 
// retrieve a user
std::cout << "User #0 is named: " << userNameForUserID[0] << std::endl;

// How to find if a given key exists in a C++ std::map
if ( userNameForUserID.find(10) == m.end() ) {
  // not found
} else {
  // found
}

for(auto& x : values)
{
    std::cout << x.first << "," << x.second << std::endl;
}
```

3. 