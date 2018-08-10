'''
Small script to show PostgreSQL and Pyscopg together

Attributes:
    logger (TYPE): Description

Deleted Attributes:
    columns (TYPE): Description
    query (str): Description
'''


import psycopg2
import psycopg2.extras
from sshtunnel import SSHTunnelForwarder
import logging
import pandas as pd

from src.configer import Configer


Configer = Configer('setting.ini')
logger = logging.getLogger(__name__)


def execute_query(query):
    """
    connect to server using ssh
    connect to database MIMIC
    execute query and fetch data

    Raises:
        e: Description

    Returns:
        TYPE: Description

    Args:
        query (TYPE): Description
    """
    try:

        with SSHTunnelForwarder(
                (Configer.ip_address, Configer.port),
                ssh_username=Configer.ssh_username,
                ssh_password=Configer.ssh_password,
                remote_bind_address=('localhost', 5432)) as server:

            server.start()
            logger.debug('server connected')
            logger.debug('server.local_bind_port: %s', server.local_bind_port)

            params = {
                'database': Configer.db_name,
                'user': Configer.db_username,
                'password': Configer.db_password,
                'host': 'localhost',
                'port': server.local_bind_port
            }

            conn = psycopg2.connect(**params)
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            logger.debug('database %s connected', params)

            cursor.execute('set search_path to %s' % Configer.search_path)
            logger.debug('set search_path to %s' % Configer.search_path)

            return fetch(cursor, query)

    except Exception as e:
        logger.error('Connection Failed')
        raise e


def fetch(cursor, query):
    """Summary

    Args:
        cursor (TYPE): Description
        query (str): query instance

    Returns:
        list: list of DictRow
    """
    rows = []

    cursor.execute(query)
    for row in cursor:
        rows.append(row)
    return rows


def execute_query_to_df(query):
    """Summary

    Args:
        query (TYPE): Description

    Returns:
        DataFrame: Description
    """
    rows = execute_query(query)
    df = pd.DataFrame.from_dict([i.copy() for i in rows])
    return df


def execute_non_query(query, has_return=False):
    """
    connect to server using ssh
    connect to database MIMIC
    execute nonquery

    Raises:
        e: Description

    Returns:
        TYPE: Description

    Args:
        query (TYPE): Description
        has_return (bool, optional): Description
    """
    return_id = None
    try:

        with SSHTunnelForwarder(
                (IP_ADDRESS, PORT),
                ssh_username=SSH_USERNAME,
                ssh_password=SSH_PASSWORD,
                remote_bind_address=('localhost', 5432)) as server:

            server.start()
            logger.debug('server connected')
            logger.debug('server.local_bind_port: %s', server.local_bind_port)

            params = {
                'database': DB_NAME,
                'user': DB_USERNAME,
                'password': DB_PASSWORD,
                'host': 'localhost',
                'port': server.local_bind_port
            }

            conn = psycopg2.connect(**params)
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            logger.debug('database %s connected', params)

            cursor.execute('set search_path to %s' % SEARCH_PATH)
            logger.debug('set search_path to %s' % SEARCH_PATH)

            cursor.execute(query)
            conn.commit()

            if has_return:
                # get return ID
                for row in cursor:
                    return_id = row[0]
                    break

    except Exception as e:
        logger.error('Connection Failed')
        raise e

    return return_id
