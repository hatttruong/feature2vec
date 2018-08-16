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


# HARD CODE feature definition path and output directory
create_train_dataset()
# create_raw_train_dataset('../output')
# define_features('../data/raw', '../output')
