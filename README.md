`centralnotice_changes_monitor`
=================================

Use configurable alerts to monitor changes to banners and transcluded pages associated
with active and upcoming CentralNotice campaigns.

# Usage

Copy `config-example.yaml` to `config.yaml` and adjust settings as appropriate.
The script looks for a configuration file in the working directory or in
`/etc/centralnotice_changes_monitor`.

Run with the --help flag for help with command-line options.


# Database

Required tables can be created by executing the SQL in `sql/create_tables.sql`.


# Developer setup

For details on how to set up an environment for testing and development, please see
https://www.mediawiki.org/wiki/User:AGreen_(WMF)/Draft:Dev_setup_for_centralnotice_changes_monitor