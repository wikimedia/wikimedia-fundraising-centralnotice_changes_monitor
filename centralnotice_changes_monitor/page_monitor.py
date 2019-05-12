from centralnotice_changes_monitor import db, wiki_api
from centralnotice_changes_monitor.banner import Page
from centralnotice_changes_monitor.alert import Alert, AlertType

PAGES_TO_MONITOR = 'SELECT title, checked_revision FROM pages_to_monitor'

REMOVE_PAGE_TO_MONITOR = 'DELETE FROM pages_to_monitor WHERE title = %s'

UPDATE_CHECKED_REVISION = (
    'UPDATE pages_to_monitor SET'
    '  checked_revision = %(revision)s'
    'WHERE '
    '  title = %(title)s'
)

INSERT_PAGE_TO_MONITOR = (
    'INSERT INTO pages_to_monitor ('
    '  title,'
    '  checked_revision'
    ') '
    'VALUES ('
    '  %(title)s,'
    '  %(revision)s'
    ')'
)


def pages_to_monitor( banners, transcluded_pages ):

    # Merge the lists ensuring only unique pages by title, since, in theory, a banner
    # could transclude another banner, so there could be separate objects for the same
    # actual page.
    pages_by_title = {}

    for page in ( banners + transcluded_pages ):
        pages_by_title[ page.title ] = page

    return list( pages_by_title.values() )


def set_checked_revision_and_get_removed( pages_to_monitor ):
    pages_to_monitor_by_title = { p.title : p for p in pages_to_monitor }
    removed_pages = []

    cursor = db.connection.cursor()
    cursor.execute( PAGES_TO_MONITOR )

    for ( title, checked_revision ) in cursor:
        if title in pages_to_monitor_by_title:
            pages_to_monitor_by_title[ title ].prev_checked_revision = checked_revision
        else:
            removed_pages.append( Page( title, None, checked_revision ) )

    cursor.close()

    return removed_pages


def set_changes( pages ):
    for page in pages:
        if page.prev_checked_revision is None:
            page.content_added = wiki_api.content( page ).splitlines()
            page.content_removed = []

        elif page.latest_revision is None:
            page.content_added = wiki_api.content( page ).splitlines()
            page.content_removed = []

        elif ( page.prev_checked_revision is not None ) and ( page.latest_revision is not None ):
            page.content_added, page.content_removed = wiki_api.compare_latest( page )

        else:
            raise ValueError( 'checked_revision and latest_revision are both None' )


def get_alerts_and_update_pages( pages, alert_patterns ):
    alerts = []

    for page in pages:
        for ptn in alert_patterns:
            lines_and_matches_added = ptn.lines_and_matches_added( page.content_added )
            alerts += _make_alerts( page, ptn, lines_and_matches_added, AlertType.ADDED )

            lines_and_matches_removed = ptn.lines_and_matches_removed( page.content_removed )
            alerts += _make_alerts( page, ptn, lines_and_matches_removed, AlertType.REMOVED )

    return alerts


def _make_alerts( page, ptn, lines_and_matches, alert_type ):
    alerts = []
    for line_and_matches in lines_and_matches:
        line = line_and_matches[0]
        for m in line_and_matches[1]:
            alerts.append( Alert( ptn.name, page.title, page.latest_revision, 
                alert_type, line, m ) )
    
    return alerts
