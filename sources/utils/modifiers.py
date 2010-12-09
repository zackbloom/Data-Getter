from functools import wraps

def hash_dict(dict):
    return ";".join(("%s:%s" % (k, v) for k, v in dict.iteritems()))

def cache(func):
    """
    A decorator to cache the response of a function based on the args and
    kwargs provided.  Obviously should only be used on functions without
    side effects.  Note: It is _not_ smart enough to realize that some args 
    and kwargs refer to the same argument.
    """
    _cache = {}
    @wraps(func)
    def _func(*args, **kwargs):
        if (args, hash_dict(kwargs)) not in _cache:
            _cache[(args, hash_dict(kwargs))] = func(*args, **kwargs)
        return _cache[(args, hash_dict(kwargs))]
        
    return _func

class NotInnitedError(Exception):
    pass

def remember_init(init_func):
    @wraps(init_func)
    def _init_func(self, *args, **kwargs):
        """
        Note that the var is set before calling init, allowing init to
        call other class methods without raising the exception.
        """
        self._init_called = True
        
        return init_func(self, *args, **kwargs)
        
    return _init_func
    
def require_init(func):
    @wraps(func)
    def _func(self, *args, **kwargs):
        if not hasattr(self, '_init_called') or not self._init_called:
            raise NotInnitedError('__init__ must be called on this object')
            
        return func(self, *args, **kwargs)
        
    return _func

class OptionallyRequireInit(type):
    """
    A metaclass which allows classes to require that subclasses call their
    __init__ methods before calling any other methods.  To enable this,
    add a '_require_init' class attribute.
    """
    def __new__(meta, name, bases, attrs):
        if '_require_init' in attrs and '__init__' in attrs:
            attrs['__init__'] = remember_init(attrs['__init__'])
            
            for k, v in attrs.iteritems():
                if callable(v) and k != '__init__':
                    attrs[k] = require_init(v)
                    
            # We don't want the _require_init attribute to be inherited.
            del attrs['_require_init']
                    
        return type.__new__(meta, name, bases, attrs)

if __name__ == "__main__":
    import unittest

    class TestCache(unittest.TestCase):
        def setUp(self):
            def func_count(arg=0, elems=[]):
                elems.append(1)
                return len(elems)

            self.func = func_count

        def test(self):
            cached_func = cache(self.func)

            self.assertNotEqual(self.func(), self.func())
            self.assertEqual(cached_func(), cached_func())
            self.assertNotEqual(cached_func(1), cached_func(2))
            self.assertEqual(cached_func(1), cached_func(1))
            self.assertNotEqual(cached_func(arg=3), cached_func(arg=4))
            self.assertEqual(cached_func(arg=2), cached_func(arg=2))

    class TestOptionallyRequireInit(unittest.TestCase):
        def setUp(self):
            class ReqClass(object):
                __metaclass__ = OptionallyRequireInit

                _require_init = True

                def __init__(self, arg=0):
                    self.initted_with = arg

                def some_method(self, arg=0):
                    return arg

            self.cls = ReqClass

            class BadSubClass(ReqClass):
                def __init__(self):
                    pass

            self.bad_cls = BadSubClass

            class GoodSubClass(ReqClass):
                def __init__(self):
                    ReqClass.__init__(self, 5)

                def other_method(self, arg=0):
                    return arg

            self.good_cls = GoodSubClass

            class ShouldntMatterSubClass(GoodSubClass):
                def __init__(self):
                    pass

            self.shouldnt_matter_cls = ShouldntMatterSubClass

        def test(self):
            bad = self.bad_cls()
            self.assertRaises(NotInnitedError, bad.some_method)

            good = self.good_cls()
            good.some_method()

            shouldnt_matter = self.shouldnt_matter_cls()
            shouldnt_matter.other_method()
            self.assertRaises(NotInnitedError, shouldnt_matter.some_method)

    unittest.main()
