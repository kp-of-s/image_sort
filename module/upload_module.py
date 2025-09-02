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
        폴더 구조 검증
        
        Args:
            folder_path (str): 검증할 폴더 경로
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not folder_path:
            return False, "폴더 경로가 제공되지 않았습니다."
        
        folder_name = os.path.basename(folder_path.rstrip("/\\"))
        
        # image 폴더 존재 여부 확인
        image_folder_path = os.path.join(folder_path, "image")
        if not os.path.isdir(image_folder_path):
            return False, "선택한 폴더 안에 'image' 폴더가 없습니다."
        
        # CSV 파일 존재 여부 확인
        csv_file_path = os.path.join(folder_path, f"{folder_name}.csv")
        if not os.path.isfile(csv_file_path):
            return False, f"폴더에 '{folder_name}.csv' 파일이 존재하지 않습니다."
        
        return True, None
    
    def check_duplicate_folder(self, folder_path):
        """
        중복 폴더명 확인
        
        Args:
            folder_path (str): 확인할 폴더 경로
            
        Returns:
            tuple: (is_duplicate, error_message)
        """
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
        """
        폴더 업로드 실행
        
        Args:
            source_folder_path (str): 업로드할 소스 폴더 경로
            
        Returns:
            tuple: (success, destination_path, error_message)
        """
        try:
            # 폴더 구조 검증
            is_valid, error_msg = self.validate_folder_structure(source_folder_path)
            if not is_valid:
                return False, None, error_msg
            
            # 중복 폴더명 확인
            is_duplicate, error_msg = self.check_duplicate_folder(source_folder_path)
            if is_duplicate:
                return False, None, error_msg
            
            # 폴더 복사
            folder_name = os.path.basename(source_folder_path.rstrip("/\\"))
            dest_path = os.path.join(self.data_root, f"unsorted_{folder_name}")
            
            shutil.copytree(source_folder_path, dest_path)
            
            return True, dest_path, None
            
        except Exception as e:
            return False, None, f"폴더 업로드 중 오류 발생:\n{str(e)}"
    
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
