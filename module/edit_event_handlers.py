import os
import tkinter as tk
import pandas as pd
from PIL import Image, ImageTk

from util.csv_utils import save_csv
from module.db_uploader import execute_db_upload

def bind_image_selection(img_listbox, image_files, image_folder, img_label, df,
                         screen_width, screen_height, selected_image, type1_label, type2_label, address_label, name_label):
    def show_selected_image(event=None):
        if not img_listbox.curselection():
            return
        idx = img_listbox.curselection()[0]
        img_name = image_files[idx]
        img_path = os.path.join(image_folder, img_name)

        img = Image.open(img_path)
        max_width = int(screen_width * 0.5)
        max_height = int(screen_height * 0.5)
        img.thumbnail((max_width, max_height))
        photo = ImageTk.PhotoImage(img)

        img_label.config(image=photo, text="")
        img_label.image = photo
        selected_image[0] = img_name

        # 데이터에서 해당 이미지 행 찾기
        row = df[df['image'] == img_name]
        if not row.empty:
            name = row.iloc[0].get('name', '-')
            type1 = row.iloc[0].get('type1', '-')
            type2 = row.iloc[0].get('type2', '-')
            adrass = row.iloc[0].get('address', '-')
        else:
            type1, type2, adrass, name = '-', '-', '-'

        name_label.config(text=f"name: {name}")
        type1_label.config(text=f"type1: {type1}")
        type2_label.config(text=f"type2: {type2}")
        address_label.config(text=f"Address: {adrass}")

    def move_to_next_image(event=None):
        selected_idx = img_listbox.curselection()
        if selected_idx:
            next_idx = (selected_idx[0] + 1) % len(image_files)  # 순환하도록 처리
            img_listbox.select_clear(0, "end")
            img_listbox.select_set(next_idx)
            img_listbox.activate(next_idx)
            show_selected_image()

    def move_to_previous_image(event=None):
        selected_idx = img_listbox.curselection()
        if selected_idx:
            prev_idx = (selected_idx[0] - 1) % len(image_files)  # 순환하도록 처리
            img_listbox.select_clear(0, "end")
            img_listbox.select_set(prev_idx)
            img_listbox.activate(prev_idx)
            show_selected_image()

    # 마우스 클릭으로 이미지 선택
    img_listbox.bind("<<ListboxSelect>>", show_selected_image)

    # 스페이스바로 이미지 넘기기 (다음 이미지로)
    img_listbox.bind("<space>", move_to_next_image)

    # 왼쪽 화살표로 이미지 넘기기 (이전 이미지로)
    img_listbox.bind("<Left>", move_to_previous_image)


def bind_type1_buttons(options, type1_frame, type2_frame,
                       df, selected_image, type1_label, type2_label,
                       folder_path, csv_file):
    for key in options.keys():
        btn = tk.Button(type1_frame, text=key, width=10,
                        command=lambda k=key: select_type1(
                            k, options, type2_frame, df, selected_image,
                            type1_label, type2_label, folder_path, csv_file))
        btn.pack(pady=2)


def select_type1(type1_value, options, type2_frame, df, selected_image,
                 type1_label, type2_label, folder_path, csv_file):
    update_type(df, selected_image, "type1", type1_value,
                type1_label, type2_label, folder_path, csv_file)

    # type2 버튼 초기화 후 새로 생성
    for widget in type2_frame.winfo_children():
        widget.destroy()
    tk.Label(type2_frame, text="Type2 선택:", font=("Arial", 10, "bold")).pack()

    for val in options[type1_value]:
        btn = tk.Button(type2_frame, text=val, width=12,
                        command=lambda v=val: update_type(
                            df, selected_image, "type2", v,
                            type1_label, type2_label, folder_path, csv_file))
        btn.pack(pady=2)


def update_type(df, selected_image, column_name, new_value,
                type1_label, type2_label, folder_path, csv_file):
    if not selected_image[0]:
        return
    img_name = selected_image[0]
    idx = df[df['image'] == img_name].index
    if not idx.empty:
        df.at[idx[0], column_name] = new_value
        save_csv(df, folder_path, csv_file)

        # 라벨 갱신
        current_row = df.loc[idx[0]]
        type1_label.config(text=f"type1: {current_row.get('type1', '-')}")
        type2_label.config(text=f"type2: {current_row.get('type2', '-')}")

def bind_unclassified_button(
        df, selected_image, type1_label, type2_label, folder_path, csv_file, Unclassified_frame
    ):
    def on_click():
        update_type(df, selected_image, "type1", "미분류",
                    type1_label, type2_label, folder_path, csv_file)
        update_type(df, selected_image, "type2", "미분류",
                    type1_label, type2_label, folder_path, csv_file)
        
    btn = tk.Button(Unclassified_frame, text="미분류", width=10, command=on_click)

    btn.pack(pady=2)


def copy_current_row(self, df, selected_image, folder_path, csv_file_name, img_listbox, image_files):
    """
    현재 선택된 행의 데이터를 CSV 마지막 줄에 추가하고 이미지 리스트를 갱신합니다.
    """
    if not selected_image[0]:
        tk.messagebox.showwarning("경고", "먼저 이미지를 선택해주세요.")
        return

    img_name = selected_image[0]
    row = df[df['image'] == img_name]

    if not row.empty:
        # 현재 선택된 행의 데이터를 추출
        row_to_add = row.iloc[0].copy()
        
        # 새로운 행으로 추가
        df.loc[len(df)] = row_to_add
        
        # CSV 파일에 저장
        save_csv(df, folder_path, csv_file_name)
        
        # 이미지 리스트 갱신
        img_listbox.delete(0, tk.END)
        df_sorted = df.sort_values(["address", "name"]).reset_index(drop=True)
        image_files.clear()
        new_image_files = [
            str(img) for img in df_sorted["image"].tolist()
            if pd.notna(img) and os.path.exists(os.path.join(folder_path, "images", str(img)))
        ]
        image_files.extend(new_image_files)
        for idx, f in enumerate(image_files):
            img_listbox.insert(tk.END, f"{idx+1}. {f}")
        
        # 새로 추가된 항목을 선택하도록 처리
        new_idx = image_files.index(img_name)
        img_listbox.select_set(new_idx)
        img_listbox.activate(new_idx)
        img_listbox.see(new_idx)
        
        tk.messagebox.showinfo("추가 완료", f"'{img_name}'의 데이터가 CSV 파일에 성공적으로 추가되었습니다.")
        
        # **다음 이미지로 자동 이동 (추가된 부분)**
        selected_idx = img_listbox.curselection()
        if selected_idx:
            next_idx = (selected_idx[0] + 1) % len(image_files)
            img_listbox.select_clear(0, "end")
            img_listbox.select_set(next_idx)
            img_listbox.activate(next_idx)
            self.show_selected_image() # 다음 이미지 정보 표시
    else:
        tk.messagebox.showerror("오류", "선택된 이미지에 해당하는 데이터를 찾을 수 없습니다.")



def handle_DB_upload(csv_file):
    if tk.messagebox.askyesno("확인", "정말로 DB에 업로드하시겠습니까?"):
        try:
            result = execute_db_upload(csv_file)
            # result = None
            # print("업로드 실행")
            
            if result:
                tk.messagebox.showerror("업로드 실패", result)
            else:
                tk.messagebox.showinfo("완료", "DB 업로드가 완료되었습니다.")
        except Exception as e:
            tk.messagebox.showerror("치명적인 오류", f"DB 업로드 중 예기치 않은 오류가 발생했습니다: {e}")