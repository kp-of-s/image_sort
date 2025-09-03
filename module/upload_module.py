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
        'image' 폴더와 CSV 파일이 존재하는 모든 폴더를 리스트로 반환

        Returns:
            tuple: (bool, list_of_valid_paths, error_message)
                list_of_valid_paths: 유효한 image+CSV 폴더 경로 리스트
        """
        if not folder_path:
            return False, [], "폴더 경로가 제공되지 않았습니다."

        valid_paths = []

        def _recursive_check(current_path):
            folder_name = os.path.basename(current_path.rstrip("/\\"))
            image_folder_path = os.path.join(current_path, "image")
            csv_file_path = os.path.join(current_path, f"{folder_name}.csv")

            # 유효한 폴더 발견 시 리스트에 추가
            if os.path.isdir(image_folder_path) and os.path.isfile(csv_file_path):
                valid_paths.append(current_path)

            # 하위 폴더 재귀 탐색
            try:
                for entry in os.listdir(current_path):
                    full_path = os.path.join(current_path, entry)
                    if os.path.isdir(full_path):
                        _recursive_check(full_path)
            except PermissionError:
                pass  # 접근 불가 폴더는 무시

        _recursive_check(folder_path)

        if valid_paths:
            return True, valid_paths, None
        else:
            return False, [], f"'{folder_path}' 폴더 및 하위 폴더에 'image' 폴더와 CSV 파일이 없습니다."

    
    def check_duplicate_folders(self, folder_paths):
        """
        여러 폴더 경로 리스트를 받아, data_root 내 중복 여부 확인

        Args:
            folder_paths (list): 유효한 폴더 경로 리스트

        Returns:
            tuple: (bool, list_of_duplicate_messages)
                bool: 중복 폴더가 하나라도 있으면 True
                list_of_duplicate_messages: 각 중복 폴더에 대한 메시지 리스트
        """
        duplicates = []

        for folder_path in folder_paths:
            folder_name = os.path.basename(folder_path.rstrip("/\\"))
            
            # 기본 폴더명 중복 확인
            dest_path = os.path.join(self.data_root, folder_name)
            if os.path.exists(dest_path):
                duplicates.append(f"{folder_name} 폴더가 이미 존재합니다.")
                continue
            
            # unsorted_ 접두사 중복 확인
            unsorted_dest_path = os.path.join(self.data_root, f"unsorted_{folder_name}")
            if os.path.exists(unsorted_dest_path):
                duplicates.append(f"unsorted_{folder_name} 폴더가 이미 존재합니다.")

        return (len(duplicates) > 0, duplicates)


    def upload_folder(self, source_folder_path):
        """
        소스 폴더 및 하위 폴더를 검사하여 유효한 폴더를
        data_root로 복사. 여러 유효 폴더를 리스트 순회 처리.

        Returns:
            tuple: (bool, list_of_copied_paths, list_of_errors)
        """

        def make_dest_path(source_folder_path, data_root):
            # 상대 경로를 뽑아냄 (업로드 루트 기준)
            # 여기서는 유저가 직접 올린 최상위 폴더를 base로 삼음
            parent_path, last_folder = os.path.split(source_folder_path.rstrip("/\\"))
            rel_path = os.path.relpath(parent_path, start=os.path.dirname(source_folder_path))

            # 중간 폴더 구조 복원
            if rel_path == ".":
                # 중간 구조가 없는 경우 (폴더c만 업로드된 경우)
                dest_path = os.path.join(data_root, f"unsorted_{last_folder}")
            else:
                dest_path = os.path.join(data_root, rel_path, f"unsorted_{last_folder}")
            
            return dest_path

        # 1. 폴더 구조 검증 (유효 폴더 리스트 반환)
        is_valid, valid_folders, error_msg = self.validate_folder_structure(source_folder_path)
        if not is_valid:
            return False, [], [error_msg]

        copied_paths = []
        error_messages = []

        # 2. 중복 체크
        is_dup, dup_messages = self.check_duplicate_folders(valid_folders)
        if is_dup:
            return False, [], dup_messages

        # 3. 각 유효 폴더 복사
        for folder_path in valid_folders:
            folder_name = os.path.basename(folder_path.rstrip("/\\"))
            dest_path = make_dest_path(source_folder_path, self.data_root)

            try:
                shutil.copytree(folder_path, dest_path)
                copied_paths.append(dest_path)
                print("복사 완료:", copied_paths)
            except Exception as e:
                error_messages.append(f"{folder_name} 복사 실패: {str(e)}")

        # 4. 최종 결과 반환
        if error_messages:
            return False, [copied_paths], error_messages
        else:
            return True, [copied_paths], None



    
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
