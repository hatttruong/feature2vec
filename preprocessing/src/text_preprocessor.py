"""
Preprocess English documents

Attributes:
    logger (TYPE): Description
"""
import logging
import nltk
import unicodedata
import string
import re
from nltk.stem import SnowballStemmer
from nltk.stem import WordNetLemmatizer
from enum import Enum


nltk.download('punkt')  # for tokenize
nltk.download('wordnet')  # for stemming & lemmertize

logger = logging.getLogger(__name__)


class Replacement(Enum):

    """Define common constants

    Attributes:
        CURRENCY (str): Description
        DATETIME (str): Description
        EMAIL (str): Description
        EMOJI_NEG (str): Description
        EMOJI_POS (str): Description
        NUMBER (str): Description
        PHONE (str): Description
        URL (str): Description

    """
    EMAIL = ' '
    URL = ' '
    NUMBER = ' '
    PHONE = ' '
    CURRENCY = ' '
    DATETIME = ' '


def handle_url(text):
    """Summary

    Args:
        text (TYPE): Description

    Returns:
        TYPE: Description
    """
    text = re.sub(r'http\S+', Replacement.URL.value, text)
    return text


def handle_email(text):
    """Summary

    Args:
        text (TYPE): Description

    Returns:
        TYPE: Description
    """
    return re.sub(r'(\w+@\w+)', Replacement.EMAIL.value, text)


def handle_numbers(text):
    """Summary

    Args:
        text (TYPE): Description

    Returns:
        TYPE: Description
    """
    # normal numbers
    text = re.sub(r'^\d+\s|\s\d+\s|\s\d+$', Replacement.NUMBER.value, text)
    text = re.sub(r'\b[\d.\/,]+', Replacement.NUMBER.value, text)
    return text


def handle_phone(text):
    """
    Handle cases:
            XX XXX XXX
            XXX XXX XXX
            XXXXXXXXX
        delimiter: whitespace OR - OR empty

    Args:
        text (TYPE): Description

    Returns:
        TYPE: Description
    """
    return re.sub(r'([\+\s]*\d{2,}[-\s.]?\d{3,4}[-\s.]?\d{3,4})',
                  Replacement.PHONE.value, text)


def remove_non_alphabet(text):
    """

    Args:
        text (TYPE): Description

    Returns:
        TYPE: Description
    """
    text = re.sub(
        r'[^a-zA-Z]', ' ', text
    )
    return text


def handle_datetime(text):
    """
    Handle cases: MM/YYYY, DD/MM/YYYY, DD/MM
    delimiters: /.-

    Args:
        text (TYPE): Description

    Returns:
        TYPE: Description
    """
    # MM/YYYY
    group_1 = r'(\d{1,2}[-./]\d{4})'

    # DD/MM or DD/MM/YYYY
    group_2 = r'(\d{1,2}[-./]\d{1,2}([-./]\d{4})?)'

    # 09h56 OR 12h
    group_3 = r'(\d{1,2}(h|H)(\d{1,2}(min|mins)?)?)'
    return re.sub(r'(' + group_1 + '|' + group_2 + '|' + group_3 + ')',
                  Replacement.DATETIME.value, text)

def lower_string(text):
    """Summary

    Args:
        text (TYPE): Description

    Returns:
        TYPE: Description
    """
    if text is not None and len(text) > 0:
        return text.lower()
    return text

def preprocess_sentence(text):
    """
    Args:
        text (TYPE): Description

    Returns:
        TYPE: Description
    """
    funcs = [handle_url, handle_phone, handle_datetime,
             handle_numbers, handle_email, lower_string]
    for f in funcs:
        logger.debug('preprocess %s' % str(f))
        text = f(text)

    return text


def contain_punctuation(word):
    for p in string.punctuation:
        if p in word:
            return True
    return False


def preprocess_document(document):
    """
    Args:
        document (TYPE): Description

    Returns:
        TYPE: Description
    """
    logger.info('start preprocess document: %s',
                document[:100] if len(document) > 100 else document)
    PUNCTUATIONS = string.punctuation + ' '
    sents = [s for s in nltk.sent_tokenize(document) if len(s) > 1]
    logger.debug('step1: \n%s', '\n'.join(sents))

    # preprocess each sentence
    sents = [preprocess_sentence(s) for s in sents]
    logger.debug('step2: \n%s', '\n'.join(sents))

    # filter again too short sentence
    sents = [s.strip() for s in sents if len(s.strip()) > 1]
    logger.debug('step3: \n%s', '\n'.join(sents))

    # tokenize words
    words = [[w.strip(PUNCTUATIONS) for w in nltk.word_tokenize(s)
              if contain_punctuation(w) is False]
             for s in sents]

    # stemming & lemming
    stemmer = SnowballStemmer("english")
    lemmatizer = WordNetLemmatizer()

    words = [[stemmer.stem(w) for w in s] for s in words]
    words = [[lemmatizer.lemmatize(w) for w in s] for s in words]

    return words
