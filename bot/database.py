import os
import psycopg2
from psycopg2 import pool
import logging

logger = logging.getLogger(__name__)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "finn")
DB_USER = os.getenv("DB_USER", "finn")
DB_PASSWORD = os.getenv("DB_PASSWORD", "finn")

_pool = None


def get_pool():
    global _pool
    if _pool is None:
        _pool = psycopg2.pool.SimpleConnectionPool(
            1, 10,
            host=DB_HOST, port=DB_PORT,
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
        )
        logger.info(f"DB pool connected to {DB_HOST}:{DB_PORT}/{DB_NAME}")
    return _pool


def get_conn():
    return get_pool().getconn()


def put_conn(conn):
    get_pool().putconn(conn)
