# module/upload_module.py
import os
import shutil
from tkinter import messagebox
from util.path_utils import get_data_root

class UploadManager:
    """폴더 업로드 관련 비즈니스 로직을 담당하는 클래스"""
    
    def __init__(self):
        self.data_root = get_data_root()
    
    def validate_folder_structure(self, folder_path):
        """
        폴더 및 하위 폴더를 재귀적으로 탐색하여,
        'image' 폴더와 CSV 파일이 존재하는지 확인

        Returns:
            tuple: (bool, error_message)
        """
        if not folder_path:
            return False, "폴더 경로가 제공되지 않았습니다."

        def _recursive_check(current_path):
            folder_name = os.path.basename(current_path.rstrip("/\\"))
            image_folder_path = os.path.join(current_path, "image")
            csv_file_path = os.path.join(current_path, f"{folder_name}.csv")

            # 유효한 폴더 발견 시 True 반환
            if os.path.isdir(image_folder_path) and os.path.isfile(csv_file_path):
                return True, None

            # 하위 폴더 재귀 탐색
            try:
                for entry in os.listdir(current_path):
                    full_path = os.path.join(current_path, entry)
                    if os.path.isdir(full_path):
                        found, error = _recursive_check(full_path)
                        if found:
                            return True, None
            except PermissionError:
                return False, f"'{current_path}' 폴더를 열 수 없습니다."

            # 현재 폴더와 하위 폴더 모두 유효하지 않음
            return False, f"'{current_path}' 폴더 또는 하위 폴더에 'image' 폴더와 CSV 파일이 없습니다."

        # 재귀 검사 시작
        return _recursive_check(folder_path)

    
    def check_duplicate_folder(self, folder_path):

        folder_name = os.path.basename(folder_path.rstrip("/\\"))
        
        # 기본 폴더명으로 중복 확인
        dest_path = os.path.join(self.data_root, folder_name)
        if os.path.exists(dest_path):
            return True, f"{folder_name} 폴더가 이미 존재합니다."
        
        # unsorted_ 접두사로 중복 확인
        unsorted_dest_path = os.path.join(self.data_root, f"unsorted_{folder_name}")
        if os.path.exists(unsorted_dest_path):
            return True, f"unsorted_{folder_name} 폴더가 이미 존재합니다."
        
        return False, None
    
    def upload_folder(self, source_folder_path):
        # 1. 폴더 구조 검증
        is_valid, error_msg = self.validate_folder_structure(source_folder_path)
        if not is_valid:
            return False, None, error_msg

        # 2. CSV 위치 기반 dest_path 결정
        folder_name = os.path.basename(source_folder_path.rstrip("/\\"))
        csv_folder = None
        for root, dirs, files in os.walk(source_folder_path):
            for file in files:
                if file.endswith(".csv"):
                    csv_folder = root
                    break
            if csv_folder:
                break

        if csv_folder == source_folder_path:
            dest_path = os.path.join(self.data_root, f"unsorted_{folder_name}")
        else:
            sub_folder_name = os.path.basename(csv_folder)
            dest_path = os.path.join(self.data_root, folder_name, f"unsorted_{sub_folder_name}")

        # 3. 중복 확인 및 폴더 복사
        is_duplicate, error_msg = self.check_duplicate_folder(dest_path)
        if is_duplicate:
            return False, None, error_msg

        shutil.copytree(csv_folder, dest_path)

        print("복사 완료:", dest_path)
        return True, dest_path, None


    
    def get_folder_info(self, folder_path):
        """
        폴더 정보 반환 (디버깅용)
        
        Args:
            folder_path (str): 폴더 경로
            
        Returns:
            dict: 폴더 정보
        """
        if not folder_path:
            return {}
        
        folder_name = os.path.basename(folder_path.rstrip("/\\"))
        return {
            "folder_path": folder_path,  # 사용자가 선택한 원본 폴더의 전체 경로
            "folder_name": folder_name,  # 폴더명 (경로에서 마지막 부분만 추출)
            "dest_path": os.path.join(self.data_root, f"unsorted_{folder_name}"),  # data 폴더 내 복사될 대상 경로 (unsorted_ 접두사 포함)
            "csv_file_path": os.path.join(folder_path, f"{folder_name}.csv"),  # 원본 폴더 내 CSV 파일 경로 (unsorted_ 접두사 없음)
            "image_folder_path": os.path.join(folder_path, "image")  # 원본 폴더 내 image 하위 폴더 경로
        }
