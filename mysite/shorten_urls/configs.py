import string

B62_ALPHABET = string.digits + string.ascii_letters
REVERSE_B62_ALPHABET = {
    val: index for index, val in enumerate(B62_ALPHABET)
}

SHORT_URL_MAX_LEN = 5
ENCODE_NUM_MAX = int(8 * 1E8)

URL_B62_BASE_NUM = int(1E8)
URL_B62_OFFSET_SIZE = int(1E8)
URL_B62_OFFSET_RANGE = [0, 6]

CRAWL_URL_PREVIEW_TIMEOUT = 3