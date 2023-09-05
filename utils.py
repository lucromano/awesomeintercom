import mysql.connector
import yaml
from uuid import uuid4
import shortuuid
import datetime as dt
import re
from pathlib import Path
import os
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt

env_pointer = yaml.safe_load(open('environment.yaml'))

def get_project_root() -> Path:
    return Path(__file__).parent.parent

if env_pointer['ENV'] == 'local':
    db_pointer = yaml.safe_load(open('db_local.yaml'))
else:
    root = get_project_root()
    config_path = os.path.join(root, 'config/')
    db_pointer = yaml.safe_load(open(os.path.join(config_path, 'db_prod.yaml')))

mysql_host = db_pointer['MYSQL_HOST']
mysql_user = db_pointer['MYSQL_USER']
mysql_password = db_pointer['MYSQL_PASSWORD']
mysql_database = db_pointer['MYSQL_DATABASE']


def user_login(email):

    cnx = mysql.connector.connect(host=mysql_host, user=mysql_user, password=mysql_password, database=mysql_database)

    get_data = (email,)
    get_query = "SELECT hashed_password from dim_user where email = %s"

    cursor = cnx.cursor()
    cursor.execute(get_query, get_data)

    get_result = cursor.fetchall()
    cnx.close()

    return get_result


def create_user(first_name, last_name, email, password):

    user_uuid = str(uuid4())
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    cnx = mysql.connector.connect(host=mysql_host, user=mysql_user, password=mysql_password, database=mysql_database)

    post_data = (user_uuid, first_name, last_name, email, hashed_password)
    post_query = "INSERT INTO dim_user VALUES(%s, %s, %s, %s, %s)"

    cursor = cnx.cursor()
    cursor.execute(post_query, post_data)
    cnx.commit()
    cnx.close()


