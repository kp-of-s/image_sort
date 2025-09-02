import tkinter as tk
from tkinter import scrolledtext
import threading
from module.image_sort_module import image_sorting

def open_sort_progress_page(root, folder_path):
    """
    정렬 작업 진행 페이지
    :param root: Tk 루트 또는 부모 프레임
    :param sort_function: 정렬 작업을 수행할 함수
    :param args, kwargs: 정렬 함수에 전달할 인자
    """
    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    tk.Label(frame, text="정렬 진행 중...", font=("Arial", 14)).pack(pady=10)

    txt_box = scrolledtext.ScrolledText(frame, width=80, height=20, state='normal')
    txt_box.pack(padx=10, pady=10, fill="both", expand=True)

    def log(message):
        txt_box.insert(tk.END, message + "\n")
        txt_box.see(tk.END)
        txt_box.update()

    # 백그라운드에서 정렬 수행
    def run_sort():
        # 예: sort_function 내부에서 log(message)를 호출하도록 수정 가능
        # 테스트용 루프
        image_sorting(folder_path)
        log("정렬 완료!")

    threading.Thread(target=run_sort, daemon=True).start()

    return frame