import data_loader
import logging
import random
import numpy as np
import pandas as pd
import sys
import math

from sklearn.metrics import confusion_matrix
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score

# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)

# set a format which is simpler for console use
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')

# tell the handler to use this format
console.setFormatter(formatter)

# add the handler to the root logger
logger = logging.getLogger(__name__)
logger.addHandler(console)


SEED = 1
DATA_DIR = '../data'
DATA_FILE_PATH = DATA_DIR + '/los/cvd_los_data.csv'
LOS_GROUPS_PATH = DATA_DIR + '/los/los_groups.csv'
CONCEPT_DEF_PATH = DATA_DIR + '/concept_definition.json'
NUMERIC_TYPE = 0
CATEGORICAL_TYPE = 1


def transform_events_to_features(admission_id, concept_definitions,
                                 within_hours=48):
    """
    Transform events with their values as:
        - categorical: lastest value
        - numeric: mean/max/min values
    """
    events_df = pd.read_csv(
        DATA_DIR + '/heart_admissions/data_train_%s.csv' % int(admission_id),
        header=None,
        names=['admission_id', 'minutes_ago', 'itemid', 'value'])

    numeric_features = dict()
    categorical_features = dict()
    for index, row in events_df.iterrows():
        itemid = row['itemid']
        value = row['value']
        minutes_ago = row['minutes_ago']
        if minutes_ago > within_hours * 60:
            break

        if itemid in concept_definitions:
            if concept_definitions[itemid]['type'] == NUMERIC_TYPE:
                if itemid in numeric_features:
                    numeric_features[itemid].append(value)
                else:
                    numeric_features[itemid] = [value]
            else:
                # if categorical event, get the latest value
                categorical_features[itemid] = value

    transformed_features = dict()
    for itemid in categorical_features.keys():
        transformed_features['%s_%s' %
                             (int(itemid), categorical_features[itemid])] = 1

    for itemid in numeric_features.keys():
        transformed_features['%s_min' %
                             int(itemid)] = np.min(numeric_features[itemid])
        transformed_features['%s_max' %
                             int(itemid)] = np.max(numeric_features[itemid])
        transformed_features['%s_mean' %
                             int(itemid)] = np.mean(numeric_features[itemid])

    return transformed_features


def load_data(los_splitters):
    """Summary
    """
    logger.info('START prepare data...')
    concept_definitions = data_loader.load_concept_definition()

    # load heart admission
    data_df = pd.read_csv(data_loader.DATA_FILE_PATH)
    data_dict = data_df[['hadm_id', 'los_hospital']].to_dict('records')

    # create train/test admission ids
    random.seed(SEED)
    random.shuffle(data_dict)
    split = int(len(data_dict) * 0.7)
    train_admission_ids = [x['hadm_id'] for x in data_dict[: split]]
    test_admission_ids = [x['hadm_id'] for x in data_dict[split:]]

    # load train data
    X_train = []
    y_train = []
    X_test = []
    y_test = []
    for index, admission in enumerate(data_dict):
        admission_id = admission['hadm_id']

        # first 24h & 48h
        for i in range(2):
            # dictionary of {feature_name: value}
            transformed_features = transform_events_to_features(
                admission_id, concept_definitions, within_hours=(i + 1) * 24)
            true_label = data_loader.get_los_group_idx(
                admission['los_hospital'] - i, los_splitters)
            if admission_id in train_admission_ids:
                X_train.append(transformed_features)
                y_train.append(true_label)
            else:
                X_test.append(transformed_features)
                y_test.append(true_label)
        sys.stdout.write('\r')
        sys.stdout.write('load data for %s admissions...' % (index + 1))
        sys.stdout.flush()
    sys.stdout.write('\r')

    # convert to matrix
    X_train_df = pd.DataFrame(X_train)
    logger.info('X_train_df.shape=%s', X_train_df.shape)
    X_train_df.dropna(axis=1, thresh=X_train_df.shape[0] * 0.3, inplace=True)
    logger.info('After drop na, X_train_df.shape=%s', X_train_df.shape)
    # logger.info('Feature name: %s', X_train_df.columns)

    X_test_df = pd.DataFrame(X_test)
    logger.info('X_test_df.shape=%s', X_test_df.shape)

    # drop columns follows X_train_df
    X_test_df = X_test_df[X_train_df.columns]
    logger.info('After drop columns, X_test_df.shape=%s', X_test_df.shape)

    # fill missing value
    na_fill_dict = dict()
    numeric_feature_suffix = ['_min', '_max', '_mean']
    for col in X_train_df.columns:
        is_categorical = True
        for suffix in numeric_feature_suffix:
            if suffix in col:
                is_categorical = False
                break

        if is_categorical:
            na_fill_dict[col] = 0
        else:
            na_fill_dict[col] = np.mean(
                [x for x in X_train_df[col] if math.isnan(x) is False])
            logger.debug('na_fill_dict[%s]=%s', col, na_fill_dict[col])

    logger.info('na_fill_dict.size: %s', len(na_fill_dict))

    logger.debug('total na values of X_train: %s',
                 X_train_df.isnull().values.sum())
    logger.debug('total na values of X_test: %s',
                 X_test_df.isnull().values.sum())

    X_train_df = X_train_df.fillna(value=na_fill_dict)
    X_test_df = X_test_df.fillna(value=na_fill_dict)

    logger.debug('total na values of X_train: %s',
                 X_train_df.isnull().values.sum())
    logger.debug('total na values of X_test: %s',
                 X_test_df.isnull().values.sum())

    logger.info('DONE prepare data.')
    return X_train_df.values, y_train, X_test_df.values, y_test


