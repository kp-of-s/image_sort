# module/upload_module.py
import os
import shutil
from tkinter import messagebox

from util.path_utils import get_data_root, folder_to_csv_name

class UploadManager:
# 폴더 업로드 관련 비즈니스 로직을 담당하는 클래스

    def validate_subfolder(self, subfolder):
        """폴더 구조 검증: image 폴더 및 csv 파일 존재 여부 확인"""
        images_folder_path = os.path.join(subfolder, 'images')

        csv_file_name = folder_to_csv_name(subfolder)
        csv_file_path = os.path.join(subfolder, csv_file_name)

        return os.path.isdir(images_folder_path) and os.path.isfile(csv_file_path)
    
    def get_all_subfolders(self, source_folder_path):
        """원본 경로 및 복사할 경로 반환"""
        origin_folder_paths = []
        dest_paths = []

        source_folder_name = os.path.basename(source_folder_path.rstrip("/\\"))

        # 1. source_folder_path 자체를 리스트에 추가
        origin_folder_paths.append(source_folder_path)
        dest_paths.append(os.path.join(get_data_root(), source_folder_name))

        for root, dirs, files in os.walk(source_folder_path):
            dirs[:] = [d for d in dirs if d != 'images']
            for d in dirs:
                full_path = os.path.join(root, d)
                #검증
                if not self.validate_subfolder(full_path):
                    continue

                origin_folder_paths.append(full_path)

                relative_root = root.split(source_folder_name, 1)[1].lstrip("/\\")
                path_from_selected = os.path.join(source_folder_name, relative_root, d)
                dest_paths.append(os.path.join(get_data_root(), path_from_selected))

        return origin_folder_paths, dest_paths

    def is_duplicate(self, folder_path):
        """기본 폴더명 및 unsorted_ 접두사 폴더명 중복 검사"""
        # 기본 폴더명 중복 확인
        # unsorted_ 접두사 중복 확인
        parts = folder_path.split(os.sep)
        parts[-1] = f"unsorted_{parts[-1]}"
        unsorted_dest_paths = os.sep.join(parts)
        return os.path.exists(folder_path) or os.path.exists(unsorted_dest_paths)
    
    def copy_to_data_folder(self, full_folder_path, dest_path):
        # 자동분류가 완료되지 않은 폴더 표시, 수동 분류 불가하도록.
       
        parent = os.path.dirname(dest_path)
        last = os.path.basename(dest_path)
        unsorted_dest_path = os.path.join(parent, f"unsorted_{last}")

        shutil.copytree(full_folder_path, unsorted_dest_path)
        return unsorted_dest_path


    def upload_folder(self, source_folder_path):
        full_folder_paths, dest_paths = self.get_all_subfolders(source_folder_path)

        copied_paths = []
        error_messages = []

        for full_folder_path, dest_path in zip (full_folder_paths, dest_paths):
            # 필요한 파일/폴더 검증
            if not self.validate_subfolder(full_folder_path):
                error_messages.append(f"필요한 파일/폴더 없음: {full_folder_path}")
                continue

            # 중복 체크
            if self.is_duplicate(dest_path):
                error_messages.append(f"중복 폴더: {dest_path}")
                continue

            # data 폴더로 복사
            try:
                unsorted_dest_path = self.copy_to_data_folder(full_folder_path, dest_path)
                copied_paths.append(unsorted_dest_path)
            except Exception as e:
                error_messages.append(f"복사 실패: {full_folder_path} - {str(e)}")


        return copied_paths, error_messages
