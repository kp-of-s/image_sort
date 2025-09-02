import os
import json
from util.path_utils import get_project_root

def get_options_file():
    """
    옵션 파일 전체 경로 반환
    exe 또는 소스 환경 모두 대응
    """
    base = get_project_root()
    return os.path.join(base, "config", "options.json")

def load_options():
    """
    옵션 파일에서 리스트 불러오기
    """
    options_file = get_options_file()
    if not os.path.exists(options_file):
        # 옵션 파일 없음: {options_file}
        return []

    with open(os.path.join(options_file), 'r', encoding='utf-8') as f:
        return json.load(f)