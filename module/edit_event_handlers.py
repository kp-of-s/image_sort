import os
import tkinter as tk
import pandas as pd
from PIL import Image, ImageTk

from util.csv_utils import save_csv
from module.db_uploader import execute_db_upload

def bind_type1_buttons(options, type1_frame, type2_frame,
                       edit_screen_instance, type1_label, type2_label):
    def select_type1(type1_value):
        # EditScreen 인스턴스의 _update_type 메서드를 호출
        edit_screen_instance._update_type("type1", type1_value)
        
        # type2 버튼 초기화 후 새로 생성
        for widget in type2_frame.winfo_children():
            widget.destroy()
        tk.Label(type2_frame, text="Type2 선택:", font=("Arial", 10, "bold")).pack()
        
        for val in options[type1_value]:
            btn = tk.Button(type2_frame, text=val, width=12,
                            command=lambda v=val: edit_screen_instance._update_type("type2", v))
            btn.pack(pady=2)
    
    for key in options.keys():
        btn = tk.Button(type1_frame, text=key, width=10,
                        command=lambda k=key: select_type1(k))
        btn.pack(pady=2)

def bind_unclassified_button(edit_screen_instance, Unclassified_frame):
    def on_click():
        # type1, type2 모두 "미분류"로 설정하기 위해
        # EditScreen 인스턴스의 _update_type 메서드를 호출
        edit_screen_instance._update_type("type1", "미분류")
        edit_screen_instance._update_type("type2", "미분류")
        
    btn = tk.Button(Unclassified_frame, text="미분류", width=10, command=on_click)
    btn.pack(pady=2)

def copy_current_row(df, img_listbox, folder_path, csv_file_name, original_df_indices):
    """
    선택된 항목의 행을 복제하고, 변경된 데이터와 UI 갱신에 필요한 리스트들을 반환합니다.
    """
    selected_idx_tuple = img_listbox.curselection()
    if not selected_idx_tuple:
        tk.messagebox.showwarning("경고", "먼저 이미지를 선택해주세요.")
        return df, [], []

    selected_idx = selected_idx_tuple[0]
    
    # 1. 원본 데이터프레임의 인덱스를 가져옵니다.
    original_df_index_to_copy = original_df_indices[selected_idx]
    
    # 2. 행을 복사합니다.
    row_to_add = df.loc[original_df_index_to_copy].copy()
    row_to_add['type1'] = None
    row_to_add['type2'] = None
    
    # 3. 새로운 인덱스를 생성하여 복제본을 추가합니다.
    new_index = df.index.max() + 1 if not df.empty else 0
    row_to_add.name = new_index
    df = pd.concat([df, pd.DataFrame([row_to_add])])
    
    save_csv(df, folder_path, csv_file_name)

    # 4. 데이터프레임을 정렬하고, 인덱스를 유지한 채로 반환합니다.
    df_sorted = df.sort_values(["address", "name"])

    new_image_files = [
        str(img) for img in df_sorted["image"].tolist()
        if pd.notna(img) and os.path.exists(os.path.join(folder_path, "images", str(img)))
    ]
    
    # 5. 정렬된 순서에 맞는 인덱스 리스트를 반환합니다.
    new_original_df_indices = df_sorted.index.tolist()
    
    return df, new_image_files, new_original_df_indices

def handle_DB_upload(csv_file):
    if tk.messagebox.askyesno("확인", "정말로 DB에 업로드하시겠습니까?"):
        try:
            result = execute_db_upload(csv_file)
            if result:
                tk.messagebox.showerror("업로드 실패", result)
            else:
                tk.messagebox.showinfo("완료", "DB 업로드가 완료되었습니다.")
        except Exception as e:
            tk.messagebox.showerror("치명적인 오류", f"DB 업로드 중 예기치 않은 오류가 발생했습니다: {e}")