def rf_gridsearch(X_train, y_train, X_test, y_test, is_binary=True):
    n_estimators = [int(x) for x in np.linspace(start=200, stop=5000, num=10)]
    max_features = ['auto', 'sqrt', 'log2']
    max_depth = [int(x) for x in np.linspace(100, 1000, num=5)]
    max_depth.append(None)
    min_samples_split = [2, 5, 10]
    min_samples_leaf = [1, 3, 10]
    bootstrap = [True, False]
    criterion = ["gini", "entropy"]

    tuned_parameters = {'n_estimators': n_estimators,
                        'max_features': max_features,
                        'max_depth': max_depth,
                        'min_samples_split': min_samples_split,
                        'min_samples_leaf': min_samples_leaf,
                        'bootstrap': bootstrap,
                        "criterion": criterion}

    scores = ['accuracy']

    for score in scores:
        logger.info("# Tuning hyper-parameters for %s", score)

        # clf = GridSearchCV(RandomForestClassifier(), tuned_parameters, cv=5,
        #                    scoring='%s' % score, n_jobs=-1, verbose=2)
        clf = RandomizedSearchCV(estimator=RandomForestClassifier(),
                                 param_distributions=tuned_parameters,
                                 n_iter=20, scoring='%s' % score, cv=3,
                                 verbose=2, random_state=42, n_jobs=-1)
        clf.fit(X_train, y_train)

        logger.info("Best parameters set found on development set:")
        logger.info(clf.best_params_)
        logger.info("Grid scores on development set:")
        means = clf.cv_results_['mean_test_score']
        stds = clf.cv_results_['std_test_score']
        for mean, std, params in zip(means, stds, clf.cv_results_['params']):
            logger.info("%0.3f (+/-%0.03f) for %r", mean, std * 2, params)

        logger.info("Detailed classification report:")
        logger.info("The model is trained on the full development set.")
        logger.info("The scores are computed on the full evaluation set.")
        y_true, y_pred = y_test, clf.predict(X_test)
        logger.info('accuracy: %s', accuracy_score(y_true, y_pred))

        average = 'binary' if is_binary else 'weighted'
        logger.info('f1_score: %s', f1_score(y_true, y_pred, average=average))
        logger.info('precision_score: %s', precision_score(
            y_true, y_pred, average=average))
        logger.info('recall_score: %s', recall_score(
            y_true, y_pred, average=average))
        logger.info(classification_report(y_true, y_pred))
        logger.info('Confusion_matrix: \n%s',
                    confusion_matrix(y_true, y_pred))


def rf_experiments():
    los_groups = data_loader.load_los_groups()
    logger.info('Total los groups: %s', los_groups)

    # START Ad-hoc
    skip = 0
    # END ad-hoc
    for los_group in los_groups:
        if skip > 0:
            skip -= 1
            continue
        logger.info('START train with los_group=%s', los_group['name'])

        X_train, y_train, X_test, y_test = load_data(los_group['values'])
        rf_gridsearch(X_train, y_train, X_test, y_test)

        logger.info('DONE train with los_group=%s', los_group['name'])


logging.basicConfig(
    filename='log_rf_model.log',
    format='%(asctime)s : %(levelname)s : %(message)s',
    level=logging.INFO)

rf_experiments()
