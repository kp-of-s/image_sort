import os
from util.path_utils import get_data_path

def get_subfolders():
    """
    data 폴더 안의 하위 폴더 목록 반환
    """
    data_path = get_data_path()  # data 폴더 경로
    if os.path.exists(data_path):
        return [f for f in os.listdir(data_path) if os.path.isdir(os.path.join(data_path, f))]
    return []

def get_image_and_csv(folder_name, image_folder_name="image"):
    """
    data/<folder_name>/image 폴더와 CSV 파일 경로 반환
    """
    folder_path = os.path.join(get_data_path(), folder_name)
    image_folder = os.path.join(folder_path, image_folder_name)

    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    csv_file = csv_files[0] if csv_files else None

    return image_folder, csv_file
