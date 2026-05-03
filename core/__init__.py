try:
    import pymysql

    pymysql.install_as_MySQLdb()
except ModuleNotFoundError:
    # Allow non-MySQL environments (e.g. sqlite in local/test)
    pass
