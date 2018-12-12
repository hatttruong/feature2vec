"""Summary

Attributes:
    Configer (TYPE): Description
"""

import logging
import argparse

import lstm_model

logging.basicConfig(
    filename='log_los_local_multi.log',
    format='%(asctime)s : %(levelname)s : %(message)s',
    level=logging.INFO)

parser = argparse.ArgumentParser()

if __name__ == '__main__':
    parser.add_argument(
        'action',
        choices=['train', 'experiment', 'multi'],
        help='define action: train model, experiment with multi process or experiment one process'
    )
    parser.add_argument(
        '-pd', '--pretrained_dir', default='../models',
        help='path to pretrained dir (for grid_search)')
    parser.add_argument(
        '-ld', '--los_dir', default=None,
        help='path to los groups definition (for grid_search)')
    parser.add_argument(
        '-pp', '--pretrained_path', default=None,
        help='path to pretrained vectors')
    parser.add_argument(
        '-p', '--processes', type=int, default=2, help='number of processes')
    parser.add_argument(
        '-hd', '--hidden_dim', type=int, default=50,
        help='hidden dimension in LSTM')
    parser.add_argument(
        '-e', '--epoch', type=int, default=5, help='epoch value')
    parser.add_argument(
        '-ot', '--optimizer_type',
        choices=['sgd', 'adam'],
        default='adam',
        help='optimizer type')

    args = parser.parse_args()

    if args.action == 'train':
        lstm_model.train(hidden_dim=args.hidden_dim, epoch=args.epoch,
                         optimizer_type=args.optimizer_type,
                         pretrained_path=args.pretrained_path)
    elif args.action == 'multi':
        lstm_model.grid_search_multi_process(pretrained_dir=args.pretrained_dir,
                                             los_groups_path=args.los_dir,
                                             processes=args.processes)
    else:
        lstm_model.grid_search(pretrained_dir=args.pretrained_dir,
                               los_groups_path=args.los_dir)
