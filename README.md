## Tutorial: Docker + Python app + PostgreSQL

### For this tutorial I used:
* Ubuntu LTS: 20.04
* Python: 3.9
* Docker: 20.10
* Docker Compose: 1.29
* PostgreSQL: latest
* PyCharm Community


### Step 0: Configuring work area

#### 1. Install [Docker](https://docs.docker.com/engine/install/) & [Docker Compose](https://docs.docker.com/compose/install/).
* *If you use Windows, install [Docker Desktop](https://docs.docker.com/desktop/windows/install/).*
#### 2. Creating project directories.

    you_project_dir
    ├───app
    └───database

_*After completing this step, check the installation was successful :*_

**Check Docker version:**
```shell
$ docker --version
Docker version 20.10.8, build 3967b7d
```

**Check Docker Compose version:**
```shell
$ docker-compose --version
docker-compose version 1.29.2, build 5becea4c
```

### Step 1: Creating Python app files

#### 1. Create *requirements.txt* file in app directory.
_*This file contains the packages that are needed for the Python app to work.*_

**Path:** *you_project_dir/app/requirements.txt*

```
greenlet==1.1.2
psycopg2-binary==2.9.1
SQLAlchemy==1.4.26
```

#### 2. Create *config.py* file in app directory.
_*This file is configuration for Python training app.*_

**Path:** *you_project_dir/app/config.py*

```python
# Import Python packages.
import os
import sys

# Get environment variables.
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_DB = os.environ.get("POSTGRES_DB")
# Docker database service name.
HOST = "postgres_database"

# This code block say: if NAME start file == THIS file THEN do this.
if __name__ == "__main__":
    sys.exit()
```

#### 3. Create *main.py* file in app directory.
_*This file is Python training app.*_

**Path:** *you_project_dir/app/main.py*

```python
from time import sleep
from random import randint
from sqlalchemy import create_engine
# Import configuration variables from config.py.
from config import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, HOST

# This func created Engine to PostgreSQL database.
# For this example, we will set the default values for the function arguments.
def get_pg_engine(host=HOST, postgres_user=POSTGRES_USER,
                  postgre_pass=POSTGRES_PASSWORD, postgre_db=POSTGRES_DB):
    engine = create_engine("postgresql+psycopg2://%s:%s@%s:5432/%s" % (postgres_user, postgre_pass, host, postgre_db))
    return engine

# This code block say: if NAME start file == THIS file THEN do this.
if __name__ == "__main__":
    # Tutorial dataflow
    while True:
        sleep(5)

        # Insert random number into tutorial file on app container.
        with open("./my_text.txt", 'a+', encoding="utf-8") as file:
            file.write("%s\n" % randint(1, 1000))

        # Insert random number into PostgreSQL on database container.
        # Open session with autocommit.
        with get_pg_engine().connect().execution_options(autocommit=True) as conn:
            # Create transaction.
            with conn.begin():
                # INSERT id (incremental value), random number, current timestamp.
                conn.execute(
                    "INSERT INTO numbers (id, number, ctime) "
                    "VALUES (nextval('numbers_seq'), %d, NOW());" % randint(1, 1000))
```

#### 4. Create *Dockerfile* file in app directory.
_*Dockerfile configures application image using commands.*_

**Path:** *you_project_dir/app/Dockerfile*

```dockerfile
# Get Python 3.9 Slim version.
FROM python:3.9-slim

# Upgrade pip version.
RUN /usr/local/bin/python -m pip install --upgrade pip
# Create work directory and set permissions.
RUN mkdir /app && chmod 770 ./app
# Set work directory.
WORKDIR /app
# Copy all python app files in work directory.
COPY . /app
# Run install Python packages from requiremts.txt.
RUN pip install -r /app/requirements.txt
# Start app on container.
CMD [ "python", "/app/main.py" ]
```

### Let's summarize Step 1.

_*We created a directory with our project, we also made a Dockerfile, which we will use to build the final project through Docker Compose.*_

_*After completing this step, you should have the following project structure:*_

    you_project_dir
        ├───app
        │    ├───main.py
        │    ├───config.py
        │    ├───requirements.txt
        │    └───Dockerfile
        └───database


### Step 2: Creating auxiliary files for the database

#### 1. Creating *CREATE_TABLE.sql* file in database directory.
_*This file will create table in database at the first start of the database container.*_

**Path:** *you_project_dir/database/CREATE_TABLE.sql*

```sql
-- Create table.
create table if not exists numbers
(
    id     serial primary key,
    number int       default 0                 not null,
    ctime  timestamp default current_timestamp not null
);

create sequence numbers_seq
  start 1
  increment 1;

-- Creating Index for the id attribute in numbers table. 
create unique index numbers_idx on numbers (id);
```

_*After completing this step, you should have the following project structure:*_

    you_project_dir
        ├───app
        │    ├───main.py
        │    ├───config.py
        │    ├───requirements.txt
        │    └───Dockerfile
        └───database
                └───CREATE_TABLE.sql


### Step 3: Creating files for Docker Compose (DC)

#### 1. Creating environment *.env* file for DC.
_*This file used to create virtual environment variables in containers with an application and database.*_

**Path:** *you_project_dir/.env*

```
POSTGRES_USER=you_postgres_user_name
POSTGRES_PASSWORD=you_postgres_user_password
POSTGRES_DB=you_database_name
```

#### 1. Creating *docker-compose.yml* file.
_*This file describes our services, images and how the services interact with each other.*_

**Path:** *you_project_dir/docker-compose.yml*

```yaml
version: "3.8"

services:
# Database service name, we use this name in config.py in variable HOST.
  postgres_database:
#   Image version, we use latest version
    image: postgres:latest
#   File with virtual environment variables.
    env_file:
      - ./.env
#   Configuring ports and virtual networks.
    ports:
      - 5433:5432
    networks:
      - app-vnet
#   Using CREATE_TABLE.sql to create a table in database. 
#   When you first start the container.
    volumes:
      - ./database/:/docker-entrypoint-initdb.d

# Python app service name.
  app:
    env_file:
      - ./.env
#   Description of context for build Python app.
#   context - where take files
#   dockerfile - path to Docker file with context. (context + Dockerfile - ./app/Dockerfile)
    build:
      context: ./app
      dockerfile: ./Dockerfile
#   Associated container names.
    depends_on:
      - postgres_database
    networks:
      - app-vnet

# Description of virtual network.
networks:
  app-vnet:
    driver: bridge
```

_*After completing this step, you should have the following project structure:*_

    you_project_dir
        ├───app
        │    ├───main.py
        │    ├───config.py
        │    ├───requirements.txt
        │    └───Dockerfile
        ├───database
        │       └───CREATE_TABLE.sql
        ├───.env
        └───docker-compose.yml

### Step 4: Launching project 

#### 1. Start containers in “detached” mode.

```shell
$ docker-compose up -d
```

###### 1.1. If you need rebuild containers, run:

```shell
$ docker-compose build
```

###### 1.2. If you need stop containers, run:

```shell
$ docker-compose down
```

#### 2. Check launch containers:

```shell
$ docker ps
CONTAINER ID   IMAGE                              COMMAND                  CREATED         STATUS         PORTS                    NAMES
2776d5923fb9   tutorialdockerpythonpostgres_app   "python /app/main.py"    9 minutes ago   Up 9 minutes                            tutorialdockerpythonpostgres_app_1
28f40d5b6c1c   postgres:latest                    "docker-entrypoint.s…"   9 minutes ago   Up 9 minutes   0.0.0.0:5433->5432/tcp   tutorialdockerpythonpostgres_postgres_database_1

```
_*If you see the*_ **Up** _*status in*_ **State** _*column, then we have successfully launched application.*_

#### 3. Let's check what our app is doing in its container:

* To access the app container, run:
```shell
# My Python app container id, is 2776d5923fb9.
$ docker exec -it <docker_container_id> bash
```
* See what is in the directory:
```shell
$ ls -l
-rwxr-xr-x 1 root root  218 Oct 26 12:15 Dockerfile
drwxr-xr-x 1 root root 4096 Oct 27 12:21 __pycache__
-rwxr-xr-x 1 root root  252 Oct 26 11:55 config.py
-rwxr-xr-x 1 root root  925 Oct 27 10:24 main.py
-rw-r--r-- 1 root root  633 Oct 27 12:35 my_text.txt
-rwxr-xr-x 1 root root  124 Oct 26 08:27 requirements.txt
```
_*If we did everything correctly, then the file*_ **my_text.txt** _*appeared in the directory,then file was created by app.*_

* See what is in the file:
```shell
$ cat my_text.txt
456
23678
782
```
_*In the file, we see a set of numbers that the app wrote there.*_

*To close the session of connecting to the container, press:* **Ctrl+D**

#### 4. Let's check that the app interacts with the database correctly. 

* To access the database container, run:
```shell
# My database container id, is 28f40d5b6c1c.
$ docker exec -it <docker_container_id> bash
```
* To enter the database, run: 
```shell
$ psql -d you_database_name -U you_postgres_user_name
```
* To view existing tables, run:
```shell
you_database_name=# \dt
           List of relations
 Schema |  Name   | Type  |         Owner
--------+---------+-------+-----------------------
 public | numbers | table | you_postgres_user_name
(1 row)
```
_*We see a table that was created based on*_ **CREATE_TABLE.sql** _*file from Step 2.*_
* Now let's select the first 5 rows of our table:
```shell
you_database_name=# select * from numbers limit 5;
id | number |           ctime
----+--------+----------------------------
  1 |    164 | 2021-10-27 12:21:45.334411
  2 |    327 | 2021-10-27 12:21:50.420848
  3 |    479 | 2021-10-27 12:21:55.576793
  4 |    582 | 2021-10-27 12:22:00.649828
  5 |    862 | 2021-10-27 12:22:05.687282
```
_*We see that the application is working correctly.*_

*To close the session of connecting to the container, press:* **Ctrl+D**

### Useful links:

* [Docker Documentation](https://docs.docker.com/)
* [SQLAlchemy Engine Documentation](https://docs.sqlalchemy.org/en/13/core/connections.html)
* [Python: Virtual Environments and Packages](https://docs.python.org/3/tutorial/venv.html)