import pprint

from kafka import KafkaConsumer


_PAGE_EDIT_TOPIC = 'mediawiki.recentchange'

_PAGE_MOVE_TOPIC = 'mediawiki.page-move'

_PAGE_DELETE_TOPIC = 'mediawiki.page-delete'

_CN_CAMPAIGN_CHANGE_TOPICS = [
    'mediawiki.centralnotice.campaign-create',
    'mediawiki.centralnotice.campaign-change',
    'mediawiki.centralnotice.campaign-delete'
]


def consume( event_queue, update_pages_to_monitor_queue, kafka_settings ):
    topics = ( [ _PAGE_EDIT_TOPIC, _PAGE_MOVE_TOPIC, _PAGE_DELETE_TOPIC ] +
        _CN_CAMPAIGN_CHANGE_TOPICS )

    topics_w_datacenter = [ kafka_settings[ 'datacenter' ] + '.' + t for t in topics ]

    consumer = KafkaConsumer(
        *topics_w_datacenter,
        bootstrap_servers = kafka_settings[ 'hosts' ],
        client_id = 'centralnotice_changes_monitor',
        auto_offset_reset = 'latest',
        enable_auto_commit = False
    )

    for message in consumer:
        pprint.pprint( message.value )
