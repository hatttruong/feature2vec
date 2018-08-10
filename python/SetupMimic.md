# README - Set up MIMIC Database #

This README would normally document whatever steps are necessary to get MIMIC Database up and running

## Request to access MIMIC

Following [this link]( https://mimic.physionet.org/gettingstarted/access/) to get access to MIMIC database. Here is detail steps:

- Get certificate for "Data or Specimens Only Research" course at [CITI programm website](https://www.citiprogram.org/index.cfm?pageID=154&icat=0&ac=0). Important: select **Massachusetts Institute of Technology Affiliates** as your organization affiliation when registering
- Apply request to access MIMIC at [physionet site](https://physionet.org/works/MIMICIIIClinicalDatabase/access.shtml). You have to fill your Professor information (email, phone,...), then Physionet will send a confirmed email to him

## Setup Mimic database
- **Server information**:
    +  [1] TP7's server
        * connect to JVN-student wifi
        * IP: 10.10.9.137
        * mimic data folder: ```/media/tuanta/USB/mimic-data/```
    +  [2] JVN server
        * connect to JVN-staff wifi
        * IP: 192.168.30.54
        * user: ubuntu
        * pass: ddmmyyyy
        * mimic data folder: ```/mnt/data/mimic-data```

- **Install MIMIC locally (Unix/Mac)**
    + Install Postgres:

    ```
    $ sudo apt-get install postgresql

    config /etc/postgresql/9.5/main
    data   /var/lib/postgresql/9.5/main
    locale en_US.UTF-8
    socket /var/run/postgresql
    port   5432
    ```

    +  **Update password** for `postgres` user:

    ```
    # update "md5" to "peer"
    sudo vi  /etc/postgresql/9.5/main/pg_hba.conf

    # restart
    sudo service postgresql restart

    # change password
    $ sudo -i -u postgres
    postgres@ubuntu:~$ psql
    postgres=# \password
    Enter new password:
    Enter it again:
    postgres=#

    # update "peer" to "md5"
    sudo vi  /etc/postgresql/9.5/main/pg_hba.conf

    # restart
    sudo service postgresql restart
    ```

    +  **CLONE MIMIC CODE** repository: 
    ```
    $ git clone https://github.com/MIT-LCP/mimic-code.git
    ```

    + **DOWNLOAD DATA:** download the CSV data files in a local directory. Under ```mimic-code/buildmimic/postgres``` subdirectory 
    
    ```
    # if make is not installed
    $ sudo apt install make

    $ sudo make mimic-download physionetuser=ha.truong2016@ict.jvn.edu.vn datadir="/media/tuanta/USB/mimic-data/
    # datadir="/mnt/data/mimic-data" (on JVN server). 

    ```

    + **CREATE A USER** to access the data
    ```

    # switch to "postgres" user
    $ sudo -i -u postgres
                    
    # create mimicuser (password=123456)
    postgres@ubuntu:~$ createuser -P -s -e -d mimicuser

    # connect to the database with psql
    postgres@ubuntu:~$ psql mimicuser -h 127.0.0.1 -d postgres

    ```

    + **CREATE AN EMPTY DATABASE** containing a MIMIC-III schema (continue at the previous step) called "mimic" containing shema named "mimiciii"
            
    ```
    # connect with psql (run command (1) & (3) of previous step)
    postgres=# CREATE DATABASE mimic OWNER mimicuser;
    postgres=# \c mimic;
    mimic=# CREATE SCHEMA mimiciii;
    ```

    + **CREATE** a set of **EMPTY TABLES** on a mimiciii schema, ready to populate with the data
        
    ```

    $ cd /etc/postgresql/9.5/main
    $ sudo vi pg_hba.conf
    # change the following config
    # TYPE DATABASE USER ADDRESS METHOD
    # local  all      all          peer --> md5

    # restart postgresql
    $ service postgresql restart
    $ sudo /etc/init.d/postgresql stop
    $ sudo /etc/init.d/postgresql start

    # create tables
    $ psql 'dbname=mimic user=mimicuser options=--search_path=mimiciii' -f /home/ubuntu/mimic-code/buildmimic/postgres/postgres_create_tables.sql
    # enter mimicuser password '123456'

    ```
        
    + **IMPORT** the CSV data files into the empty tables
        * Note: 
            *  [reallocate Postgres to another directory](https://www.digitalocean.com/community/tutorials/how-to-move-a-postgresql-data-directory-to-a-new-location-on-ubuntu-16-04)
            *  [create-lvm-storage-in-linux] (https://www.tecmint.com/create-lvm-storage-in-linux/). Use ```fdisk -c -u /dev/sda/```
            
    ```

    $ psql 'dbname=mimic user=mimicuser options=--search_path=mimiciii' -f /home/ubuntu/mimic-code/buildmimic/postgres/postgres_load_data_gz.sql -v mimic_data_dir=/mnt/data/mimic-data/
    # enter mimicuser password '123456'

    ```

    + **ADD INDEXES** to improve performance

    ```
    $ psql 'dbname=mimic user=mimicuser options=--search_path=mimiciii' -f /home/ubuntu/mimic-code/buildmimic/postgres/postgres_add_indexes.sql
    # enter mimicuser password '123456'
    ```

## Query MIMIC database

    [1] ssh hattt@10.10.9.137 [password: see in setting.ini.tp7]
    [2] ssh ubuntu@192.168.30.54 [password: see in setting.ini.jvn]

    hattt@10:~$ sudo -i -u postgres
    postgres@10:~$ psql [password: see in setting.ini]

    # list all database
    postgres=#: \l

    # connect to mimic database
    postgres=# \connect mimic
    You are now connected to database "mimic" as user "postgres".

    mimic=# set search_path to mimiciii;

    # list all tables in mimiciii schema
    mimic=# SELECT * FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';

    # example query
    mimic=# select * from admissions;
