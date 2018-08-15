"""Summary

Attributes:
    df (TYPE): Description
    query (str): Description
"""
from src.connect_db import *
from src.db_util import *
from src.preprocess import *
from src.configer import *
# from src import concept_helper
import os
# from pathlib import Path


Configer = Configer('setting.ini')
logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s',
    level=logging.INFO)

print(Configer.ip_address, Configer.port,
      Configer.ssh_username, Configer.ssh_password)
print(Configer.db_name, Configer.db_username, Configer.db_password)


def represents_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def hash(str):
    h = 2166136261
    for (i=0
         i < str.size()
         i + +)
        h = h ^ uint32_t(int8_t(str[i]))
        h = h * 16777619

    return h

# define_features()

# group_items = [
#     # '212 220048  Heart Rhythm',
#     #                '161 224650  Ectopy Type 1',
#     #                '162 226479  Ectopy Type 2',
#     #                '159 224651  Ectopy Frequency 1',
#     #                '160 226480  Ectopy Frequency 2',
#     '211 220045  Heart Rate',
#     '814 220228  Hemoglobin',
#     '833 RBC',
#     '1542 220546 861 4200 1127 WBC',
#     '828 3789        Platelet']
# for group_item in group_items:
#     items = group_item.split()
#     items = [x for x in items if len(x) > 0]
#     ids = []
#     for x in items:
#         if represents_int(x):
#             ids.append(int(x))
#         else:
#             break

#     print('ids=[%s], file="%s.csv"' %
#           (','.join([str(x) for x in ids]), group_item))
#     get_chartevents_by_ids(
#         ids, os.path.join('data', 'raw', '%s.csv' % group_item))

# define_features('../data/raw', )
# redefine_features(os.path.join('../output', 'feature_definition.json.backup'))
# create_train_dataset('../output')
