import string

B62_ALPHABET = string.digits + string.ascii_letters
REVERSE_B62_ALPHABET = {
    val: index for index, val in enumerate(B62_ALPHABET)
}

SHORT_URL_MAX_LEN = 5
ENCODE_NUM_MAX = int(8 * 1E8)