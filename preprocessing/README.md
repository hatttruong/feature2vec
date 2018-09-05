# README - Predict Length of Stay - Preprocessing #

This README would normally document whatever steps are necessary to get your application up and running.

# 1. Setup

## Setup to connect Postgres in Python

- environment: Python 3.5
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

## Prepare data for merge tool

!TODO
Crawl google search result for each items (save to `SearchTermResults` table)
Cluster documents and create candidate groups based on `SearchTermResults`, insert into `GroupItems`

```
id
name
createdBy: 'SYS'
```

For each item, calculate min, max, percentile, export distributions image

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
values
distributionImg
candidateGroupId
groupId
```

## Prepare data to train feature

There are two files we need to prepare for training **feature2vec**: `concept_definition.json` and `data_train.csv`.

In order to improve performance, add index on `chartevents` tables:

```
$ psql 'dbname=mimic user=mimicuser options=--search_path=mimiciii' -f /Users/hatruong/hagit/feature2vec/mics/add_index.sql
```

### Generate `concept_definition.json`

Here is command to generate:
```
$ cd python
$ python3 main.py define_concepts -o ../output -p 8
# Total concepts: 6463
# TOTAL DURATION: 1918 seconds ~ 31mins
# total features: 948392 (not merged)
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
        'data': [{'value': 3}, {'value': 4}],
        'segments': [{'value': 0}, {'value': 2}],
    }],
    'item2concept': [{'itemid': 1, 'conceptid': 2}, {'itemid': 11, 'conceptid': 3}]
}
```

* It takes 30-40 mins in average for exporting concept definition.
* In case we don't merge duplicate items:
    - there are **6463** items in **chartevents**
    - it takes **5** mins to extract items from **chartevents** table
    - we don't extract based on **linksto** field of **d_items** because it is INCORRECT)
    - total features: **948392**
* In case we merge duplicate items, **TODO**
    - there are xxx concepts in **chartevents**
    - it takes xxmins to extract items from **chartevents** table
    - we don't extract based on **linksto** field of **d_items** because it is INCORRECT)
    - total features: xxx


### Generate `data_train.csv`:

Here is command to generate:
```
$ cd python
$ python3 main.py create_train_dataset -ed ../data/train -p 8
```

* `data_train.csv` structure: sorted by hadm_id, minutes_ago

```
hadm_id, minutes_ago, conceptid, value
...
...
```

* It takes 1min in average for exporting data of 50 admissions
