import re


def _lines_and_matches( compiled_re, content ):
    return [ ( line, compiled_re.findall( line ) ) for line in content ]


class AlertPattern:
    def __init__( self, name, added, removed ):
        self.name = name
        self.added_re = re.compile( added )
        self.removed_re = re.compile( removed )


    def lines_and_matches_added( self, content_added ):
        return _lines_and_matches( self.added_re, content_added )


    def lines_and_matches_removed( self, content_removed ):
        return _lines_and_matches( self.removed_re, content_removed )
