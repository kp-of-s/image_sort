import os
import sys

def get_project_root():
    """프로젝트 루트 경로 반환 (exe + 소스 환경 지원)"""
    if getattr(sys, 'frozen', False):
        # exe 환경: 실행 파일 위치 기준
        return os.path.dirname(sys.executable)
    # 소스 실행 환경: util 폴더 기준 한 단계 위
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def get_base_path():
    """PyInstaller 실행 시와 개발 환경에서 동일하게 경로 반환"""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS  # exe로 빌드된 경우 임시 경로
    return os.path.dirname(os.path.abspath(__file__))

def get_project_path():
    """현재 실행 프로젝트 경로"""
    return os.path.dirname(get_base_path())

def get_config_path():
    """config 폴더 경로"""
    return os.path.join(get_project_root(), 'config')

def get_data_root():
    """data 폴더 경로"""
    return os.path.join(get_project_root(), 'data')

def get_data_subpath(subfolder=""):
    """data 하위 특정 폴더 경로"""
    return os.path.join(get_data_root(), subfolder)

def folder_to_csv_name(folder_path):
    """
    폴더 경로에서 마지막 폴더명 + '.csv' 반환
    unsorted_ 접두사가 있으면 제거
    예: 'data/unsorted_선택한폴더명' → '선택한폴더명.csv'
    """
    folder_name_with_prefix = os.path.basename(folder_path.rstrip("/\\"))
    # unsorted_ 접두사 제거
    # 언더바('_') 뒤의 문자열만 추출
    if "_" in folder_name_with_prefix:
        folder_name = folder_name_with_prefix.split("_", 1)[1]
    else:
        folder_name = folder_name_with_prefix
    return f"{folder_name}.csv"