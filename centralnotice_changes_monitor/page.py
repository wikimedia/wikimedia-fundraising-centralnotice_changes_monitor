class Page:
    def __init__( self, title, latest_revision = None, prev_checked_revision = None ):
        self.title = title
        self.latest_revision = latest_revision
        self.prev_checked_revision = prev_checked_revision

        self.content_added = None
        self.content_removed = None