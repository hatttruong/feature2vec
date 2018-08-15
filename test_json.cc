#include <iostream>
#include <fstream>
#include <jsoncpp/json/json.h>

using namespace std;


int main() {
  // json format as :
  ifstream ifs("output/feature_definition.json");
  Json::Reader reader;
  Json::Value obj;
  reader.parse(ifs, obj); // reader can also read strings
  for (int i = 0; i < obj.size(); i++) {
    cout << "    itemid: " << obj[i]["itemid"].asUInt() << endl;
    cout << "    type: " << obj[i]["type"].asUInt() << endl;
    cout << "    min_value: " << obj[i]["min_value"].asFloat() << endl;
    cout << "    max_value: " << obj[i]["max_value"].asFloat() << endl;
    cout << "    step: " << obj[i]["step"].asFloat() << endl;

    // array of data
    // const Json::Value& data = obj[i]["data"];
    // for (int j = 0; j < data.size(); j++) {
    //   if (obj[i]["type"].asUInt() == 0) {
    //     cout << "    value: " << data[j]["value"].asFloat();
    //   } else {
    //     cout << "    value: " << data[j]["value"].asString();
    //   }
    //   cout << ", id: " << data[j]["id"].asUInt();
    //   cout << endl;
    // }

    // array of segments
    const Json::Value& segments = obj[i]["segments"];
    for (int j = 0; j < segments.size(); j++) {
      if (obj[i]["type"].asUInt() == 0) {
        cout << "    value: " << segments[j]["value"].asFloat();
      } else {
        cout << "    value: " << segments[j]["value"].asString();
      }
      cout << ", id: " << segments[j]["id"].asUInt();
      cout << endl;
    }
    cout << endl;
  }
}