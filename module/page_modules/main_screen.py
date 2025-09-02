# module/page_modules/main_screen.py
import tkinter as tk
from module.page_modules.upload_folder_page import open_upload_folder_page
from module.page_modules.select_folder_page import open_select_folder_page  # 기존 페이지
from util.path_utils import get_data_root

def open_main_screen(root):
    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    tk.Label(frame, text="기능 선택", font=("Arial", 16)).pack(pady=20)

    def go_upload():
        frame.pack_forget()
        open_upload_folder_page(root)

    def go_select():
        frame.pack_forget()
        open_select_folder_page(root, get_data_root())

    tk.Button(frame, text="폴더 업로드", width=20, command=go_upload).pack(pady=10)
    tk.Button(frame, text="폴더 선택", width=20, command=go_select).pack(pady=10)

    return frame
