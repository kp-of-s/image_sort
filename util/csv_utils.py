import pandas as pd
import os
from util.path_utils import get_data_subpath

def load_csv(folder_name, csv_file):
    """
    data/<folder_name>/<csv_file>에서 CSV 파일 로드
    """
    if csv_file:
        file_path = os.path.join(get_data_subpath(folder_name), csv_file)
        if os.path.exists(file_path):
            return pd.read_csv(file_path, encoding="utf-8-sig")
    return None

def save_csv(df, folder_name, csv_file):
    """
    DataFrame을 data/<folder_name>/<csv_file>에 저장
    """
    if csv_file and df is not None:
        folder_path = get_data_subpath(folder_name)
        os.makedirs(folder_path, exist_ok=True)  # 폴더 없으면 생성
        file_path = os.path.join(folder_path, csv_file)
        df.to_csv(file_path, index=False, encoding="utf-8-sig")
