import time
from mysql.connector import pooling, errors

_pool = None

def _get_pool():
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name="biblioteca_pool",
            pool_size=1,
            host="bhyzuw3zf8xbwgnzo1cm-mysql.services.clever-cloud.com",
            port=3306,
            user="uss7hp09dihk513n",
            password="VVCRVpNs4hmFzosCAGrx",
            database="bhyzuw3zf8xbwgnzo1cm",
            connection_timeout=10
        )
    return _pool

def conectar():
    pool = _get_pool()
    for intento in range(25):
        try:
            conexion = pool.get_connection()
            conexion.ping(reconnect=True, attempts=3, delay=1)
            return conexion
        except errors.PoolError:
            if intento == 24:
                raise
            time.sleep(0.15)