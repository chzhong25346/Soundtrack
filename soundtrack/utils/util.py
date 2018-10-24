import hashlib


def gen_id(string):
    return int(hashlib.md5(str.encode(string)).hexdigest(), 16)
