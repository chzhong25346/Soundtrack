import hashlib


def gen_id(string):
    return int(hashlib.md5(str.encode(string)).hexdigest(), 16)


def normalize_sp500(data):
    data['symbol'] = data['symbol'].str.replace(".","-")
    return data
