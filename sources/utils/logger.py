import logging 
import logging.handlers
import sys
import re

class LoopError(Exception):
    pass

def loop_through(obj):
    if isinstance(obj, dict):
        return obj.iteritems()
    elif isinstance(obj, list) or isinstance(obj, tuple):
        return enumerate(obj)
    raise LoopError("Can't loop through %s" % unicode(obj).encode('ascii', 'replace'))

def remove_vals(struct):
    while True:
        m = re.search('<<<(.+)>>>', struct, re.DOTALL)
        if not m:
            return struct

        struct = struct[:m.start(1)] + struct[m.end(1)+1:]

def get_repeat_count_str(count, depth):
    return "\n" + "\t"*depth + "... (%d more)" % count

def get_structure(struct, depth=0):
    """
    A really rough method to print the structure of a data structure.
    Only really supports combinations of dicts, lists, tuples and values.
    Intelligently eliminates duplicates.
    """
    try: 
        out = ""
        last_st = None
        seen = []
        st_count = 0
        for k, v in loop_through(struct):
            st = get_structure(v, depth + 1)
            if remove_vals(st) == last_st and isinstance(k, int):
                if st_count:
                    out = out[:-len(get_repeat_count_str(st_count, depth))]

                st_count += 1
                out += get_repeat_count_str(st_count, depth)
            else:
                last_st = remove_vals(st)
                out += "\n" + "\t" * depth
                if st_count:
                    st_count = 0
                    out += "\n" + "\t" * depth

                out += "%s: %s" % (str(k), st)
        return out
    except LoopError:
        return "<<<%s>>>" % unicode(struct).encode('ascii', 'replace')

_logging_set_up = False
def _setup_logger(logger):
    global _logging_set_up
    logger.setLevel(logging.INFO)
    
    print_handler = logging.StreamHandler(sys.stderr)
    logger.addHandler(print_handler)
    
    _logging_set_up = True
    
def get_logger():
    global _logging_set_up
    
    logger = logging.getLogger('logger')
    
    if not _logging_set_up:
        _setup_logger(logger)
    
    return logger
    
logger = get_logger()
