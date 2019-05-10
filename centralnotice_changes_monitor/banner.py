from centralnotice_changes_monitor.page import Page

TITLE_PREFIX = 'MediaWiki:Centralnotice-template-'

class Banner( Page ):

    def __init__( self, name, latest_revision = None ):
        self.name = name
        super().__init__( TITLE_PREFIX + name, latest_revision )
