def sha1_string(string):
    import hashlib
    hashed_string = string.encode('utf-8')
    return hashlib.sha1(hashed_string).hexdigest()