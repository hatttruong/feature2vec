"""Summary

Attributes:
    Configer (TYPE): Description
"""

import logging
import argparse

from src.preprocess import *
from src.item_preprocessor import *
from src.configer import *
from src import tfidf

Configer = Configer('setting.ini')
logging.basicConfig(
    # filename='log.log',
    format='%(asctime)s : %(levelname)s : %(message)s',
    level=logging.INFO)

parser = argparse.ArgumentParser()

print(Configer.ip_address, Configer.port,
      Configer.ssh_username, Configer.ssh_password)
print(Configer.db_name, Configer.db_username, Configer.db_password)


if __name__ == '__main__':
    parser.add_argument(
        'action',
        choices=['define_concepts', 'update_chartevents',
                 'create_train_dataset', 'crawl_webpages',
                 'tfidf_medical_webpages', 'cluster', 'backup', 'restore',
                 'create_los_dataset'],
        help='define action for preprocess'
    )
    parser.add_argument('-p', '--process', default=2, type=int,
                        help='number of process')

    parser.add_argument(
        '-cd', '--concept_dir', default='../data',
        help='directory to store concept definition')

    # options for create train data
    parser.add_argument(
        '-ed', '--export_dir',
        help='directory to store train data (options for create train data)')

    args = parser.parse_args()
    if args.action == 'define_concepts':
        define_concepts(output_dir=args.concept_dir,
                        processes=args.process)
    elif args.action == 'update_chartevents':
        update_chartevents_value(concept_dir=args.concept_dir)

    elif args.action == 'create_train_dataset':
        create_train_feature_dataset(export_dir=args.export_dir,
                                     processes=args.process,
                                     concept_dir=args.concept_dir)
    elif args.action == 'crawl_webpages':
        # TODO: parameters
        export_dir = '../data/webpages'
        concept_dir = '../data'
        crawl_webpages(concept_dir, export_dir)
    elif args.action == 'tfidf_medical_webpages':
        tfidf.train_tfidf(min_count=5, chunksize=5000, ngrams=(1, 1),
                          model_dir='../models')
    elif args.action == 'cluster':
        cluster()
    elif args.action == 'backup':
        backup_merge_data()
    elif args.action == 'restore':
        restore_merge_data()
    elif args.action == 'create_los_dataset':
        create_cvd_los_dataset(export_dir=args.export_dir,
                               concept_dir=args.concept_dir)
