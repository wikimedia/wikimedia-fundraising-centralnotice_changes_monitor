import mysql.connector as mariadb

from centralnotice_changes_monitor import db, wiki_api
from centralnotice_changes_monitor.page import Page, PageStatus
from centralnotice_changes_monitor.alert import Alert, AlertType


PAGES_TO_MONITOR = 'SELECT title, checked_revision FROM pages_to_monitor'

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

UPDATE_CHECKED_REVISION = (
    'UPDATE pages_to_monitor SET'
    '  checked_revision = %(revision)s '
    'WHERE '
    '  title = %(title)s'
)

REMOVE_PAGE_TO_MONITOR = 'DELETE FROM pages_to_monitor WHERE title = %s'


def pages_to_monitor( banners, transcluded_pages ):

    # Merge the lists ensuring only unique pages by title, since, in theory, a banner
    # could transclude another banner, so there could be separate objects for the same
    # actual page.
    pages_by_title = {}

    for page in ( banners + transcluded_pages ):
        pages_by_title[ page.title ] = page

    return list( pages_by_title.values() )


def set_latest_revisions( pages ):
    latest_revisions = wiki_api.latest_revisions( pages )
    for page in pages:
        page.latest_revision = latest_revisions[ page.title ]


def set_properties_from_db_and_get_removed( pages_to_monitor ):
    pages_to_monitor_by_title = { p.title : p for p in pages_to_monitor }
    removed_pages = []
    previously_monitoring_page_titles = []

    cursor = db.connection.cursor()
    cursor.execute( PAGES_TO_MONITOR )

    for ( title, checked_revision ) in cursor:
        previously_monitoring_page_titles.append( title )

        if title in pages_to_monitor_by_title:
            page = pages_to_monitor_by_title[ title ]
            page.checked_revision = checked_revision
            page.status = PageStatus.MONITORING

        else:
            page = Page( title, None, checked_revision )
            page.status = PageStatus.REMOVED
            removed_pages.append( page )

    for page in pages_to_monitor:
        if page.title not in previously_monitoring_page_titles:
            page.status = PageStatus.NEW

    cursor.close()

    return removed_pages


def set_changes( page ):
    """ Note: Before this function is called, the page's latest_revision and
    checked_revision properties must be set as appropriate for its status.
    """

    if page.status == PageStatus.NEW:
        page.content_added = wiki_api.content( page ).splitlines()
        page.content_removed = []

    elif page.status == PageStatus.MONITORING:
        page.content_added, page.content_removed = wiki_api.compare_latest( page )

    elif page.status == PageStatus.REMOVED:
        page.content_added = []
        page.content_removed = wiki_api.content( page ).splitlines()

    else:
        raise ValueError( 'Incorrect value for page.status: ' + page.status )


def get_alerts( page, alert_patterns ):
    alerts = []

    for ptn in alert_patterns:
        lines_and_matches_added = ptn.lines_and_matches_added( page.content_added )
        alerts += _make_alerts( page, ptn, lines_and_matches_added, AlertType.ADDED )

        lines_and_matches_removed = ptn.lines_and_matches_removed( page.content_removed )
        alerts += _make_alerts( page, ptn, lines_and_matches_removed, AlertType.REMOVED )

    return alerts


def update_page_after_alerts( page ):

    page.reset_checked_revision_and_changes( page.latest_revision )
    cursor = db.connection.cursor()

    if page.status == PageStatus.NEW:

        try:
            cursor.execute( INSERT_PAGE_TO_MONITOR, {
                'title': page.title,
                'revision': page.checked_revision
            } )

        except mariadb.Error as e:
            db.connection.rollback()
            cursor.close()
            raise e

        db.connection.commit()
        page.status = PageStatus.MONITORING

    elif page.status == PageStatus.MONITORING:

        try:
            cursor.execute( UPDATE_CHECKED_REVISION, {
                'revision': page.checked_revision,
                'title': page.title
            } )

        except mariadb.Error as e:
            db.connection.rollback()
            cursor.close()
            raise e

        db.connection.commit()

    elif page.status == PageStatus.REMOVED:

        try:
            cursor.execute( REMOVE_PAGE_TO_MONITOR, ( page.title, ) )

        except mariadb.Error as e:
            db.connection.rollback()
            cursor.close()
            raise e

        db.connection.commit()

    else:
        cursor.close()
        raise ValueError( 'Incorrect value for page.status: ' + page.status )

    cursor.close()


def _make_alerts( page, ptn, lines_and_matches, alert_type ):
    alerts = []
    for line_and_matches in lines_and_matches:
        line = line_and_matches[0]
        for m in line_and_matches[1]:
            alerts.append( Alert( ptn.name, page.title, page.latest_revision,
                alert_type, line, m ) )
    
    return alerts
