import pandas as pd
from pathlib import Path

from src.db_util import *

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def insert_concept(concept, unitname, itemids):
    """Summary
    """
    query = "WITH rows AS (\
        INSERT INTO jvn_concepts(concept, unitname) \
        VALUES('%s', '%s') \
        RETURNING conceptid \
    ) SELECT conceptid FROM rows" % (concept, unitname)

    logger.info('start insert concept: %s', locals())
    conceptid = execute_non_query(query, has_return=True)

    for itemid in itemids:
        insert_mapping_concept(conceptid, itemid)

    logger.info('done insert_concept')


def insert_mapping_concept(conceptid, itemid):
    """Summary

    Args:
        conceptid (TYPE): Description
        itemid (TYPE): Description
    """
    logger.info('start insert_mapping_concept: %s', locals())
    query = "INSERT INTO jvn_mapping_concept(conceptid, itemid) \
        VALUES (%s, %s)" % (conceptid, itemid)
    execute_non_query(query)
    logger.info('done insert_mapping_concept')


def insert_mapping_value(conceptid, value, unified_value):
    logger.info('start insert_mapping_value: %s', locals())
    query = "INSERT INTO jvn_mapping_value(conceptid, value, unified_value) \
        VALUES (%s, %s, %s)" % (conceptid, value, unified_value)
    execute_non_query(query)
    logger.info('done insert_mapping_value')


def find_concept_id(concept):
    query = 'SELECT * FROM jvn_concepts WHERE concept="%s"' % concept
    df = execute_query_to_df(query)
    if df.shape[0] != 1:
        raise ValueError('Cannot find concept "%s" in database' % concept)

    return df['conceptid'][0]


def insert_concept_from_file():
    concept_df = pd.read_csv(
        Path('../mics/mapping_concepts.csv'), index_col=False)
    for index, row in concept_df.iterrows():
        # concept, unitname, numeric, itemids
        itemids = row['itemids'].split()
        insert_concept(concept=row['concept'],
                       unitname=row['unitname'],
                       itemids=itemids)


def insert_mapping_value_from_file():
    concept_df = pd.read_csv(
        Path('../mics/mapping_value.csv'), index_col=False)
    for index, row in concept_df.iterrows():
        # concept, value, unified_value
        # find concept id
        conceptid = find_concept_id(row['concept'])
        insert_mapping_value(conceptid=conceptid,
                             value=row['value'],
                             unified_value=row['unified_value'])
