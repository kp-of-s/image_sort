import os
import tkinter as tk
import pandas as pd
from PIL import Image, ImageTk
import webbrowser

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
        if pd.notna(img) and is_valid_url(str(img))
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

def is_valid_url(url):
    """URL이 유효한지 확인합니다."""
    try:
        import re
        # 간단한 URL 패턴 검증
        url_pattern = re.compile(
            r'^https?://'  # http:// 또는 https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # 도메인
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
            r'(?::\d+)?'  # 포트
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None
    except:
        return False

def open_webpage_in_browser(url, browser_tab_id):
    """기본 브라우저에서 웹페이지를 열되, 가능한 한 같은 창에서 열도록 합니다."""
    try:
        # 첫 번째 웹페이지가 아니면 새 탭으로 열기
        if browser_tab_id is None:
            # 첫 번째 웹페이지는 새 창으로 열기
            return webbrowser.open(url, new=1, autoraise=True)
        else:
            # 이후 웹페이지들은 새 탭으로 열기 (가능한 경우)
            webbrowser.open(url, new=2, autoraise=True)
            return browser_tab_id
    except Exception as e:
        print(f"브라우저 열기 실패: {e}")
        # 실패 시 기본 방식으로 열기
        try:
            webbrowser.open(url)
            return browser_tab_id
        except:
            print("브라우저를 열 수 없습니다.")
            return browser_tab_id

def update_info_display(edit_screen_instance):
    """선택된 항목의 정보만 업데이트합니다 (웹페이지 열기 없이)."""
    if not edit_screen_instance.img_listbox.curselection():
        return
    
    idx = edit_screen_instance.img_listbox.curselection()[0]
    
    if idx >= len(edit_screen_instance.original_df_indices):
        return

    original_df_index = edit_screen_instance.original_df_indices[idx]
    row = edit_screen_instance.df.loc[original_df_index]
    
    webpage_url = row['image']
    edit_screen_instance.selected_image[0] = webpage_url
    
    # 상태 업데이트 (웹페이지 열기 없이)
    if is_valid_url(webpage_url):
        edit_screen_instance.status_label.config(text=f"선택된 웹페이지:\n{webpage_url}")
    else:
        edit_screen_instance.status_label.config(text=f"유효하지 않은 URL:\n{webpage_url}")
    
    edit_screen_instance.name_label.config(text=f"name: {row.get('name', '-')}")
    edit_screen_instance.type1_label.config(text=f"type1: {row.get('type1', '-')}")
    edit_screen_instance.type2_label.config(text=f"type2: {row.get('type2', '-')}")
    edit_screen_instance.address_label.config(text=f"address: {row.get('address', '-')}")

def show_selected_webpage(edit_screen_instance):
    """선택된 리스트 항목에 해당하는 웹페이지를 브라우저에서 엽니다."""
    if not edit_screen_instance.img_listbox.curselection():
        return
    
    idx = edit_screen_instance.img_listbox.curselection()[0]
    
    if idx >= len(edit_screen_instance.original_df_indices):
        return

    original_df_index = edit_screen_instance.original_df_indices[idx]
    row = edit_screen_instance.df.loc[original_df_index]
    
    webpage_url = row['image']
    
    # URL 유효성 검사
    if not is_valid_url(webpage_url):
        edit_screen_instance.status_label.config(text=f"유효하지 않은 URL:\n{webpage_url}")
        edit_screen_instance.selected_image[0] = None
        return
    
    edit_screen_instance.selected_image[0] = webpage_url
    
    # 상태 업데이트
    edit_screen_instance.status_label.config(text=f"브라우저에서 열리는 중...\n{webpage_url}")
    
    # 브라우저에서 웹페이지 열기
    edit_screen_instance.browser_tab_id = open_webpage_in_browser(webpage_url, edit_screen_instance.browser_tab_id)
    
    # 상태 업데이트
    edit_screen_instance.status_label.config(text=f"브라우저에서 열림:\n{webpage_url}")
    
    # 정보 업데이트
    update_info_display(edit_screen_instance)

def on_listbox_click(edit_screen_instance):
    """리스트박스를 직접 클릭했을 때 웹페이지를 엽니다."""
    # 약간의 지연을 두어 선택이 완료된 후 실행
    edit_screen_instance.win.after(100, lambda: show_selected_webpage(edit_screen_instance))

def move_to_next_image(edit_screen_instance):
    """다음 이미지로 이동합니다."""
    selected_idx_tuple = edit_screen_instance.img_listbox.curselection()
    if selected_idx_tuple:
        next_idx = (selected_idx_tuple[0] + 1) % len(edit_screen_instance.image_files)
        edit_screen_instance.img_listbox.select_clear(0, "end")
        edit_screen_instance.img_listbox.select_set(next_idx)
        edit_screen_instance.img_listbox.activate(next_idx)
        edit_screen_instance.img_listbox.see(next_idx)
        show_selected_webpage(edit_screen_instance)

def move_to_previous_image(edit_screen_instance):
    """이전 이미지로 이동합니다."""
    selected_idx_tuple = edit_screen_instance.img_listbox.curselection()
    if selected_idx_tuple:
        prev_idx = (selected_idx_tuple[0] - 1 + len(edit_screen_instance.image_files)) % len(edit_screen_instance.image_files)
        edit_screen_instance.img_listbox.select_clear(0, "end")
        edit_screen_instance.img_listbox.select_set(prev_idx)
        edit_screen_instance.img_listbox.activate(prev_idx)
        edit_screen_instance.img_listbox.see(prev_idx)
        show_selected_webpage(edit_screen_instance)