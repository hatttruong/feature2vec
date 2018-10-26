# Use LSTM to predict LOS#

## Setup

* Requirement:
    - Linux/MAC: Python 2.7, or >=3.5
    - Windown: Python >= 3.5

* Install Pytorch: refer to [this link](https://pytorch.org/get-started/locally/) to get exactly command to install

```
pip3 install torch
```

## References:
1. [Use pretrain in LSTM](https://medium.com/@martinpella/how-to-use-pre-trained-word-embeddings-in-pytorch-71ca59249f76)

2. [LSTM classification](https://github.com/yuchenlin/lstm_sentence_classifier)

## Predict

### 1. LSTM without pretrain features
```
$ cd los
$ python3 main.py

2018-10-22 21:35:40,378 : INFO : loading LOS data from ../data/los/cvd_los_data.train and ../data/los/cvd_los_data.test
2018-10-22 21:35:40,435 : INFO : train: 2249, test: 964
2018-10-22 21:35:40,435 : INFO : load events for each admission
2018-10-22 21:37:56,750 : INFO : feature size: 27815, label size: 10
2018-10-22 21:37:56,750 : INFO : loading data done!
2018-10-22 21:37:56,798 : INFO : Epoch: 1 start!
2018-10-22 21:57:27,335 : INFO : Epoch: 1 done! train avg_loss:2.24171 , acc:0.174744
2018-10-22 21:58:27,520 : INFO : 'test' avg_loss:2.24051 train acc:0.157676
2018-10-22 22:06:18,242 : INFO : Epoch: 2 done! train avg_loss:2.19147 , acc:0.192975
2018-10-22 22:07:17,313 : INFO : 'test' avg_loss:2.23772 train acc:0.157676
2018-10-22 22:15:06,312 : INFO : Epoch: 3 done! train avg_loss:2.15319 , acc:0.207648
2018-10-22 22:16:05,131 : INFO : 'test' avg_loss:2.23624 train acc:0.169087
2018-10-22 22:24:15,706 : INFO : Epoch: 4 done! train avg_loss:2.10064 , acc:0.241885
2018-10-22 22:25:13,693 : INFO : 'test' avg_loss:2.23978 train acc:0.175311
2018-10-22 22:33:17,743 : INFO : Epoch: 5 done! train avg_loss:2.0315 , acc:0.277901
2018-10-22 22:33:17,752 : INFO : now best dev acc: 0.17531120331950206
2018-10-22 22:34:13,737 : INFO : 'test' avg_loss:2.24576 train acc:0.16805

```
### 2. LSTM with pretrain features using Skip-MF

* With `min_threshold=0`: feature size: 35234, label size: 11
* With `min_threshold=5`: feature size: 18983, label size: 11

Total number of features reduces a half when applying `min_threshold` = 5

#### Grid Search

```
# RUN on SERVER TP7
$ sudo python main.py experiment -pd /media/tuanta/USB/hattt/models

# RUN on local
$ python3 main.py experiment -pd ../models


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

#### 2.1 CASE 1
```
$ cd los
# Local machine - CASE 1
$ python3 main.py --p ../models/skipgram_ce_nm_ws_60_dim_100_epoch_1.vec
2018-10-23 11:12:27,226 : INFO : feature size: 27815, label size: 10
2018-10-23 11:12:27,226 : INFO : loading data done!
2018-10-23 11:12:27,392 : INFO : Epoch: 1 start!
2018-10-23 11:19:12,937 : INFO : Epoch: 1 done! train avg_loss:2.21843 , acc:0.176078
2018-10-23 11:20:13,206 : INFO : 'test' avg_loss:2.16617 train acc:0.189834
2018-10-23 11:26:55,395 : INFO : Epoch: 2 done! train avg_loss:2.13751 , acc:0.197866
2018-10-23 11:27:54,115 : INFO : 'test' avg_loss:2.12258 train acc:0.198133
2018-10-23 11:34:14,699 : INFO : Epoch: 3 done! train avg_loss:2.09526 , acc:0.213428
2018-10-23 11:35:13,763 : INFO : 'test' avg_loss:2.14338 train acc:0.181535
2018-10-23 11:41:01,281 : INFO : Epoch: 4 done! train avg_loss:2.07144 , acc:0.216096
2018-10-23 11:41:59,738 : INFO : 'test' avg_loss:2.09706 train acc:0.21473
2018-10-23 11:47:35,664 : INFO : Epoch: 5 done! train avg_loss:2.04562 , acc:0.22988
2018-10-23 11:47:35,674 : INFO : now best dev acc: 0.21473029045643152
2018-10-23 11:48:30,279 : INFO : 'test' avg_loss:2.07397 train acc:0.221992

```

```
$ python3 main.py -ot adam --p ../models/skipgram_ce_nm_ws_60_dim_100_epoch_1.vec
```

#### 2.2 CASE 2

```
# Local machine - CASE 2
$ sudo python3 main.py --p /media/tuanta/USB/hattt/models/skipgram_ce_nm_ws_180_dim_100_epoch_1.vec
2018-10-23 13:38:36,994 : INFO : 'test' avg_loss:2.10647 train acc:0.208506
```

#### 2.2 CASE 3

```
# Local machine - CASE 3
$ python3 main.py --p /media/tuanta/USB/hattt/models/skipgram_ce_nm_ws_360_dim_100_epoch_1.vec
```

