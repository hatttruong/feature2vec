"""Summary
"""
from unittest import TextTestRunner, TestSuite, TestLoader
from test_preprocess import *
import logging

logging.basicConfig(
    # filename=os.path.join(Configer.log_dir, 'train_unsupervised.log'),
    format='%(asctime)s : %(levelname)s : %(message)s',
    level=logging.INFO)


def suite():
    """Summary

    Returns:
        TYPE: Description
    """
    loader = TestLoader()
    suite = TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(TestPreprocessMethods))
    return suite


if __name__ == '__main__':
    runner = TextTestRunner(verbosity=2)
    runner.run(suite())
