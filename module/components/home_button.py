# module/components/home_button.py
import tkinter as tk

def create_home_button(parent, go_home_command):
    """
    클릭 시 항상 main_screen을 불러와 화면 전환
    parent._current_frame를 사용해 기존 화면 숨김 처리
    """
    return tk.Button(parent, text="홈으로", command=go_home_command)
