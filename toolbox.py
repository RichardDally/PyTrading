import uuid
import random
import string
from datetime import datetime


def generate_unique_identifier() -> str:
    return str(uuid.uuid4().int)


def pretty_timestamp(timestamp: int):
    return datetime.fromtimestamp(timestamp).strftime('%Y%m%d_%H%M%S')


def random_string(length):
    """
    Generate a random string of fixed length
    """
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(length))
