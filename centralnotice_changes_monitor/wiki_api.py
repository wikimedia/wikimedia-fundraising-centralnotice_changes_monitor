import os

import logging

_logger = logging.getLogger( __name__ )

_site = None

def init( host = None, scriptpath = None ):
    global _site

    # This must be set before we use pywikibot
    os.environ[ 'PYWIKIBOT2_DIR' ] = '.'
    from pywikibot import Site

    if ( host ):
        from pywikibot.family import SingleSiteFamily

        class ConfigurableFamily( SingleSiteFamily ):

            name = 'configurable'
            domain = host

            def protocol(self, code ):
                return 'http'
 
            def scriptpath( self, code ):
                return scriptpath or super().scriptpath( code )

        _site = Site( code = 'configurable', fam = ConfigurableFamily() )

    else:
        _site = Site( code = 'configurable', fam = 'meta' )


def active_and_future_campaigns():
    from pywikibot.data.api import Request
    from pywikibot import Timestamp

    parameters = {
        'action': 'query',
        'list': 'centralnoticeactivecampaigns',
        'cnacincludefuture': ''
    }

    request = Request( _site, parameters = parameters )

    # TODO Error handling
    raw_query_data = request.submit()
    raw_campaigns = (
        raw_query_data[ 'query' ][ 'centralnoticeactivecampaigns' ][ 'campaigns' ] )

    # Convert start and end to datetime objects
    for c in raw_campaigns:
        c[ 'start' ] = Timestamp.fromtimestampformat( c[ 'start'] )
        c[ 'end' ] = Timestamp.fromtimestampformat( c[ 'end'] )

    return raw_campaigns


def latest_revisions( pages ):
    from pywikibot.data.api import Request

    parameters = {
        'action': 'query',
        'prop': 'revisions',
        'rvprop': 'ids',
        'titles': '|'.join( [ p.title for p in pages ] )
    }

    # Use POST in case the list of titles would cause a very long URL for GET
    request = Request( _site, use_get = False, parameters = parameters )

    # TODO Error handling
    raw_query_data = request.submit()

    return _title_and_revision_dict( raw_query_data )


def transclusions( pages ):
    from pywikibot.data.api import Request

    parameters = {
        'action': 'query',
        'generator': 'templates',
        'prop': 'revisions',
        'titles': '|'.join( [ p.title for p in pages ] )
    }

    # Use POST in case the list of titles would cause a very long URL for GET
    request = Request( _site, use_get = False, parameters = parameters )

    # TODO Error handling
    raw_query_data = request.submit()

    return _title_and_revision_dict( raw_query_data )


def compare_latest( page ):
    from pywikibot import diff

    html_diff = _site.compare( page.checked_revision, page.latest_revision )
    changes = diff.html_comparator( html_diff )
    return changes[ 'added-context' ], changes[ 'deleted-context' ]


def content( page ):
    import pywikibot
    return pywikibot.Page( _site, page.title ).text


def _title_and_revision_dict( raw_query_data ):
    # Traverse the API results data structure
    raw_pages = raw_query_data[ 'query' ][ 'pages' ].values()

    # Return a dictionary where keys are titles and values are the latest revision
    return { p[ 'title' ] : p[ 'revisions' ][ 0 ][ 'revid' ] for p in raw_pages }
