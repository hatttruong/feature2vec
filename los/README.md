# Use LSTM to predict LOS#

## Setup

* Requirement:
    - Linux/MAC: Python 2.7, or >=3.5
    - Windown: Python >= 3.5
    - pip3 install pandas
    - pip3 install -U scikit-learn

* Install Pytorch: refer to [this link](https://pytorch.org/get-started/locally/) to get exactly command to install

```
$ pip3 install torch
$ pip3 install torch torchvision # python 3.6
```

## References:
1. [Use pretrain in LSTM](https://medium.com/@martinpella/how-to-use-pre-trained-word-embeddings-in-pytorch-71ca59249f76)

2. [LSTM classification](https://github.com/yuchenlin/lstm_sentence_classifier)

## Predict

### 1. LSTM with pretrain features using Skip-MF

* With `min_threshold=0`: feature size: 35234, label size: 11
* With `min_threshold=5`: feature size: 18983, label size: 11

Total number of features reduces a half when applying `min_threshold` = 5

#### Grid Search

```
# RUN on SERVER TP7
$ sudo python main.py experiment -pd /media/tuanta/USB/hattt/models  -ld ../data/los/los_groups.csv

# RUN on local
$ python3 main.py experiment -pd ../models -ld ../data/los/los_groups.csv

# RUN on local - MULTI PROCESS
$ python3 main.py multi -pd ../models -ld ../data/los/los_groups.csv -p 2


create train data for 3213 admissions, total samples: 19448
feature size: 18983, label size: 11
```

Some notes:

* with 2 LOS groups:
    - [WITHOUT pretrain]: **2 hours**/epoch, **minutes**/evaluate, accuracy: **%**
    - [WITH pretrain]: **1.5 hours**/epoch, **10 minutes**/evaluate, accuracy: **94.5%**
* with 3 LOS groups:
    - [WITHOUT pretrain]: **hours**/epoch, **minutes**/evaluate, accuracy: **%**
    - [WITH pretrain]: **hours**/epoch, **minutes**/evaluate, accuracy: **%**
* with 5 LOS groups:
    - [WITHOUT pretrain]: **hours**/epoch, **minutes**/evaluate, accuracy: **%**
    - [WITH pretrain]: **hours**/epoch, **minutes**/evaluate, accuracy: **%**
* with 11 LOS groups:
    - [WITHOUT pretrain]: **hours**/epoch, **minutes**/evaluate, accuracy: **%**
    - [WITH pretrain]: **hours**/epoch, **minutes**/evaluate, accuracy: **%**


### 2. Random Forest

```
$ python rf_model.py


2018-12-11 19:10:58,466 : INFO : Total los groups: [{'name': '95-percentile', 'values': [21]}, {'name': '90-percentile', 'values': [21, 2]}, {'name': '30-percentile', 'values': [21, 9, 5, 2]}, {'name': '10-percentile', 'values': [21, 14, 10, 9, 7, 6, 5, 4, 3, 2]}]
2018-12-11 19:10:58,467 : INFO : START prepare data...
2018-12-11 19:45:29,044 : INFO : X_train_df.shape=(17992, 8926)
2018-12-11 19:45:32,634 : INFO : After drop na, X_train_df.shape=(17992, 370)
2018-12-11 19:45:39,970 : INFO : X_test_df.shape=(7712, 7326)
2018-12-11 19:45:40,011 : INFO : After drop columns, X_test_df.shape=(7712, 370)
2018-12-11 19:45:40,644 : INFO : na_fill_dict.size: 370
2018-12-11 19:45:40,888 : INFO : DONE prepare data.
```

Result:

* los_group=95-percentile, values=[21]
