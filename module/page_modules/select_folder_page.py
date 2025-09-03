import tkinter as tk
from tkinter import ttk, messagebox
import os
from module.page_modules.edit_screen import open_edit_screen
from util.path_utils import folder_to_csv_name

def open_select_folder_page(root, data_path):
    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True)

    tree = ttk.Treeview(frame)
    tree.pack(fill="both", expand=True)

    # 첫 번째 컬럼 설정
    tree.heading("#0", text="폴더 탐색기", anchor="w")

    # 루트 폴더 추가
    root_node = tree.insert("", "end", text=os.path.basename(data_path), open=True, values=[data_path])

    # 하위 폴더/파일 트리 채우기
    def populate_tree(parent_node, parent_path):
        try:
            for name in os.listdir(parent_path):
                for name in os.listdir(parent_path):
                    if name.startswith("unsorted_"):
                        continue
                full_path = os.path.join(parent_path, name)
                if os.path.isdir(full_path):
                    node = tree.insert(parent_node, "end", text=name, values=[full_path])
                    # 하위 폴더가 있으면 더미 노드 추가
                    if any(os.path.isdir(os.path.join(full_path, d)) for d in os.listdir(full_path)):
                        tree.insert(node, "end", text="dummy")
        except PermissionError:
            pass

    populate_tree(root_node, data_path)

    # 트리 확장 시 동적 로드
    def on_open(event):
        node = tree.focus()
        children = tree.get_children(node)
        if len(children) == 1 and tree.item(children[0], "text") == "dummy":
            tree.delete(children[0])
            parent_path = tree.item(node, "values")[0]
            populate_tree(node, parent_path)

    tree.bind("<<TreeviewOpen>>", on_open)

    # 클릭 시 CSV 파일 확인
    def on_select(event):
        node = tree.focus()
        folder_path = tree.item(node, "values")[0]
        if os.path.isdir(folder_path):
            csv_files = [f for f in os.listdir(folder_path) if f.endswith(".csv")]
            if csv_files:
                # 여기서 open_edit_screen 호출 가능
                open_edit_screen(folder_path, folder_to_csv_name(folder_path))

    tree.bind("<<TreeviewSelect>>", on_select)

    return frame

# 실행 예시
if __name__ == "__main__":
    root = tk.Tk()
    root.title("CSV 탐색기")
    root.geometry("600x400")
    open_select_folder_page(root, "C:/your/data/path")  # 데이터 폴더 경로
    root.mainloop()
