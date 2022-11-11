import uuid
import random
import typing as tp

GEN_STRING = 'GfTLy9uE4dg7ADzeOrjWCsixF1l38hQ5IPRmtnkVJKaoXBYbpvZ0q2SNUwcM6H'
BASE = len(GEN_STRING)

def gen_key_from_index(idx: int):
    """generate a url key """
    key = "" if idx else GEN_STRING[0]
    while idx:
        idx, mod = divmod(idx, BASE)
        key += GEN_STRING[mod]
    return key

