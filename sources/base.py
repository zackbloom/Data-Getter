import urllib
import json
import sys

from utils import couchdb_api, modifiers, xml_api
from utils.logger import logger

class LoaderElement(object):
    __metaclass__ = modifiers.OptionallyRequireInit
    
class DummyGetter(LoaderElement):
    def get(self):
        """
        Obtains data as a string.
        """
        return ""

    def iter_get(self):
        return [self.get()]
        
class DummyParser(LoaderElement):
    def parse(self, data_str):
        """
        Accepts a string-representation of data.
        Returns a python object also representing that data.
        """
        return data_str
        
class DummyNormalizer(LoaderElement):
    def normalize_record(self, record):
        """
        Accepts a single record of a source-specific format.
        Normalizes the data for storage, returning a dict or similar object which
        follows the item-access interface and implements the iteritems method.
        """
        return record

    def normalize_metadata(self, data):
        """
        Accepts the entire parsed data object.
        Normalizes the metadata returning it, and the unparsed data records.
        """
        return {}, data

    def normalize(self, data):
        metadata, record_data = self.normalize_metadata(data)
        records = [self.normalize_record(r) for r in record_data]

        return metadata, records
        
class DummyStorer(LoaderElement):
    def store(self, data):
        """
        Expects a list of dicts containing records.
        Stores the provided data.
        """
        return data
        
class Loader(DummyGetter, DummyParser, DummyNormalizer, DummyStorer):
    """
    A basic loader.  Subclasses are expected to overload one or more of the
    dummy methods provided.
    """
    def run(self, stop_on_failure=False):
        fail_cnt = 0
        metadata = None
        getter = self.iter_get()
        try:
            while True:
                try:
                    # Some getters require metadata from the last response to figure out the
                    # pagination of the next one
                    data_str = getter.send(metadata)
                    logger.debug('Got: %s' % data_str)
                    logger.info('Got records')

                    data = self.parse(data_str)
                    logger.debug('Parsed into: %s' % str(data))

                    metadata, records = self.normalize(data)
                    logger.debug('Normalized: \nMetadata: %s \nRecords: %s' % \
                        (str(metadata), str(records)))
                    logger.info('Normalized %d records' % len(records))

                    logger.info('Storing')
                    self.store(metadata, records)
                except Exception, e:
                    if isinstance(e, StopIteration):
                        raise

                    if stop_on_failure or fail_cnt > 100:
                        raise
                    else:
                        fail_cnt += 1
                        sys.stderr.write("Failed: %s" % str(e))
                        continue
        except StopIteration:
            pass

class BasicURLGetter(LoaderElement):
    def __init__(self, url):
        self.url = url
        
    def get(self, data=None):
        return self._get(self.url)

    def _get(self, url):
        page = urllib.urlopen(url)
        return page.read()

    def iter_get(self, data=None):
        return [self.get()]

class PaginatedURLGetter(BasicURLGetter):
    _require_init = True

    def __init__(self, url_template, num_pages=5, start_page=0):
        self.url_template = url_template
        self.num_pages = num_pages
        self.start_page = start_page
        self.current_page = start_page - 1

    def get(self):
        return list(self.iter_get())

    def iter_get(self, initial=None):
        res = initial
        try:
            while True:
                res = yield self.next_get(res)
        except StopIteration:
            pass

    def _next_get(self, data=None):
        return self.url_template % self.current_page

    def next_get(self, data=None):
        self.current_page += 1
        if self.current_page >= (self.num_pages + self.start_page):
            raise StopIteration()

        url = self._next_get(data)
        return BasicURLGetter._get(self, url)

class PageKeyedURLGetter(PaginatedURLGetter):
    _require_init = True

    def __init__(self, url_template, var_getter, num_pages=5):
        PaginatedURLGetter.__init__(self, url_template, num_pages)

        self.var_getter = var_getter

    def get(self):
        raise NotImplemented("This getter requires info about the last request to load the next, use next_get")

    def _next_get(self, data=None):
        return self.url_template % self.var_getter(data)

class JSONParser(LoaderElement):
    def parse(self, data_str):
        return json.loads(data_str)
    
class XMLParser(LoaderElement):
    def parse(self, data_str):
        return xml_api.xmltodict(data_str)

class CouchDBStorer(LoaderElement):
    _require_init = True

    def __init__(self, db_name, server=couchdb_api.get_server(), truncate=False):
        self.db = couchdb_api.get_db(db_name, server)
        if truncate:
            couchdb_api.truncate_db(db_name, server)
        
    def store(self, metadata, records):
        [r.update(metadata) for r in records]
        self.db.update(records)
        
if __name__ == '__main__':
    import unittest
    from zlib import adler32
    
    class URLGetterTester(unittest.TestCase):
        def test(self):
            getter = BasicURLGetter('http://www.example.com')
            page = getter.get()
            
            # We use the hash to avoid having to include the full page in the test
            hash = adler32(page)
            self.assertEqual(hash, 1899871367) 
            
    class JSONParserTester(unittest.TestCase):
        def test(self):
            parser = JSONParser()
            output = parser.parse('{"a": 1}')
            
            self.assertEqual(output, {'a': 1})
            
    unittest.main()
