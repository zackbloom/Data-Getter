from base import *
from utils.logger import logger, get_structure

class RedditNormalizer(LoaderElement):
    def normalize_metadata(self, data):
        logger.info('Original Structure:\n%s' % get_structure(data))

        records = [d['data'] for d in data['data']['children']]
        return {'after': data['data']['after']}, records

def reddit_pager(metadata=None):
    if metadata:
        return metadata['after']
    else:
        return 't3_e5qtt'
        
class ProggitLoader(PageKeyedURLGetter, JSONParser, CouchDBStorer, RedditNormalizer, Loader):
    def __init__(self):
        PageKeyedURLGetter.__init__(self, 
            'http://api.reddit.com/r/programming?after=%s', 
            reddit_pager, num_pages=400)
        CouchDBStorer.__init__(self, 'reddit_data', truncate=True)

if __name__ == '__main__':
    loader = ProggitLoader()
    loader.run()
