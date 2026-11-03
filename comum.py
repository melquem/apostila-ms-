"""Conexões compartilhadas. Credenciais SEMPRE via variável de ambiente (nunca no código)."""
import os


def mongo_db(nome="seguranca"):
    from pymongo import MongoClient
    uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
    return MongoClient(uri, serverSelectionTimeoutMS=3000)[nome]


def mysql_conn():
    import mysql.connector
    return mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST", "localhost"),
        user=os.environ.get("MYSQL_USER", "root"),
        password=os.environ["MYSQL_PASSWORD"],
        database=os.environ.get("MYSQL_DATABASE", "seguranca"))
