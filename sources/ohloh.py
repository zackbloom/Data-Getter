from base import *
import sys
from utils.logger import logger, get_structure
from utils.xml_api import fix_single_elems

START_PAGE = 3180
if len(sys.argv) > 1:
    START_PAGE = int(sys.argv[1])

class OhlohNormalizer(LoaderElement):
    def normalize_metadata(self, data):
        data = fix_single_elems(data)
        logger.info('Original Structure:\n%s' % get_structure(data))
        return {}, [data['result']['project']]

class OhlohLoader(PaginatedURLGetter, XMLParser, CouchDBStorer, OhlohNormalizer, Loader):
    def __init__(self):
        PaginatedURLGetter.__init__(self, 
            'https://ohloh.net/p/%d.xml?api_key=eLb1oDU6eRE5Hdr6XNnNAg', 
            num_pages=1000, start_page=START_PAGE)
        CouchDBStorer.__init__(self, 'ohloh_data', truncate=False)

if __name__ == '__main__':
    loader = OhlohLoader()
    loader.run()
