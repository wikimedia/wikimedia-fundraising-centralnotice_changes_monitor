`centralnotice_changes_monitor`
=================================

Provides a stream of changes in CentralNotice banners and settings, and allows configurable
alerts.

Usage
-----

Copy `config-example.yaml` to `config.yaml` and adjust settings as appropriate.
The script looks for a configuration file in the working directory or in
`/etc/centralnotice_changes_monitor`.

TODO: How to run as deamon


Database
--------

Required tables can be created by executing the SQL in `sql/create_tables.sql`.

For developer setup, create a database and a database user, grant the user rights on
the database, then run the following command (substituting database, user and password
as appropriate):

`mariadb -u cn_changes_monitor --password=cn_changes_monitor_pw cn_changes_monitor < sql/create_tables.sql`

For development purposes, the SQL to drop all tables is also provided. To use it, copy
`sql/drop_tables_example.sql` as `sql/drop_tables.sql` and uncomment the last two
two lines.

Then, you can reset the database like this:

`cat sql/drop_tables.sql sql/create_tables.sql | mariadb -u cn_changes_monitor --password=cn_changes_monitor_pw cn_changes_monitor`

(Do not deploy an uncommented version of the drop tables file to production. Using the
filename `sql/drop_tables.sql` for the uncommented version will prevent it from being
added to the Git repository.)

Installation
------------

For development, try this command (from the repository root directory):

`pip3 install -e .`
