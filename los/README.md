# Use LSTM to predict LOS#

## Setup
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
$ python3 lstm_model.py

2018-10-22 21:35:40,378 : INFO : loading LOS data from ../data/los/cvd_los_data.train and ../data/los/cvd_los_data.test
2018-10-22 21:35:40,435 : INFO : train: 2249, test: 964
2018-10-22 21:35:40,435 : INFO : load events for each admission
2018-10-22 21:37:56,750 : INFO : feature size: 27815, label size: 10
2018-10-22 21:37:56,750 : INFO : loading data done!
2018-10-22 21:37:56,798 : INFO : Epoch: 1 start!
2018-10-22 21:57:27,335 : INFO : Epoch: 1 done! train avg_loss:2.24171 , acc:0.174744
2018-10-22 22:06:18,242 : INFO : Epoch: 2 done! train avg_loss:2.19147 , acc:0.192975
2018-10-22 22:15:06,312 : INFO : Epoch: 3 done! train avg_loss:2.15319 , acc:0.207648
2018-10-22 22:24:15,706 : INFO : Epoch: 4 done! train avg_loss:2.10064 , acc:0.241885
2018-10-22 22:33:17,743 : INFO : Epoch: 5 done! train avg_loss:2.0315 , acc:0.277901
2018-10-22 22:33:17,752 : INFO : now best dev acc: 0.17531120331950206
2018-10-22 22:34:13,737 : INFO : 'test' avg_loss:2.24576 train acc:0.16805

```
### 2. LSTM with pretrain features using Skip-MF

```
$ cd los
$ python3 lstm_model.py
```