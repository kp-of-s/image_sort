import tkinter as tk
from tkinter import scrolledtext
import threading
import pandas as pd
from module.image_sort_module import image_sorting
from module.text_sort_module import text_sorting
from module.category_sort_module import category_sorting
from module.components.home_button import go_main
from util.path_utils import get_config_path, folder_to_csv_name

def open_sort_progress_page(root, dest_paths):
    """
    정렬 작업 진행 페이지
    :param root: Tk 루트 또는 부모 프레임
    :param dest_path: 복사된 폴더의 경로 (data/unsorted_{폴더명})
    """
    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    tk.Label(frame, text="정렬 진행 중...", font=("Arial", 14)).pack(pady=10)

    txt_box = scrolledtext.ScrolledText(frame, width=80, height=20, state='normal')
    txt_box.pack(padx=10, pady=10, fill="both", expand=True)

    # 메인 화면 이동 버튼 추가
    home_btn = tk.Button(frame, text="메인 화면으로 돌아가기")
    home_btn.pack(pady=10)

    # 버튼 클릭 시 home 버튼 사용
    home_btn.configure(command=lambda: go_main(root, frame))

    def log(message):
        txt_box.insert(tk.END, message + "\n")
        txt_box.see(tk.END)
        txt_box.update()

    # 백그라운드에서 정렬 수행
    def run_sort():
        import asyncio
        import os
        
        async def wait_for_copy_completion(dest_paths):
            log("폴더 복사 완료 확인 중...")
            
            max_wait_time = 80  # 최대 대기 시간 (초)
            wait_time = 0       
            while wait_time < max_wait_time:
                all_done = True
                
                for dest_path in dest_paths:
                    csv_path = os.path.join(dest_path, folder_to_csv_name(dest_path))
                    print("Checking for:", csv_path)
                    image_path = os.path.join(dest_path, "images")

                    if not (os.path.isfile(csv_path) and os.path.isdir(image_path)):
                        all_done = False

                if all_done:
                    log("모든 폴더 복사 완료 확인됨!")
                    return True

                await asyncio.sleep(1)
                wait_time += 1

            log("오류: 폴더 복사 완료를 확인할 수 없습니다.")
            return False
        
        async def column_check(dest_path):
            try:
                file_name = folder_to_csv_name(dest_path)
                log(f"{file_name} 열 검사 중...")
                 # 파일 경로
                csv_column_check = os.path.join(get_config_path(), "csv_column_check.txt")
                csv_file_path = os.path.join(dest_path, file_name)
                df = pd.read_csv(csv_file_path, encoding="utf-8-sig")
                column_list = []
                with open(csv_column_check, "r", encoding="utf-8") as f:
                    content = f.read()
                    column_list = [item.strip() for item in content.split(",") if item.strip()]
                column_list.append('autoSortRow')

                # df의 칼람명 중, column_list에 있는 칼람이 없다면 추가
                for col in column_list:
                    if col not in df.columns:
                        df[col] = ""
                        log(f"열 '{col}'이(가) CSV에 없어서 추가되었습니다.")

                df.to_csv(csv_file_path, index=False, encoding="utf-8-sig")

                log("CSV 열 검사 완료!")
            except Exception as e:
                log(f"CSV 열 검사 중 오류 발생: {str(e)}")

        async def run_text_sorting(dest_path):
            """텍스트 분류 실행"""
            log("텍스트 분류 시작...")
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, text_sorting, dest_path, log)
                log("텍스트 분류 완료!")
            except Exception as e:
                log(f"텍스트 분류 중 오류 발생: {str(e)}")

        async def run_category_sorting(dest_path):
            """텍스트 분류 실행"""
            log("텍스트 분류 시작...")
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, category_sorting, dest_path, log)
                log("카테고리 분류 완료!")
            except Exception as e:
                log(f"카테고리 분류 중 오류 발생: {str(e)}")
        
        async def run_image_sorting(dest_path):
            """이미지 분류 실행"""
            log("이미지 분류 시작...")
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, image_sorting, dest_path, log)
                log("정렬 완료!")
            except Exception as e:
                log(f"정렬 중 오류 발생: {str(e)}")

        async def rename_sorted_folder(dest_path):
            # 폴더의 마지막 부분(폴더명) 가져오기
            folder_name = os.path.basename(dest_path)
            
            if '_' in folder_name:
                new_folder_name = folder_name.split('_', 1)[1]
                new_path = os.path.join(os.path.dirname(dest_path), new_folder_name)
                
                # 폴더 이름 변경
                os.rename(dest_path, new_path)
                log(f"폴더 이름이 변경되었습니다: {new_folder_name}")
            else:
                log("폴더 이름 변경에 문제가 발생했습니다.")

        
        async def main():
            """메인 비동기 함수"""
            home_btn.config(state="disabled")
            if await wait_for_copy_completion(dest_paths):
                for dest_path in dest_paths:
                    await column_check(dest_path)
                    await run_text_sorting(dest_path)
                    await run_category_sorting(dest_path)
                    # await run_image_sorting(dest_path)
                    await rename_sorted_folder(dest_path)
            home_btn.config(state="normal")
        
        # 비동기 함수 실행
        asyncio.run(main())

    threading.Thread(target=run_sort, daemon=True).start()

    return frame