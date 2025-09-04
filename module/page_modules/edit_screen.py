import os
import tkinter as tk
from tkinter import ttk
from util.csv_utils import load_csv
from util.image_utils import get_image_files
from util.options_utils import load_options
import keyboard
from module.edit_event_handlers import (
    bind_image_selection,
    bind_type1_buttons,
    handle_DB_upload
)

def open_edit_screen(folder_path, csv_file_name):
    """편집 화면 생성"""

    csv_file = os.path.join(folder_path, csv_file_name)

    # 데이터 로드
    df = load_csv(folder_path, csv_file_name)
    options = load_options()

    # 윈도우 생성
    win = tk.Toplevel()
    win.title(f"편집 화면 - {os.path.basename(folder_path)}")

    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    win_width = int(screen_width * 0.8)
    win_height = int(screen_height * 0.8)
    win.geometry(f"{win_width}x{win_height}")

    # 레이아웃 설정
    win.grid_columnconfigure(0, weight=0)  # 리스트 열은 고정
    win.grid_columnconfigure(1, weight=1)  # 내용물 열은 확장

    # 이미지 리스트 프레임 (왼쪽에 고정)
    list_frame = tk.Frame(win, bd=2, relief="solid")
    # grid를 사용하여 0행, 0열에 배치하고, 2개 행에 걸쳐 전체 높이를 차지하게 합니다.
    list_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=5, pady=5)
    img_listbox = tk.Listbox(list_frame, width=30)
    img_listbox.pack(fill="both", expand=True)
    image_folder = os.path.join(folder_path, "images")
    image_files = get_image_files(image_folder)
    for idx, f in enumerate(image_files):
        img_listbox.insert(tk.END, f"{idx+1}. {f}")

    # 메인 콘텐츠 컨테이너 (오른쪽에 배치)
    content_frame = tk.Frame(win)
    # grid를 사용하여 0행, 1열에 배치하고, 창의 전체 공간을 차지하게 합니다.
    content_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
    content_frame.grid_rowconfigure(0, weight=1) # 이 프레임 내부의 행 설정

    # --- 이 아래부터는 content_frame 내부에 pack으로 수직 배치 ---

    # 이미지 표시 프레임
    img_frame = tk.Frame(content_frame, bd=2, relief="solid")
    img_frame.pack(fill="both", expand=True)
    img_label = tk.Label(img_frame, text="이미지를 선택하세요")
    img_label.pack(fill="none", expand=False)

    # 정보 표시 프레임
    info_frame = tk.Frame(content_frame, bd=2, relief="solid")
    info_frame.pack(fill="x", padx=5, pady=5)
    tk.Label(info_frame, text="선택 항목 정보", font=("Arial", 14, "bold")).pack(pady=10)
    type1_label = tk.Label(info_frame, text="type1: -", font=("Arial", 12))
    type1_label.pack(pady=5)
    type2_label = tk.Label(info_frame, text="type2: -", font=("Arial", 12))
    type2_label.pack(pady=5)
    address_label = tk.Label(info_frame, text="address: -", font=("Arial", 12))
    address_label.pack(pady=5)

    # 버튼 영역 프레임
    bottom_frame = tk.Frame(content_frame, bd=2, relief="solid")
    bottom_frame.pack(fill="x", padx=5, pady=5)

    # type1 / type2 버튼 컨테이너
    btn_frame = tk.Frame(bottom_frame)
    btn_frame.pack(pady=10)
    type1_frame = tk.Frame(btn_frame)
    type1_frame.pack(side="left", padx=10)
    type2_frame = tk.Frame(btn_frame)
    type2_frame.pack(side="left", padx=10)

    tk.Label(type1_frame, text="Type1 선택:", font=("Arial", 10, "bold")).pack()
    tk.Label(type2_frame, text="Type2 선택:", font=("Arial", 10, "bold")).pack()

    # 선택 이미지 상태
    selected_image = [None]

    # 이벤트 바인딩
    bind_image_selection(
        img_listbox, image_files, image_folder, img_label,
        df, screen_width, screen_height, selected_image,
        type1_label, type2_label, address_label
    )

    bind_type1_buttons(
        options, type1_frame, type2_frame,
        df, selected_image, type1_label, type2_label,
        folder_path, csv_file_name
    )

     # 데이터베이스 업로드 버튼 프레임
    upload_button_frame = tk.Frame(bottom_frame, pady=10)
    upload_button_frame.pack(side="bottom", fill="x")

    # 업로드 버튼
    save_button = tk.Button(upload_button_frame, text="데이터베이스에 업로드", command=lambda: handle_DB_upload(csv_file))
    save_button.pack(padx=10, pady=5)