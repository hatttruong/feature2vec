#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Testcases for preprocess file

"""
import sys
import unittest
sys.path.append('../')

import preprocess
import db_util


class TestPreprocessMethods(unittest.TestCase):

    """
    Test cases for functions of text_preprocessing.preprocess module
        - remove_numbers
        - lowercase

    """

    def test_save_dictionary_object(self):
        """Summary
        """
        dict_data = {"1":
                     [{'itemid': 123, 'label': 'label 1',
                       'abbreviation': 'abbreviation 1'},
                      {'itemid': 456, 'label': 'label 2',
                       'abbreviation': 'abbreviation 2'}],
                     "2":
                     [{'itemid': 123, 'label': 'label 1',
                       'abbreviation': 'abbreviation 1'},
                      {'itemid': 456, 'label': 'label 2',
                          'abbreviation': 'abbreviation 2'}
                      ]
                     }
        output_path = 'test_save_dictionary_object.json'
        preprocess.export_dict_to_json(dict_data, output_path)
        self.assertEqual(
            preprocess.load_dict_from_json(output_path),
            dict_data)

    def test_compute_min_max_step(self):
        """Summary
        """
        values = [5, 5.6, 7.878, 10, 11.312, 13.4, 15.6978,
                  17.6, 8, 9.6, 24.0123, 30]
        min_value, max_value, steps = preprocess.compute_min_max_step(values)
        self.assertEqual(steps, 0.1)

        values = [5, 5, 7, 10, 11.3, 13, 15, 17, 8, 9, 24, 30, 3, 34]
        min_value, max_value, steps = preprocess.compute_min_max_step(values)
        self.assertEqual(steps, 1)

    def test_get_feature_index(self):
        """Summary
        """
        preprocess.features = preprocess.load_dict_from_json(
            'feature_definition.txt')

        # category feature
        self.assertEqual(
            preprocess.get_feature_index('212', 'Wand.Atrial Pace'), 6)

        # numeric feature
        self.assertEqual(preprocess.get_feature_index('828', 93.0), 524)

        # less than min value=52
        self.assertEqual(preprocess.get_feature_index('828', 20), 482)

        # greater than max value=489
        self.assertEqual(preprocess.get_feature_index('828', 500), 921)


if __name__ == '__main__':
    unittest.main()
