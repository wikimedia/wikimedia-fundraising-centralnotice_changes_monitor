from centralnotice_changes_monitor import wiki_api
from centralnotice_changes_monitor.campaign import Campaign


def campaigns():
    campaigns_raw = wiki_api.active_and_future_campaigns()

    campaigns= []
    for campaign_raw in campaigns_raw:
        campaign = Campaign(
            campaign_raw[ 'name' ],
            campaign_raw[ 'start' ],
            campaign_raw[ 'end' ],
            campaign_raw[ 'banners' ]
        )

        campaigns.append( campaign )

    return campaigns
