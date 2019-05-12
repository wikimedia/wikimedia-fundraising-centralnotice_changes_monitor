from enum import Enum


class AlertType( Enum ):
    ADDED = 'added'
    REMOVED = 'removed'


class Alert:
    def __init__( self, pattern_name, page_title, page_revision, alert_type, line, match,
        change = None ):
        self.pattern_name = pattern_name
        self.page_revision = page_revision
        self.page_title = page_title
        self.alert_type = alert_type
        self.line = line
        self.match = match

        # Change data may not be available if diff from changes between the prevoius
        # and current execution of this script.
        self.change = change


    def output( self ):
        # TODO include change metadata
        return '**{}** {} (rev. {}). Match: \'{}\'. Line {}: \'{}\''.format(
            self.pattern_name,
            self.page_title,
            self.page_revision,
            self.match,
            self.alert_type.value,
            self.line
        )