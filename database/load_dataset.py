import pandas as pd
import json
import os


def load_and_prepare_data(file_path):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, file_path)
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    df = pd.DataFrame(data)
    return df
