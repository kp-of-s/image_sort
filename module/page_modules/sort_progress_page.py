import tkinter as tk
from tkinter import scrolledtext
import threading
from module.image_sort_module import image_sorting

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

    def log(message):
        txt_box.insert(tk.END, message + "\n")
        txt_box.see(tk.END)
        txt_box.update()

    # 백그라운드에서 정렬 수행
    def run_sort():
        import asyncio
        import os
        
        async def wait_for_copy_completion():
            """비동기적으로 복사 완료를 기다림"""
            log("폴더 복사 완료 확인 중...")
            
            max_wait_time = 30  # 최대 30초 대기
            wait_time = 0
            
            while wait_time < max_wait_time:
                if os.path.exists(dest_path):
                    # image 폴더와 CSV 파일이 모두 존재하는지 확인
                    image_folder = os.path.join(dest_path, "image")
                    # unsorted_ 접두사 제거 후 CSV 파일명 생성
                    folder_name = os.path.basename(dest_path)
                    if folder_name.startswith("unsorted_"):
                        folder_name = folder_name[9:]  # "unsorted_" 제거
                    csv_file = os.path.join(dest_path, f"{folder_name}.csv")
                    
                    if os.path.exists(image_folder) and os.path.exists(csv_file):
                        log("폴더 복사 완료 확인됨!")
                        return True
                    else:
                        log(f"파일 확인 중... ({wait_time}s)")
                else:
                    log(f"폴더 확인 중... ({wait_time}s)")
                
                await asyncio.sleep(1)  # 비동기 대기
                wait_time += 1
            
            log("오류: 폴더 복사 완료를 확인할 수 없습니다.")
            return False
        
        async def run_image_sorting():
            """비동기적으로 이미지 분류 실행"""
            log("이미지 분류 시작...")
            try:
                # image_sorting을 비동기로 실행 (log 함수 전달)
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, image_sorting, dest_path, dest_path, log)
                log("정렬 완료!")
            except Exception as e:
                log(f"정렬 중 오류 발생: {str(e)}")
        
        async def main():
            """메인 비동기 함수"""
            if await wait_for_copy_completion():
                await run_image_sorting()
        
        # 비동기 함수 실행
        asyncio.run(main())

    threading.Thread(target=run_sort, daemon=True).start()

    return frame