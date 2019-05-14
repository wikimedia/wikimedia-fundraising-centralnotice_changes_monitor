import json
import logging
from kafka import KafkaConsumer

from centralnotice_changes_monitor import ( wiki_api, db, campaign_manager, banner_manager,
    page_manager )

from centralnotice_changes_monitor.alert_pattern import AlertPattern

_PAGE_EDIT_TOPIC = 'mediawiki.recentchange'

_UPDATE_PAGES_TO_MONITOR_TOPICS = [
    'mediawiki.page-move',
    'mediawiki.page-delete',
    'mediawiki.centralnotice.campaign-create',
    'mediawiki.centralnotice.campaign-change',
    'mediawiki.centralnotice.campaign-delete'
]

_logger = logging.getLogger( __name__ )


def monitor( db_settings, wiki_api_settings, kafka_settings, alert_pattern_settings ):

    # Before pywikibot is imported for the first time, we need to set the environment
    # variable that points to its configuration file. We'll also set up which wiki
    # to query here.
    wiki_api.init( **( wiki_api_settings or {} ) )

    # Connect to Kafka right away in the hope that we won't miss any events between the
    # initial setup of stuff to monitor and when we're ready to consume from Kafka.
    _logger.info( 'Starting KafkaConsumer' )
    kafka_consumer = _kafka_consumer( kafka_settings )

    # Open db connection
    db.connect( **db_settings )

    # Since the script shouldn't stop running unless interrupted or there's an error,
    # ensure that in those cases we close the db connection.
    try:
        # Create alert pattern objects
        alert_patterns = [ AlertPattern( **settings ) for settings in alert_pattern_settings ]

        _logger.info( 'Initial fetch and check of pages to monitor' )
        pages_to_monitor = _update_pages_to_monitor_and_emit_alerts( alert_patterns )

        # Consume messages from the queue. This loop shouldn't exit except on error.
        for message in kafka_consumer:
            try:
                event = json.loads( message.value )

            except json.JSONDecodeError:
                _logger.info( 'Couldn\t decode message from Kafka stream: ' + message.value )
                continue

            topic = event[ 'meta' ][ 'topic' ]

            if topic == _PAGE_EDIT_TOPIC:
                title = event[ 'title' ]

                if title in pages_to_monitor.keys():
                    _logger.info( 'Checking alerts following change to ' + title )

                    pages_to_monitor = (
                        _update_pages_to_monitor_and_emit_alerts( alert_patterns ) )

            else:
                _logger.info( 'Checking alerts following event: ' + topic )
                pages_to_monitor = _update_pages_to_monitor_and_emit_alerts( alert_patterns )

    finally:
        db.close()



def _kafka_consumer( kafka_settings ):
    topics = ( [ _PAGE_EDIT_TOPIC ] + _UPDATE_PAGES_TO_MONITOR_TOPICS )

    # Tópic names sent to Kafka must include datacenter
    topics_w_datacenter = [ kafka_settings[ 'datacenter' ] + '.' + t for t in topics ]

    consumer = KafkaConsumer(
        *topics_w_datacenter,
        bootstrap_servers = kafka_settings[ 'hosts' ],
        client_id = 'centralnotice_changes_monitor',
        auto_offset_reset = 'latest',
        enable_auto_commit = False
    )

    return consumer


def _update_pages_to_monitor_and_emit_alerts( alert_patterns ):
    # Get state of campaigns and banners and list of pages to monitor
    campaigns = campaign_manager.campaigns()
    banners = banner_manager.from_campaigns( campaigns )
    transcluded_pages = banner_manager.transcluded_pages( banners )
    pages_to_monitor = page_manager.pages_to_monitor( banners, transcluded_pages )

    # Unlike transcluded pages, we don't get banners' latest revision when the objects
    # are created, so we fetch that data separately.
    page_manager.set_latest_revisions( banners )

    # Find and set pages' revision checked and status properties with regard to state stored
    # in the db, and get a list of pages no longer in monitoring.
    removed_pages = page_manager.set_properties_from_db_and_get_removed( pages_to_monitor )

    # Check for alerts looking at changes in pages to monitor and removed pages
    for page in pages_to_monitor + removed_pages:
        _check_patterns_emit_alerts_and_update_page( page, alert_patterns )

    return { p.title : p for p in pages_to_monitor }


def _check_patterns_emit_alerts_and_update_page( page, alert_patterns ):
    page_manager.set_changes( page )
    alerts = page_manager.get_alerts( page, alert_patterns )

    # Output alerts
    for alert in alerts:
        print( alert.output() )

    page_manager.update_page_after_alerts( page )
