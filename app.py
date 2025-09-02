# app.py
import tkinter as tk
from module.page_modules.main_screen import open_main_screen

def main():
    root = tk.Tk()
    root.title("메인 화면")
    root.geometry("400x400")

    # 기능 선택 화면 로딩
    open_main_screen(root)

    root.mainloop()

if __name__ == "__main__":
    main()