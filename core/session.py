import os
import dropbox
from core.out import *


class Session(object):
    def __init__(self):
        # This will be assigned with the File object of the file currently
        # being analyzed.
        self.token = None
        # This is not being used yet.
        self.plugin = None
        # Dropbox session
        self.dbx = None
        # Local dir
        self.ldir = os.getcwd()
        # Remote dir
        self.rdir = ''

    def clear(self):
        # Reset session attributes.
        self.plugin = None
        self.token = None
        self.dbs = None
        self.ldir = None

    def is_set(self):
        # Check if the session has been opened or not.
        if self.token and self.dbx:
            return True
        else:
            return False

    def set_token(self, token):
        # Open a session
        self.token = token
        print_info("Token set as: {0}".format(token))
        self.dbx = dropbox.Dropbox(self.token)

__session__ = Session()
