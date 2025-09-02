import os
import tkinter as tk
from PIL import Image, ImageTk
from util.csv_utils import save_csv

def bind_image_selection(img_listbox, image_files, image_folder, img_label, df,
                         screen_width, screen_height, selected_image, type1_label, type2_label, address_label):
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
            type1 = row.iloc[0].get('type1', '-')
            type2 = row.iloc[0].get('type2', '-')
            adrass = row.iloc[0].get('address', '-')
        else:
            type1, type2, adrass = '-', '-'

        type1_label.config(text=f"type1: {type1}")
        type2_label.config(text=f"type2: {type2}")

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
