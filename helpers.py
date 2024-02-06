MULTIPLIER_LOOKUP = {"K": 1024, "M": 1048576, "G": 1073741824}

SIZE_STRINGS = ["KB", "MB", "GB", "TB", "PB"]

def bytes_to_size_string(num):
    """ Converts a byte value into a size string """
    i = 0
    ret = num / 1024
    while ret >= 1024 and i < 4:
        i += 1
        ret = ret / 1024
    return f"{ret:.2f}{SIZE_STRINGS[i]}"


def size_string_to_bytes(size_string):
    """ Converts a size string into a bytes value """
    num = float(size_string[:-1])
    size_iden = size_string[-1:]

    mult = MULTIPLIER_LOOKUP.get(size_iden, 1)

    return num * mult