import pandas as pd
from typing import Iterator, Dict

def process_cicids2017(filepath: str) -> Iterator[Dict]:
    """
    Reads CICIDS2017 CSV and yields events matching Phase 0 schema.
    Requires downloading CICIDS2017 dataset from UNB website.
    """
    df = pd.read_csv(filepath)
    # Mapping logic to normalize feature names, protocols, labels, timestamps 
    # to the NetworkEvent schema goes here.
    for _, row in df.iterrows():
        # Placeholder
        pass
