from couchdb import *
from couchdb.client import *

from modifiers import cache

COUCHDB_URL = 'http://campdoc:campdoc@localhost:5984/'

@cache
def get_server(url=COUCHDB_URL):
    return Server(url)
    
@cache
def get_db(db_name, server=get_server(), auto_create=True):
    try:
        return server[db_name]
    except ResourceNotFound:
        return server.create(db_name)

def truncate_db(db_name, server=get_server(), keep_design_docs=True):
    db = get_db(db_name, server)
    for doc in db:
        if not (keep_design_docs and doc.startswith('_')):
            del db[doc]
