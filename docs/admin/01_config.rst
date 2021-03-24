Configuration files and format
==============================

File locations and order
------------------------

AlekSIS is configured through text files in the directory `/etc/aleksis/`.
You can place any file types there that are supported by the `Dynaconf`_
configuration system (INI, YAML and TOML).

Files are evaluated in alphabetical order, with later definitions
overwriting earlier ones. Normally, there will be only one configuration
file, but you can make up any structure you like. If you use multiple
files, it might be a good idea to number them, e.g. `00_main.toml`,
`01_myschool.toml`, `99_temporary.toml`.

The TOML format is recommended and is the only format described in detail in
AlekSIS’ documentation. For all other formats, refer to the `Dynaconf`_
documentation.

Configuration file format (TOML)
--------------------------------

TOML file are simple text files that define variables, much like in Python
(i.e. there are scalars, lists and dictionaries). AlekSIS structures its
configuration by topic.

A configuration file might look like this::

  secret_key = "VerySecretKeyForSessionSecurity"

  [http]
  allowed_hosts = [ "aleksis.myschool.example.com", "localhost" ]

  [database]
  name = "aleksis"
  user = "aleksis"
  password = "SuperSecretPassword"

  [caching]
  redis = { enabled = true, address = "127.0.0.1" }

The `secret_key` setting above defines a single value. The following `http`
section defines a table (cf. a dictionary) in one way, and you can see the
second form of such a table in the `redis` setting (we could as well
have defined another section and placed `enabled` and `address` below it
as scalars).

This can be a bit confusing, so this documentation will explain how to
configure AlekSIS on a per-feature basis.

.. _Dynaconf: https://dynaconf.readthedocs.io/en/latest/
