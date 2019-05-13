from centralnotice_changes_monitor import wiki_api
from centralnotice_changes_monitor.banner import Banner, Page


def from_campaigns( campaigns ):
    banner_names = set()

    for campaign in campaigns:
        for banner_name in campaign.banner_names:
            banner_names.add( banner_name )

    # We don't yet know the latest revision for each banner. Create the objects
    # without that info for now.
    return [ Banner( banner_name ) for banner_name in banner_names ]


def transcluded_pages( banners ):
    pages_raw = wiki_api.transclusions( banners )
    return[ Page( title, latest_revsion ) for title, latest_revsion in pages_raw.items() ]