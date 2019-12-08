Authenticating against LDAP
===========================

BiscuIT can authenticate users against an LDAP directory (like OpenLDAP or
Active Directory). The BiscuIT core can only authenticate and synchronise
authenticated users to BiscuIT's database. There are apps that help with
tasks like mass-importing accounts and linking accounts to persons in
the BiscuIY system (see below).


Installing packages for LDAP support
------------------------------------

Installing the necessary librairies for LDAP support unfortunately is not
very straightforward under all circumstances.

TBA.


Configuration of LDAP support
-----------------------------

Configuration is done under the `default.ldap` section in BiscuIT's
configuration file. For example, add something like the following to your
configuration (normally in `/etc/biscuit`; you can either append to an
existing file or add a new one)::

  [default.ldap]
  uri = "ldaps://ldap.myschool.edu"
  bind = { dn = "cn=reader,dc=myschool,dc=edu", password = "secret" }
  users = { base = "ou=people,dc=myschool,dc=edu", filter = "(uid=%(user)s)" }
  map = { first_name = "givenName", last_name = "sn", email = "mail" }