import tkinter as tk
from tkinter import scrolledtext
import threading
from module.image_sort_module import image_sorting
from module.text_sort_module import text_sorting
from module.components.home_button import go_main

def open_sort_progress_page(root, dest_path):
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
        
        async def wait_for_copy_completion():
            """비동기적으로 복사 완료를 기다림 (CSV 위치 기준 확인)"""
            log("폴더 복사 완료 확인 중...")
            
            max_wait_time = 30  # 최대 30초 대기
            wait_time = 0
            
            while wait_time < max_wait_time:
                if os.path.exists(dest_path):
                    csv_folder = None
                    for root, dirs, files in os.walk(dest_path):
                        for file in files:
                            if file.endswith(".csv"):
                                csv_folder = root
                                break
                        if csv_folder:
                            break

                    if csv_folder:
                        image_folder = os.path.join(csv_folder, "image")
                        csv_file = next((os.path.join(csv_folder, f) for f in os.listdir(csv_folder) if f.endswith(".csv")), None)
                        
                        if os.path.exists(image_folder) and csv_file and os.path.exists(csv_file):
                            log("폴더 복사 완료 확인됨!")
                            return True
                        else:
                            log(f"파일 확인 중... ({wait_time}s)")
                    else:
                        log(f"CSV 파일을 찾는 중... ({wait_time}s)")
                else:
                    log(f"폴더 확인 중... ({wait_time}s)")
                
                await asyncio.sleep(1)
                wait_time += 1
            
            log("오류: 폴더 복사 완료를 확인할 수 없습니다.")
            return False


        async def run_text_sorting():
            """텍스트 분류 실행"""
            log("텍스트 분류 시작...")
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, text_sorting, dest_path, log)
                log("텍스트 분류 완료!")
            except Exception as e:
                log(f"텍스트 분류 중 오류 발생: {str(e)}")
        
        async def run_image_sorting():
            """이미지 분류 실행"""
            log("이미지 분류 시작...")
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, image_sorting, dest_path, log)
                log("정렬 완료!")
            except Exception as e:
                log(f"정렬 중 오류 발생: {str(e)}")

        async def rename_sorted_folder():
            # 폴더의 마지막 부분(폴더명) 가져오기
            folder_name = os.path.basename(dest_path)
            
            if '_' in folder_name:
                new_folder_name = folder_name.split('_', 1)[1]
                new_path = os.path.join(os.path.dirname(dest_path), new_folder_name)
                
                # 폴더 이름 변경
                os.rename(dest_path, new_path)
                log(f"폴더 이름이 변경되었습니다: {dest_path} -> {new_path}")
            else:
                log("폴더 이름 변경에 문제가 발생했습니다.")

        
        async def main():
            """메인 비동기 함수"""
            from module.page_modules.main_screen import open_main_screen
            home_btn.config(state="disabled")
            if await wait_for_copy_completion():
                await run_text_sorting()
                await run_image_sorting()
                await rename_sorted_folder()
                home_btn.config(state="normal")
        
        # 비동기 함수 실행
        asyncio.run(main())

    threading.Thread(target=run_sort, daemon=True).start()

    return frame