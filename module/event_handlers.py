from PIL import Image, ImageTk


def bind_image_selection(img_listbox, image_files, image_folder, img_label, treeview, df,
                         screen_width, screen_height, selected_image):
    """이미지 선택 이벤트 처리"""
    def show_selected_image(event=None):
        if not img_listbox.curselection():
            return
        idx = img_listbox.curselection()[0]
        img_name = image_files[idx]
        img_path = f"{image_folder}/{img_name}"

        # 이미지 로드 및 썸네일
        img = Image.open(img_path)
        max_width = int(screen_width * 0.6)
        max_height = int(screen_height * 0.5)
        img.thumbnail((max_width, max_height))
        photo = ImageTk.PhotoImage(img)

        img_label.config(image=photo, text="")
        img_label.image = photo
        selected_image[0] = img_name

        # Treeview 갱신
        update_treeview(treeview, df, img_name)

    img_listbox.bind("<<ListboxSelect>>", show_selected_image)


def update_treeview(treeview, df, img_name):
    """Treeview 업데이트"""
    for item in treeview.get_children():
        treeview.delete(item)
    filtered = df[df['Image'] == img_name]
    for _, row in filtered.iterrows():
        treeview.insert("", "end", values=list(row))


def bind_combobox_save(edit_combobox, edit_var, selected_image, df, treeview,
                       save_csv, folder_path, csv_file):
    """콤보박스 선택 이벤트 처리"""
    def save_edit(event=None):
        img_name = selected_image[0]
        if img_name is None:
            return
        new_value = edit_var.get()
        if not new_value:
            return

        # Treeview 업데이트
        for item_id in treeview.get_children():
            values = list(treeview.item(item_id, "values"))
            values[df.columns.get_loc("category")] = new_value
            treeview.item(item_id, values=values)

        # DataFrame 업데이트
        df.loc[df["Image"] == img_name, "category"] = new_value

        # CSV 저장
        save_csv(df, folder_path, csv_file)

        # 콤보박스 초기화
        edit_var.set("")

    edit_combobox.bind("<<ComboboxSelected>>", save_edit)
