# Drop rows with missing outcome or confounder values for a clean baseline run
import numpy as np
import pandas as pd
import logging
from config import treatment, outcome, confounders
from causaldata import nhefs

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_data():
    # Load the dataset
    logger.info("Loading dataset...")
    data = nhefs.load_pandas().data

    logger.info(f"Original dataset shape: {data.shape}")
    logger.info(f"Original dataset columns: {data.columns}")

    # pick only cols needed and 
    # Drop rows with missing values in treatment, outcome, or confounders
    df = data[[treatment, outcome] + confounders].dropna()
    logger.info(f"Dataset shape: {df.shape}")

    return df
