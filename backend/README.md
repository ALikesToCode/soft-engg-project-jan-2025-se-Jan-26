# Starting the backend server
Assuming a Debian/linux environment

## Create virtual python environment
```
python -m venv .venv && . .venv/bin/activate
```
## Install requirements.txt

```
pip install -r requirements.txt
```

## Setup Postgres
```
user@debian:~$ sudo apt install postgresql
user@debian:~$ sudo -i -u postgres
postgres@debian:~$ psql

postgres=# ALTER USER postgres PASSWORD 'password_for_postgres_user';
postgres=# create database se_project_db;
postgres=# exit
```

## Start backend

```
unicorn main:app
```

Application should now be started on localhost.