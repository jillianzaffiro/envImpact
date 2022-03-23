from os import path, makedirs
import functools
import pickle

from Common.Config import get_config


def persist(dname="data", suffix="p"):
    def outer_wrapper(func):
        @functools.wraps(func)
        def inner_wrapper(*args, **kwargs):
            cfg = get_config()
            fname = f"{dname}_{cfg.FILE_TAG}.{suffix}"
            if path.exists(fname):
                with open(fname, "rb") as f:
                    data = pickle.load(f)
                return data
            data = func(*args, **kwargs)
            with open(fname, "wb") as f:
                pickle.dump(data, f)
            return data
        return inner_wrapper
    return outer_wrapper


def persist_results(fname, func, *args, **kwargs):
    if path.exists(fname):
        data = pickle.load(open(fname, "rb"))
        return data

    dir_path = path.dirname(fname)
    if not path.exists(dir_path):
        try:
            makedirs(dir_path)
        except IOError as e:
            raise Exception('Unable to create dir at {}\n{}'.format(fname[:-1], e.strerror))

    data = func(*args, **kwargs)
    pickle.dump(data, open(fname, "wb"))
    return data


#
# Example use
@persist(dname="test")
def hello(name):
    return f"Hello {name}"
