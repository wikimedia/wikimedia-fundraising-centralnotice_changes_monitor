from enum import Enum


class AlertType( Enum ):
    ADDED = 'added'
    REMOVED = 'removed'


class Alert:
    def __init__( self, pattern_name, page_title, alert_type, line, match, change = None):
        self.pattern_name = pattern_name
        self.page_title = page_title
        self.alert_type = alert_type
        self.line = line
        self.match = match

        # Change data may not be available if diff from changes between the prevoius
        # and current execution of this script.
        self.change = change


    def output( self ):
        # TODO include change metadata
        return '{} for page {}, {} on line {}'.format(
            self.pattern_name,
            self.page_title,
            self.alert_type,
            self.line
        )