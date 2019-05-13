import logging
from queue import Queue
from threading import Thread

from centralnotice_changes_monitor import ( wiki_api, db, campaign_manager, banner_manager,
    page_manager, kafka_consumer )

from centralnotice_changes_monitor.alert_pattern import AlertPattern

_logger = logging.getLogger( __name__ )


def stream_changes( db_settings, wiki_api_settings, kafka_settings, alert_pattern_settings,
    max_queue_size ):
    _logger.debug( 'Fetching camapigns' )

    # Before pywikibot is imported for the first time, we need to set the environment
    # variable that points to its configuration file. We'll also set up which wiki
    # to query here.
    wiki_api.init( **( wiki_api_settings or {} ) )

    # Open db connection
    db.connect( **db_settings )

    # Create alert pattern objects
    alert_patterns = [ AlertPattern( **settings ) for settings in alert_pattern_settings ]

    # Queue for events that trigger the controller to update the pages to monitor
    event_queue = Queue( max_queue_size )

    # Queue to send new lists of pages to monitor to the kafka consumer
    update_pages_to_monitor_queue = Queue( max_queue_size )

    # Start and connect kafka consumer
    kafka_consumer_thread = Thread(
        target = kafka_consumer.consume,
        args = ( event_queue, update_pages_to_monitor_queue, kafka_settings ),
        daemon = True
    )

    kafka_consumer_thread.start()

    # Get initial state of campaigns and banners and list of pages to monitor
    campaigns = campaign_manager.campaigns()
    banners = banner_manager.from_campaigns( campaigns )
    transcluded_pages = banner_manager.transcluded_pages( banners )
    pages_to_monitor = page_manager.pages_to_monitor( banners, transcluded_pages )

    # Unlike transcluded pages, we don't get banners' latest revision when the objects
    # are created, so we fetch that data separately.
    banner_manager.set_latest_revisions( banners )

    # Find and set pages' revision checked and status properties with regard to state stored
    # in the db, and get a list of pages no longer in monitoring.
    removed_pages = page_manager.set_properties_from_db_and_get_removed( pages_to_monitor )

    # Check for alerts looking at changes in pages to monitor and removed pages
    for page in pages_to_monitor + removed_pages:
        page_manager.set_changes( page )
        alerts = page_manager.get_alerts( page, alert_patterns )

        # Output alerts
        for alert in alerts:
            print( alert.output() )

        page_manager.update_page_after_alerts( page )


    while True:
        pass

    db.close()

    return 'Resultsies'
