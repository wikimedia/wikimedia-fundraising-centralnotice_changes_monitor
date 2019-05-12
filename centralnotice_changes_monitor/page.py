from enum import Enum


class PageStatus( Enum ):
    NEW = 'new'
    MONITORING = 'monitoring'
    REMOVED = 'removed'


class Page:
    def __init__( self, title, latest_revision = None, checked_revision = None ):
        self.title = title
        self.latest_revision = latest_revision
        self.checked_revision = checked_revision

        # These properties are set after the object has been created.
        self.status = None
        self.content_added = None
        self.content_removed = None


    def reset_checked_revision_and_changes( self, checked_revision ):
        self.checked_revision = checked_revision
        self.content_added = None
        self.content_removed = None