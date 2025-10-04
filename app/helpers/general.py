import numpy as np
from faker import Faker
import random
import uuid
import pandas as pd

# ----------------------------
# Utility functions
# ----------------------------


def set_seed(seed, locale=None):
    np.random.seed(seed)
    random.seed(seed)
    Faker.seed(seed)
    return Faker(locale) if locale else Faker()


def rand_ids(prefix, n):
    return [f"{prefix}_{uuid.uuid4().hex[:8]}" for _ in range(n)]


def date_range(start, end, freq):
    return pd.date_range(start=start, end=end, freq=freq)
