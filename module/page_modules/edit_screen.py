import os
import tkinter as tk
from tkinter import ttk
from util.csv_utils import load_csv, save_csv
from util.options_utils import load_options
import pandas as pd

# 이벤트 핸들러 함수들을 별도로 import 합니다.
from module.edit_event_handlers import (
    bind_type1_buttons,
    bind_unclassified_button,
    handle_DB_upload,
    copy_current_row,
    is_valid_url,
    open_webpage_in_browser,
    update_info_display,
    show_selected_webpage,
    on_listbox_click,
    move_to_next_image,
    move_to_previous_image,
)

class EditScreen:
    def __init__(self, folder_path, csv_file_name):
        self.folder_path = folder_path
        self.csv_file_name = csv_file_name
        self.csv_file = os.path.join(folder_path, csv_file_name)
        self.image_folder = os.path.join(folder_path, "images")

        self.df = load_csv(self.folder_path, self.csv_file_name)
        self.options = load_options()
        self.selected_image = [None]
        self.image_files = []
        self.original_df_indices = []

        for col in self.df.columns:
                if self.df[col].isna().all():  # 모든 값이 None/NaN인 경우
                    self.df[col] = self.df[col].astype("string")
        
        # 브라우저 관련 변수
        self.browser_tab_id = None  # 기존 탭 ID 저장

        self.win = tk.Toplevel()
        self.win.title(f"편집 화면 - {os.path.basename(self.folder_path)}")

        self._create_widgets()
        self._get_and_update_image_files()
        self._bind_events()

    def _get_and_update_image_files(self):
        """
        DataFrame을 정렬하고, 리스트박스에 표시할 파일 리스트와 원본 인덱스 매핑을 생성합니다.
        """
        df_sorted = self.df.sort_values(["address", "name"])

        self.image_files = []
        self.original_df_indices = []

        # 각 행을 순회하며 유효한 이미지 URL과 인덱스만 추가합니다.
        for index, row in df_sorted.iterrows():
            img_url = str(row["image"])
            
            # URL이 유효할 때만 리스트에 추가합니다.
            if pd.notna(img_url) and is_valid_url(img_url):
                self.image_files.append(img_url)
                self.original_df_indices.append(index)
        
        self._update_listbox_content()
    
    def _update_type(self, column_name, new_value):
        if not self.img_listbox.curselection():
            return
        
        idx = self.img_listbox.curselection()[0]
        
        # original_df_indices를 사용하여 데이터프레임의 실제 인덱스를 찾습니다.
        target_index = self.original_df_indices[idx]

        try:
            # self.df를 직접 사용하여 수정합니다.
            if target_index is not None and target_index in self.df.index:
                self.df.loc[target_index, column_name] = new_value
                save_csv(self.df, self.folder_path, self.csv_file_name)
            else:
                tk.messagebox.showwarning("경고", f"대상 인덱스({target_index})를 데이터프레임에서 찾을 수 없습니다.")

        except Exception as e:
            tk.messagebox.showerror("데이터 업데이트 오류", f"데이터를 업데이트하는 도중 오류가 발생했습니다: {e}")
            return

        update_info_display(self)


    def _update_listbox_content(self):
        """현재 image_files 리스트를 기반으로 Listbox 내용을 새로 고칩니다."""
        self.img_listbox.delete(0, tk.END)
        for idx, url in enumerate(self.image_files):
            # 해당 행의 name 컬럼 값을 가져와서 표시
            original_df_index = self.original_df_indices[idx]
            row = self.df.loc[original_df_index]
            name_value = row.get('name', f'항목 {idx+1}')
            
            # name이 비어있거나 NaN인 경우 기본값 사용
            if pd.isna(name_value) or name_value == '':
                name_value = f'항목 {idx+1}'
            
            self.img_listbox.insert(tk.END, f"{idx+1}. {name_value}")

    def _create_widgets(self):
        screen_width = self.win.winfo_screenwidth()
        screen_height = self.win.winfo_screenheight()
        win_width = int(screen_width * 0.8)
        win_height = int(screen_height * 0.8)
        self.win.geometry(f"{win_width}x{win_height}")

        self.win.grid_columnconfigure(0, weight=0)
        self.win.grid_columnconfigure(1, weight=1)

        self.list_frame = tk.Frame(self.win, bd=2, relief="solid")
        self.list_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=5, pady=5)
        self.img_listbox = tk.Listbox(self.list_frame, width=30)
        self.img_listbox.pack(fill="both", expand=True)

        self.content_frame = tk.Frame(self.win)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.content_frame.grid_rowconfigure(0, weight=1)

        self.web_frame = tk.Frame(self.content_frame, bd=2, relief="solid")
        self.web_frame.pack(fill="both", expand=True)
        
        # 웹페이지 상태 표시를 위한 프레임
        self.status_frame = tk.Frame(self.web_frame, bg="white")
        self.status_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 현재 웹페이지 상태 표시 라벨
        self.status_label = tk.Label(self.status_frame, 
                                   text="웹페이지를 선택하면 자동으로 브라우저에서 열립니다", 
                                   font=("Arial", 12), 
                                   bg="white",
                                   wraplength=600)
        self.status_label.pack(expand=True)

        self.info_frame = tk.Frame(self.content_frame, bd=2, relief="solid")
        self.info_frame.pack(fill="x", padx=5, pady=5)
        tk.Label(self.info_frame, text="선택 항목 정보", font=("Arial", 14, "bold")).pack(pady=10)
        self.name_label = tk.Label(self.info_frame, text="name: -", font=("Arial", 12))
        self.name_label.pack(pady=5)
        self.type1_label = tk.Label(self.info_frame, text="type1: -", font=("Arial", 12))
        self.type1_label.pack(pady=5)
        self.type2_label = tk.Label(self.info_frame, text="type2: -", font=("Arial", 12))
        self.type2_label.pack(pady=5)
        self.address_label = tk.Label(self.info_frame, text="address: -", font=("Arial", 12))
        self.address_label.pack(pady=5)

        self.bottom_frame = tk.Frame(self.content_frame, bd=2, relief="solid")
        self.bottom_frame.pack(fill="x", padx=5, pady=5)
        self.btn_frame = tk.Frame(self.bottom_frame)
        self.btn_frame.pack(pady=10)
        
        self.type1_frame = tk.Frame(self.btn_frame)
        self.type1_frame.pack(side="left", padx=10)
        self.type2_frame = tk.Frame(self.btn_frame)
        self.type2_frame.pack(side="left", padx=10)
        self.Unclassified_frame = tk.Frame(self.btn_frame)
        self.Unclassified_frame.pack(side="left", padx=10)

        tk.Label(self.Unclassified_frame, text="미분류", font=("Arial", 10, "bold")).pack()
        tk.Label(self.type1_frame, text="Type1 선택:", font=("Arial", 10, "bold")).pack()
        tk.Label(self.type2_frame, text="Type2 선택:", font=("Arial", 10, "bold")).pack()

        self.upload_button_frame = tk.Frame(self.bottom_frame, pady=10)
        self.upload_button_frame.pack(side="bottom", fill="x")
        self.copy_button = tk.Button(self.upload_button_frame, text="선택 항목 추가", command=self.handle_copy_row)
        self.copy_button.pack(side="left", padx=10, pady=5)
        self.save_button = tk.Button(self.upload_button_frame, text="데이터베이스에 업로드", command=self.handle_db_upload)
        self.save_button.pack(padx=10, pady=5)


    def _bind_events(self):
        # webpage_selection 로직을 EditScreen 클래스에 통합
        self.img_listbox.bind("<<ListboxSelect>>", lambda e: update_info_display(self))
        self.img_listbox.bind("<Button-1>", lambda e: on_listbox_click(self))
        
        # 방향키 네비게이션 (상/좌=이전, 하/우=다음)
        def handle_prev(e):
            move_to_previous_image(self)
            return "break"
        
        def handle_next(e):
            move_to_next_image(self)
            return "break"
        
        self.img_listbox.bind("<Up>", handle_prev)
        self.img_listbox.bind("<Left>", handle_prev)
        self.img_listbox.bind("<Down>", handle_next)
        self.img_listbox.bind("<Right>", handle_next)
        self.img_listbox.bind("<space>", handle_next)

        # 외부 이벤트 핸들러 함수를 호출하며 필요한 인자를 전달
        bind_type1_buttons(
            self.options,
            self.type1_frame,
            self.type2_frame,
            self,
            self.type1_label,
            self.type2_label
        )
        bind_unclassified_button(
            self,
            self.Unclassified_frame
        )


    def handle_copy_row(self):
        selected_idx_tuple = self.img_listbox.curselection()
        if not selected_idx_tuple:
            tk.messagebox.showwarning("경고", "먼저 이미지를 선택해주세요.")
            return
            
        original_selected_idx = selected_idx_tuple[0]
        
        # copy_current_row 함수 호출하여 복제 수행
        result = copy_current_row(
            self.df, self.img_listbox, self.folder_path, self.csv_file_name, self.original_df_indices
        )
        
        # 반환된 결과로 업데이트
        if len(result) == 3:
            self.df, self.image_files, self.original_df_indices = result
        else:
            return
        
        self._update_listbox_content()
        
        new_item_index = -1
        for i, img_url in enumerate(self.image_files):
            # 복제본은 동일 URL 중 유일하게 'type1'이 비어있는 행입니다.
            # 이 특성을 사용해 인덱스 컬럼 없이 복제본을 찾습니다.
            if img_url == self.image_files[original_selected_idx]:
                # self.df.loc[self.original_df_indices[i]]로 올바른 행에 접근합니다.
                target_row = self.df.loc[self.original_df_indices[i]]
                
                if pd.isna(target_row['type1']):
                    new_item_index = i
                    break
        if new_item_index != -1:
            self.img_listbox.select_clear(0, "end")
            self.img_listbox.select_set(new_item_index)
            self.img_listbox.activate(new_item_index)
            self.img_listbox.see(new_item_index)
            update_info_display(self)
        else:
            self.img_listbox.select_clear(0, "end")
            self.img_listbox.select_set(original_selected_idx)
            self.img_listbox.activate(original_selected_idx)
            update_info_display(self)

    def handle_db_upload(self):
        handle_DB_upload(self.csv_file)

def open_edit_screen(folder_path, csv_file_name):
    EditScreen(folder_path, csv_file_name)