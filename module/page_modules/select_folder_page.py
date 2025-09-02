# module/page_modules/select_folder_page.py
import tkinter as tk
from tkinter import messagebox
import os
from module.page_modules.edit_screen import open_edit_screen
from util.path_utils import folder_to_csv_name
from module.components.home_button import create_home_button

def open_select_folder_page(root, data_path):
    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True)

    current_path = [None]  # 리스트로 감싸 상태 공유 가능

    def open_folder(folder_path):
        current_path[0] = folder_path
        csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
        if csv_files:
            open_edit_screen(folder_path, folder_to_csv_name(folder_path))
            return

        subfolders = [
            f for f in os.listdir(folder_path)
            if os.path.isdir(os.path.join(folder_path, f)) and not f.startswith("unsorted_")
        ]
        if subfolders:
            listbox.delete(0, tk.END)
            for sf in subfolders:
                listbox.insert(tk.END, sf)
            label.config(text=f"{os.path.basename(folder_path)} 의 하위 폴더를 선택하세요")
        else:
            messagebox.showwarning("폴더 비어있음", f"{folder_path}에 CSV 파일이나 하위 폴더가 없습니다.")

    label = tk.Label(frame, text="1차 분류 폴더를 선택하세요")
    label.pack(pady=10)

    listbox = tk.Listbox(frame, width=50, height=20)
    listbox.pack(padx=10, pady=10)

    def on_select(event):
        if not listbox.curselection():
            return
        selection = listbox.get(listbox.curselection())
        folder_path = os.path.join(data_path, selection)
        open_folder(folder_path)

    listbox.bind("<<ListboxSelect>>", on_select)

    first_folders = [
        f for f in os.listdir(data_path)
        if os.path.isdir(os.path.join(data_path, f)) and not f.startswith("unsorted_")
    ]

    for f in first_folders:
        listbox.insert(tk.END, f)

    return frame
