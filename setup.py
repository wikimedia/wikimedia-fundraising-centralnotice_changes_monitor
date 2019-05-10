from setuptools import setup

setup( name = 'centralnotice_changes_monitor',
    version  = '0.1',
    description = 'Provides a stream of changes in CentralNotice banners and settings,'
        'and allows configurable alerts.',
    license = 'GPL',
    packages = [ 'centralnotice_changes_monitor' ],
    install_requires = [
        'pywikibot >= 3.0',
        'mysql-connector-python >= 1.2.3'
    ]
)