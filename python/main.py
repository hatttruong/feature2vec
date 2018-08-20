"""Summary

Attributes:
    Configer (TYPE): Description
"""
from src.connect_db import *
from src.db_util import *
from src.preprocess import *
from src.configer import *

Configer = Configer('setting.ini')
logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s',
    level=logging.INFO)

print(Configer.ip_address, Configer.port,
      Configer.ssh_username, Configer.ssh_password)
print(Configer.db_name, Configer.db_username, Configer.db_password)


# HARD CODE feature definition path
# /media/tuanta/USB/mimic-data/train_all_items
# processes=6
#
create_train_dataset(
    export_dir='/media/tuanta/USB/mimic-data/train',
    file_name='data_train_5.csv',
    processes=6)
# create_raw_train_dataset('../output')
# define_features('../data/raw', '../output')
