import os
import tkinter as tk
from tkinter import ttk
from module.event_handlers import bind_image_selection, bind_combobox_save
from util.csv_utils import load_csv, save_csv
from util.options_utils import load_options
from util.image_utils import get_image_files


def open_edit_screen(folder_path, csv_file):
    """편집 화면 초기화 및 구성"""
    # CSV 데이터 로드
    df = load_csv(folder_path, csv_file)

    # 윈도우 생성
    win = tk.Toplevel()
    win.title(f"편집 화면 - {os.path.basename(folder_path)}")

    # 화면 비율 기반 크기
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    win_width = int(screen_width * 0.7)
    win_height = int(screen_height * 0.8)
    win.geometry(f"{win_width}x{win_height}")

    # 이미지 폴더 및 파일 리스트
    image_folder = os.path.join(folder_path, "image")
    image_files = get_image_files(image_folder)

    # 좌측 리스트
    list_frame = tk.Frame(win)
    list_frame.pack(side="left", fill="y", padx=5, pady=5)
    img_listbox = tk.Listbox(list_frame, width=35, height=30)
    img_listbox.pack(side="left", fill="y")
    for idx, f in enumerate(image_files):
        img_listbox.insert(tk.END, f"{idx+1}. {f}")

    # 이미지 라벨
    img_label = tk.Label(win, text="이미지를 선택하세요")
    img_label.pack(side="top", fill="both", expand=True, padx=10, pady=10)

    # Treeview
    tree_frame = tk.Frame(win)
    tree_frame.pack(side="bottom", fill="both", expand=True, pady=10)
    treeview = ttk.Treeview(tree_frame, columns=list(df.columns), show="headings")
    for col in df.columns:
        treeview.heading(col, text=col)
        treeview.column(col, width=100)
    treeview.pack(fill="both", expand=True)

    # 편집 Combobox
    edit_frame = tk.Frame(win)
    edit_frame.pack(side="bottom", fill="x", padx=10, pady=5)
    tk.Label(edit_frame, text="category:").pack(side="left")

    options = load_options()
    edit_var = tk.StringVar()
    edit_combobox = ttk.Combobox(edit_frame, textvariable=edit_var, values=options, state="readonly", width=20)
    edit_combobox.pack(side="left", padx=5)

    # 선택 이미지 저장용
    selected_image = [None]

    # 이벤트 바인딩
    bind_image_selection(
        img_listbox, image_files, image_folder, img_label, treeview, df,
        screen_width, screen_height, selected_image
    )
    bind_combobox_save(
        edit_combobox, edit_var, selected_image, df, treeview,
        save_csv, folder_path, csv_file
    )
