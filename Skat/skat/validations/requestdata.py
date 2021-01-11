
def empty_validation(req_param):
    if not req_param:
        raise ValueError("Fields must not be empty!")
    return req_param
