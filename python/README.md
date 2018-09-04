# README - Predict Length of Stay #

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
$ cd python/src/test/
$ sudo python3 test_suite.py
```

# 2. Main functions

## Prepare data for merge tool

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
