# module/page_modules/upload_folder_page.py
import tkinter as tk
from tkinter import filedialog, messagebox
from module.upload_module import UploadManager
from module.page_modules.sort_progress_page import open_sort_progress_page
from module.components.home_button import add_back_to_main_button

def open_upload_folder_page(root):
    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    # 업로드 매니저 인스턴스 생성
    upload_manager = UploadManager()

    # GUI 구성요소
    label = tk.Label(frame, text="업로드할 폴더를 선택하세요", font=("Arial", 12))
    label.pack(pady=10)

    selected_folder_var = tk.StringVar()
    entry = tk.Entry(frame, textvariable=selected_folder_var, width=50, state="readonly")
    entry.pack(pady=5)

    def browse_folder():
        """폴더 선택 다이얼로그"""
        folder = filedialog.askdirectory(title="업로드할 폴더 선택")
        if folder:
            selected_folder_var.set(folder)

    browse_btn = tk.Button(frame, text="폴더 선택", command=browse_folder)
    browse_btn.pack(pady=5)

    def upload_folder():
        """폴더 업로드 실행"""
        folder_path = selected_folder_var.get()
        
        # 폴더 선택 확인
        if not folder_path:
            messagebox.showwarning("폴더 선택 필요", "업로드할 폴더를 선택하세요")
            return
        
        # 업로드 매니저를 통한 업로드 실행
        success, dest_paths, error_message = upload_manager.upload_folder(folder_path)
        
        if success:
            # 업로드 성공
            selected_folder_var.set("")  # 입력창 초기화
            frame.pack_forget()  # 현재 페이지 숨김
            open_sort_progress_page(root, dest_paths)  # 정렬 페이지로 이동
        else:
            # 업로드 실패 - 오류 메시지 표시
            messagebox.showerror("업로드 실패", error_message)

    upload_btn = tk.Button(frame, text="업로드", command=upload_folder)
    upload_btn.pack(pady=10)

    add_back_to_main_button(root, frame)

    return frame