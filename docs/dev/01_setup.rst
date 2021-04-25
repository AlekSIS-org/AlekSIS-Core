Setting up the development environment
======================================

AlekSIS and all official apps use `Poetry`_ to manage virtualenvs and
dependencies. You should make yourself a bit confortable with poetry
by reading its documentation.

Poetry makes a lot of stuff very easy, especially managing a virtual
environment that contains AlekSIS and everything you need to run the
framework and selected apps.

Also, `Yarn`_ is needed to resolve JavaScript dependencies.

Get the source tree
-------------------

To download AlekSIS and all officially bundled apps in their
development version, use Git like so::

  git clone --recurse-submodules https://edugit.org/AlekSIS/AlekSIS

If you do not want to download the bundled apps, leave out the
``--recurse-submodules`` option.


Install native dependencies
---------------------------

Some system libraries are required to install AlekSIS::

  sudo apt install build-essential libpq-dev libpq5 libssl-dev python3-dev python3-pip python3-venv yarnpkg gettext chromium

Get Poetry
----------

Make sure to have Poetry installed like described in its
documentation. Right now, we encourage using pip to install Poetry
once system-wide (this will change once distributions pick up
Poetry). On Debian, for example, this would be done with::

  sudo pip3 install poetry

You can use any other of the `Poetry installation methods`_.


Install AlekSIS in its own virtual environment
----------------------------------------------

Poetry will automatically manage virtual environments per project, so
installing AlekSIS is a matter of::

  poetry install


Regular tasks
-------------

After making changes to the environment, e.g. installing apps or updates,
some maintenance tasks need to be done:

1. Download and install JavaScript dependencies
2. Collect static files
3. Run database migrations

All three steps can be done with the ``poetry run`` command and
``manage.py``::

  poetry run ./manage.py yarn install
  poetry run ./manage.py collectstatic
  poetry run ./manage.py compilemessages
  poetry run ./manage.py migrate
  poetry run ./manage.py createinitialrevisions

(You might need database settings for the `migrate` command; see below.)

Running the development server
------------------------------

The development server can be started using Django's ``runserver`` command.
If you want to automatically start other necessary tools in development,
like the `Celery` worker and scheduler, use ``runuwsgi`` instead.
You can either configure AlekSIS like in a production environment, or pass
basic settings in as environment variable. Here is an example that runs the
development server against a local PostgreSQL database with password
`aleksis` (all else remains default) and with the `debug` setting enabled::

  ALEKSIS_debug=true ALEKSIS_database__password=aleksis poetry run ./manage.py runuwsgi

.. figure:: /screenshots/index.png
   :scale: 50%
   :alt: Screenshot of index page

   After installing the development environment with default settings,
   you should see the index page with the Bootstrap style.

.. _Poetry: https://poetry.eustace.io/
.. _Poetry installation methods: https://poetry.eustace.io/docs/#installation
.. _Yarn: https://yarnpkg.com
.. _Celery: https://celeryproject.org/
