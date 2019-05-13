import logging
DEFAULT_CONFIG_FILENAMES = [ './config.yaml', '/etc/centralnotice_changes_monitor/config.yaml' ]

LOG_FORMAT = '{levelname} {msg} ({filename} line {lineno})'


def setup_logging( debug ):
    logging.basicConfig( format = LOG_FORMAT, style = '{' )

    if debug:
        logging.root.setLevel( level = logging.INFO )
    else:
        logging.root.setLevel( level = logging.WARNING )
