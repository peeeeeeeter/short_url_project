from .configs import (B62_ALPHABET, ENCODE_NUM_MAX, REVERSE_B62_ALPHABET,
                      SHORT_URL_MAX_LEN)


def b62_encode(number: int) -> str:
    result = []
    alphabet_Len = len(B62_ALPHABET)

    if not isinstance(number, int):
        raise ValueError('number must be positive integer')
    elif not 1 <= number <= ENCODE_NUM_MAX:
        raise ValueError(
            'number must be in range 1 to {}'.format(ENCODE_NUM_MAX))

    while number:
        result.append(B62_ALPHABET[number % alphabet_Len])
        number //= alphabet_Len

    return ''.join(reversed(result))


def b62_decode(string: str, maxlen: int = SHORT_URL_MAX_LEN) -> int:

    if not isinstance(string, str):
        raise ValueError('string must be a instance of str')
    elif not 1 <= len(string) <= maxlen:
        raise ValueError(
            'string length must be in range 1 to {}'.format(SHORT_URL_MAX_LEN))

    number = 0
    for index, char in enumerate(reversed(string)):
        number += pow(62, index) * REVERSE_B62_ALPHABET[char]

    return number
