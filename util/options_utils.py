import os
from util.path_utils import get_project_root

def get_options_file():
    """
    옵션 파일 전체 경로 반환
    exe 또는 소스 환경 모두 대응
    """
    base = get_project_root()
    return os.path.join(base, "config", "options.txt")

def load_options():
    """
    옵션 파일에서 리스트 불러오기
    """
    options_file = get_options_file()
    if not os.path.exists(options_file):
        print(f"옵션 파일 없음: {options_file}")
        return []

    with open(options_file, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]