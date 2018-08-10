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

TODO