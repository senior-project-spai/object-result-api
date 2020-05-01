import os

S3 = {
    'ENDPOINT': os.environ['S3_ENDPOINT'],
    'ACCESS_KEY': os.environ['S3_ACCESS_KEY'],
    'SECRET_KEY': os.environ['S3_SECRET_KEY']
}

MYSQL = {
    'host': os.environ['MYSQL_HOST'],
    'port': os.environ['MYSQL_PORT'],
    'user': os.environ['MYSQL_USER'],
    'passwd': os.environ['PASSWORD'],
    'db': os.environ['MYSQL_DB'] 
}
