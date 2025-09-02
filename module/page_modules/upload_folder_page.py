# module/page_modules/upload_folder_page.py
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil
from util.path_utils import get_data_root
from module.page_modules.sort_progress_page import open_sort_progress_page  # 새 페이지

def open_upload_folder_page(root):
    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    data_root = get_data_root()

    label = tk.Label(frame, text="업로드할 폴더를 선택하세요", font=("Arial", 12))
    label.pack(pady=10)

    selected_folder_var = tk.StringVar()
    entry = tk.Entry(frame, textvariable=selected_folder_var, width=50, state="readonly")
    entry.pack(pady=5)

    def browse_folder():
        folder = filedialog.askdirectory(title="업로드할 폴더 선택")
        if folder:
            selected_folder_var.set(folder)

    browse_btn = tk.Button(frame, text="폴더 선택", command=browse_folder)
    browse_btn.pack(pady=5)

    def upload_folder():
        folder_path = selected_folder_var.get()
        if not folder_path:
            messagebox.showwarning("폴더 선택 필요", "업로드할 폴더를 선택하세요")
            return
        folder_name = os.path.basename(folder_path.rstrip("/\\"))
        dest_path = os.path.join(data_root, folder_name)
        csv_file_path = os.path.join(folder_path, f"{folder_name}.csv")
        image_folder_path = os.path.join(folder_path, "image")

        print("folder_path", folder_path)
        print("folder_name", folder_name)
        print("dest_path", dest_path)
        print("csv_file_path", csv_file_path)
        print("image_folder_path", image_folder_path)


        if not os.path.isdir(image_folder_path):
            messagebox.showwarning("검증 실패", "선택한 폴더 안에 'image' 폴더가 없습니다.")
            return

        # 검증: CSV 파일 존재 여부
        if not os.path.isfile(csv_file_path):
            messagebox.showwarning("검증 실패", f"폴더에 '{folder_name}.csv' 파일이 존재하지 않습니다.")
            return


        if os.path.exists(dest_path):
            messagebox.showwarning("중복 폴더", f"{folder_name} 폴더가 이미 존재합니다.")
            return
        
        dest_path = os.path.join(data_root, f"unsorted_{folder_name}")
        if os.path.exists(dest_path):
            messagebox.showwarning("중복 폴더", f"{folder_name} 폴더가 이미 존재합니다.")
            return

        try:
            shutil.copytree(folder_path, dest_path)
            selected_folder_var.set("")
            frame.pack_forget()  # 현재 업로드 페이지 숨김
            open_sort_progress_page(root, folder_path)  # 정렬 페이지 호출
            # old_file = os.path.join(folder_path, dest_path + ".csv")
            # new_file = os.path.join(folder_path, folder_name + ".csv")
            # print(old_file, new_file)
            # os.rename(old_file, new_file)
        except Exception as e:
            messagebox.showerror("오류", f"폴더 업로드 중 오류 발생:\n{e}")

    upload_btn = tk.Button(frame, text="업로드", command=upload_folder)
    upload_btn.pack(pady=10)

    return frame