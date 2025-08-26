
# Library app

## Installation

#### Create virtual environment in the project root directory:

```Shell
$ python3.13 -m .venv .venv
```

#### Activate the virtual environment:

- ##### For Linux / Mac:

  ```Shell
  $ source .venv/bin/activate
  ```

- ##### For Windows:
  ```PowerShell
  $ .\.venv\Scripts\activate
  ```

#### Install the required packages:

```Shell
(.venv) $ pip install -r requirements.txt
```

## Running

##### [1] Set the environment variables:

Create a `.env` file in the project's root directory and add your 
environment variables to this file. See the [.env.example](.env.example)
file for the specific environment variables that need to be defined.

##### [2] Prepare the database:

Since the SQLite database file is stored in this Git repo, if you would like to
use a fresh new database, remove the file [db.sqlite3](db.sqlite3), 
and then run:

```Shell
(.venv) $ python manage.py makemigrations
(.venv) $ python manage.py migrate
(.venv) $ python manage.py createsuperuser
```

If you would like to use the existing database, you can optionally create your
own superuser:

```Shell
(.venv) $ python manage.py createsuperuser
```

Credentials for the existing superuser in the database:

- Username: `admin`
- Email: `tomas.giedraitis@yahoo.com`
- Password: `test`

Credentials for the existing users:

User of a `staff` group:

- Username: `darbuotojas`
- Email: `darbuotojas@example.com`
- Password: `rorosroros1`

User of a `reader` group:

- Username: `ruta_t`
- Email: `ruta_t@example.com`
- Password: `rorosroros1`
 
The password for all other users (clients) in the database is `rorosroros1`.

##### [3] Run the development server:

Finally, run the development server:

```Shell
(.venv) $ python manage.py runserver
```

## Software dependencies

[Django](https://www.djangoproject.com/) – the web framework for perfectionists
with deadlines. Django aims to follow Python’s
["batteries included" philosophy](https://docs.python.org/3/tutorial/stdlib.html#tut-batteries-included).
It ships with a variety of extra, optional tools that solve common web
development problems.

[Boostrap v5](https://getbootstrap.com/) - powerful, extensible, and
feature-packed frontend toolkit.

For the full list of software dependencies see
[requirements.txt](requirements.txt).

## Latest releases

**v0.1.0** (2025-07-01)

## API references

None

## [License](LICENSE)

The MIT License (MIT)

Copyright (c) 2025 Code Academy