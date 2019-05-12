import logging

from centralnotice_changes_monitor import ( wiki_api, db, campaign_manager, banner_manager,
    page_monitor )

from centralnotice_changes_monitor.alert_pattern import AlertPattern

_logger = logging.getLogger( __name__ )


def stream_changes( wiki_api_settings, db_settings, alert_pattern_settings ):
    _logger.debug( 'Fetching camapigns' )

    # Before pywikibot is imported for the first time, we need to set the environment
    # variable that points to its configuration file. We'll also set up which wiki
    # to query here.
    wiki_api.init( **( wiki_api_settings or {} ) )

    # Open db connection
    db.connect( **db_settings )

    # Create alert pattern objects
    alert_patterns = [ AlertPattern( **settings ) for settings in alert_pattern_settings ]

    # Start and connect campaign changes monitor and content monitor but on hold

    # Get initial state of campaigns and banners and list of pages to monitor
    campaigns = campaign_manager.campaigns()
    banners = banner_manager.from_campaigns( campaigns )
    transcluded_pages = banner_manager.transcluded_pages( banners )
    pages_to_monitor = page_monitor.pages_to_monitor( banners, transcluded_pages )

    # Unlike transcluded pages, we don't get banners' latest revision when the objects
    # are created, so we fetch that data separately.
    banner_manager.set_latest_revisions( banners )

    # Find and set pages' status and last revision checked and get a list of removed
    # pages from the db.
    removed_pages = page_monitor.set_properties_from_db_and_get_removed( pages_to_monitor )

    # Check for alerts on changes on both current and past pages to monitor
    for page in pages_to_monitor + removed_pages:
        page_monitor.set_changes( page )
        alerts = page_monitor.get_alerts( page, alert_patterns )

        # Output alerts
        for alert in alerts:
            _logger.warn( alert.output() )

        page_monitor.update_page_after_alerts( page )

    db.close()

    return 'Resultsies'
