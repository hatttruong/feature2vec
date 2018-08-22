"""Summary

Attributes:
    Configer (TYPE): Description
"""

import logging
import argparse

from src.preprocess import *
from src.configer import *

Configer = Configer('setting.ini')
logging.basicConfig(
    # filename='log.log',
    format='%(asctime)s : %(levelname)s : %(message)s',
    level=logging.INFO)

parser = argparse.ArgumentParser()

print(Configer.ip_address, Configer.port,
      Configer.ssh_username, Configer.ssh_password)
print(Configer.db_name, Configer.db_username, Configer.db_password)


# create_raw_train_dataset('../output')

if __name__ == '__main__':
    parser.add_argument(
        'action', choices=['define_features', 'create_train_dataset'],
        help='define action for preprocess'
    )
    # options for create train data
    parser.add_argument(
        '-ed', '--export_dir',
        help='directory to store train data')
    parser.add_argument(
        '-p', '--process',
        help='number of process')

    # options for definefeatures
    parser.add_argument(
        '-i', '--input_dir',
        help='directory of data')
    parser.add_argument(
        '-o', '--output_dir',
        help='directory to store feature definition')

    args = parser.parse_args()
    if args.action == 'create_train_dataset':
        # create_train_dataset(
        #     export_dir='/media/tuanta/USB/mimic-data/train',
        #     processes=6)
        create_train_dataset(
            export_dir=args.export_dir,
            processes=args.process)
    elif args.action == 'define_features':
        # define_features('../data/raw', '../output')
        define_features(data_dir=args.input_dir, output_dir=args.output_dir)
