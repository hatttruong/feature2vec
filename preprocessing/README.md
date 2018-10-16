# README - Predict Length of Stay - Preprocessing #

This README would document whatever steps are necessary to get your application up and running.

# 1. Setup

## Setup to connect Postgres in Python

- environment: Python 3.5
- install JAVA (requirement of `boilerpipe3`)
- install requirements (including psycopg2, sshtunnel):
    ```
    $ sudo apt-get update
    $ sudo apt-get install libssh-dev
    $ sudo apt-get install python3-psycopg2
    $ sudo pip3 install -r requirements.txt
    ```

## Run

```
sudo python3 connect_db.py
```

## Test

```
$ cd preprocessing/src/test/
$ sudo python3 test_suite.py
```

# 2. Main functions

## 2.1 Prepare data for merge tool

* **Step 1**: clone items information from `d_items` table to `jvn_items` table which has structure as follow:

```
itemid
label
abbr
dbsource
linksto
isnumeric
min
max
percentile25th
percentile50th
percentile75th
distributionImg
```

- With **numeric** item, calculate min, max, (25-50-75) percentile, export distributions image
- With **category** item: copy fields `itemid, label, abbr, dbsource, linksto`

```
$ cd preprocessing
$ python3 main.py prepare_numeric_item
```

- Backup data of `jvn_items` to file:

```
TODO
```

* **Step 2**: Crawl google search result for each items (save to files and store at `data/webpages`)

```
# crawl data
python3 main.py crawl_webpages

# preprocess before clustering
python3 main.py tfidf_medical_webpages
```

* **Step 3**: Cluster medical terms by similarity of label, distribution values (numeric) or similarity values (category)

TODO: read [KL Divergence](https://bigdatascientistblog.wordpress.com/2017/09/11/a-simple-introduction-to-kullback-leibler-divergence-through-python-code/)

```
$ cd preprocessing
$ python3 main.py cluster
```

* **Step 4**: Because `merge_tool` load data from `public` path of `mimic` database, run `merge_tool/migrate_data.sql` to copy data from `mimiciii` path to `public` path. Then run `merge_tool` website to start merging items. (Please read `merge_tool/README.md` to know to how to start). While merging, run the following commands to back up data to csv (just in case unintended delete actions):

```
$ cd preprocessing
$ vi setting.ini
# SearchPath = public
# :wq

$ python3 main.py backup
$ python3 main.py restore
```

## 2.2 Prepare data to train feature

There are two files we need to prepare for training **feature2vec**: `concept_definition.json` and `data_train.csv`.

In order to improve performance, add index on `chartevents` tables:

```
$ psql 'dbname=mimic user=mimicuser options=--search_path=mimiciii' -f /Users/hatruong/hagit/feature2vec/mics/add_index.sql
```

### 2.2.1 Generate `concept_definition.json`

Here is command to generate:
```
$ (on local machine: 8G Ram)
$ cd preprocessing
$ python3 main.py define_concepts -cd ../data -p 16

# Total concepts: 6
# TOTAL DURATION (static features): 0.620664 seconds
# TOTAL DURATION (load raw non-static concepts): 218.988309 seconds ~ 3.5mins
# Number of concept arguments: 6
# DONE 6376/6376 concepts
# TOTAL DURATION (create non-static concepts): 1695.681615 seconds
# seconds/concept: 0.26594755567754075 seconds
# mean query times: 4.027205550345045
# Total numeric features: 2,669
# Total categorical features: 3,713
# Total values of both numeric, categorical: 122,202
# Total segments of numeric features: 509,470
# Total values & segments: 631,672
```

* `concept_definition.json` structure:

```
{
    'definition': [{
        'conceptid': 123,
        'type': 0,
        'min_value': 1,
        'max_value': 99,
        'multiply': 1,
        'data': [
            {'value': 3, 'id': 0},
            {'value': 4, 'id': 1}
        ],
        'segments': [
            {'value': 0, 'id': 2},
            {'value': 2, 'id': 3}
        ],
        'hashmaps': [
            {"value": "MARRIED", "hash": 1039924087},
            {"value": "SEPARATED", "hash": 1106694804}
        ]
    }],
    'item2concept': [{'itemid': 1, 'conceptid': 2}, {'itemid': 11, 'conceptid': 3}]
}
```

* It takes **28 mins** in average for exporting all concept definitions.
* In case we don't merge duplicate items:
    - There are **5** static items in **v_first_admissions** along with **los_icu_h**
    - There are **6376** non-static items in **chartevents**
    - It takes **3.5** mins to extract items from **chartevents** table
    - We don't extract based on **linksto** field of **d_items** because it is INCORRECT
    - Total numeric features: **2,669**
    - Total categorical features: **3,713**
    - Total values of numeric & categorical features: **122,202**
* In case we merge duplicate items, **TODO**
    - There are **xxx** concepts in **chartevents**
    - It takes **xx** mins to extract items from **chartevents** table
    - We don't extract based on **linksto** field of **d_items** because it is INCORRECT
    - Total features: **xxx**

### 2.2.2 Update `chartevents` table:

* Update value of chartevents based on `concept_definition.json`: after exporting `concept_definition.json`, value of `chartevents` table will be updated (the new values are stored in `jvn_value` column).
* It takes about **xx hrs** to done.

```
$ cd preprocessing
$ python3 main.py update_chartevents -cd ../data

# START update value of chartevents based on "concept_definition.json"
# Total concepts (load from json): 6382
# Done: 50/6380 concepts, avg duration: 1.01 seconds/concept
# Done: 100/6380 concepts, avg duration: 2.75 seconds/concept
...
# DURATION (update values): 50889 seconds ~ 14hrs
```

### 2.2.3 Generate `data_train_chartevents_*.csv`:

Here is command to generate:
```
$ cd preprocessing
$ python3 main.py create_train_dataset -cd ../data -p 12 -ed ../data/temp
```

* `data_train_chartevents_*.csv` structure: sorted by hadm_id, minutes_ago and **without** header

```
hadm_id, minutes_ago, conceptid, value
...
...
```

* It takes **2-5** seconds in average for exporting data of 50 admissions and about **30** minutes to export all data.

```
2018-09-12 11:01:52,814 : INFO : DONE 34134/34134 admissions
2018-09-12 11:01:52,820 : INFO : TOTAL DURATION: 1853.657842 seconds
2018-09-12 11:01:52,829 : INFO : seconds/admissions: 0.05446488341070694 seconds
2018-09-12 11:01:56,680 : INFO : mean query times: 0.5911701626314861
2018-09-12 11:01:56,682 : INFO : mean update times: 0.0035191389786683905
2018-09-12 11:01:56,736 : INFO : run "concat_train_data.sh" to concat all files
```

* run `concat_train_data.sh`:

```
Total Entries: 177,804,820
```

## 2.3 Prepare data to predict LOS using LSTM:

