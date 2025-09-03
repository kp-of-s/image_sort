# module/components/home_button.py
import tkinter as tk

def go_main(root, current_frame):
    from module.page_modules.main_screen import open_main_screen
    """현재 페이지를 숨기고 메인 화면으로 전환"""
    current_frame.pack_forget()
    current_frame.destroy()  # 필요에 따라 제거
    open_main_screen(root)

def add_back_to_main_button(root, current_frame, text="메인 화면으로 돌아가기"):
    """현재 페이지에 메인 화면 이동 버튼 추가"""
    btn = tk.Button(current_frame, text=text,
                    command=lambda: go_main(root, current_frame))
    btn.pack(pady=10)  # 위치와 스타일은 필요에 따라 조정
