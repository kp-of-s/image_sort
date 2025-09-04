# module/upload_module.py
import os
import shutil
from tkinter import messagebox
from util.path_utils import get_data_root

class UploadManager:
    """폴더 업로드 관련 비즈니스 로직을 담당하는 클래스"""
    
    def __init__(self):
        self.data_root = get_data_root()
    
    import os

    def validate_folder_structure(self, folder_path):
        """폴더 구조 검증: image 폴더 및 csv 파일 존재 여부 확인"""
        if not folder_path:
            return []

        invalid_folders = []

        try:
            for entry in os.listdir(folder_path):
                current_path = os.path.join(folder_path, entry)
                if os.path.isdir(current_path):
                    folder_name = os.path.basename(current_path.rstrip("/\\"))
                    image_folder = os.path.join(current_path, "image")
                    csv_file = os.path.join(current_path, f"{folder_name}.csv")

                    if not (os.path.isdir(image_folder) and os.path.isfile(csv_file)):
                        invalid_folders.append(folder_name)

        except PermissionError:
            invalid_folders.append(os.path.basename(folder_path.rstrip("/\\")))

        return invalid_folders

    
    def check_duplicate_folders(self, folder_path):
        """기본 폴더명 및 unsorted_ 접두사 폴더명 중복 검사"""
        duplicates = []

        rel_path = os.path.relpath(folder_path, start=os.path.dirname(self.data_root))

        # 기본 폴더명 중복 확인
        dest_path = os.path.join(self.data_root, rel_path)
        if os.path.exists(dest_path):
            duplicates.append(f"{rel_path} 경로가 이미 존재합니다.")

        # unsorted_ 접두사 중복 확인
        parts = rel_path.split(os.sep)
        parts[-1] = f"unsorted_{parts[-1]}"   # 마지막 폴더명만 변경
        unsorted_rel_path = os.path.join(*parts)
        unsorted_dest_path = os.path.join(self.data_root, unsorted_rel_path)
        if os.path.exists(unsorted_dest_path):
            duplicates.append(f"{unsorted_rel_path} 경로가 이미 존재합니다.")

        return (len(duplicates) > 0, duplicates)


    def upload_folder(self, source_folder_path):

        import os

        def make_dest_path(source_folder_path, invalid_folders):
            folders_with_csv = []

            parent_dir = os.path.dirname(source_folder_path)

            for root, dirs, files in os.walk(source_folder_path):
                # CSV 파일이 있는지 확인
                if any(file.lower().endswith(".csv") for file in files):
                    # 최하위 폴더명
                    folder_name = os.path.basename(root.rstrip("/\\"))

                    # 유효하지 않은 폴더는 제외
                    if folder_name in invalid_folders:
                        continue

                    # parent_folder 기준 상대 경로 생성
                    rel_path = os.path.relpath(root, start=parent_dir)
                    folders_with_csv.append(rel_path)

            print(f"Folders with CSV (유효한 폴더만): {folders_with_csv}")
            return folders_with_csv

        
        # 1. csv가 담긴 폴더의 구조 검증
        invalid_folders = self.validate_folder_structure(source_folder_path)
        if invalid_folders:
            messagebox.showwarning(
                title="폴더 구조 경고",
                message="폴더가 바르지 못한 구조입니다."
            )

        dest_paths = make_dest_path(source_folder_path, invalid_folders)
        error_messages = []
        copied_paths = []

        for rel_path in dest_paths:
            folder_path = os.path.join(os.path.dirname(source_folder_path), rel_path)
            folder_name = os.path.basename(folder_path.rstrip("/\\"))

            intermediate_path = os.path.dirname(rel_path)

            new_folder_name = f"unsorted_{folder_name}"

            # 목적지 경로 생성
            dest_folder_path = os.path.join(self.data_root, intermediate_path, new_folder_name)

            # 필요시 중간 폴더까지 생성
            os.makedirs(os.path.dirname(dest_folder_path), exist_ok=True)

            print(f"Copying {folder_path} → {dest_folder_path}")

            try:
                shutil.copytree(folder_path, dest_folder_path)
            except Exception as e:
                error_messages.append(f"{folder_name} 복사 실패: {str(e)}")


        success = len(error_messages) == 0

        return success, copied_paths, error_messages
