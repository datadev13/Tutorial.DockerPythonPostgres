from time import sleep
from random import randint
from sqlalchemy import create_engine
from config import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, HOST


def get_pg_engine(host=HOST, postgres_user=POSTGRES_USER,
                  postgre_pass=POSTGRES_PASSWORD, postgre_db=POSTGRES_DB):
    engine = create_engine("postgresql+psycopg2://%s:%s@%s:5432/%s" % (postgres_user, postgre_pass, host, postgre_db))
    return engine


if __name__ == "__main__":
    while True:
        sleep(5)
        with open("./my_text.txt", 'a+', encoding="utf-8") as file:
            file.write("%s\n" % randint(1, 1000))
        with get_pg_engine().connect().execution_options(autocommit=True) as conn:
            with conn.begin():
                conn.execute(
                    "INSERT INTO numbers (id, number, ctime) "
                    "VALUES (nextval('numbers_seq'), %d, NOW());" % randint(1, 1000))
