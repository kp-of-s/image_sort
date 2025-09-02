import pandas as pd
import re

# 기본 패턴 정의 (필요 시 수정 가능)
patterns = {
    r"패턴1": "분류1",
    r"패턴2": "분류2",
    r"패턴3": "분류3",
    # 필요하면 추가
}

def classify_name(name: str) -> str:
    """단일 문자열을 패턴에 맞춰 분류"""
    for pattern, label in patterns.items():
        if re.search(pattern, str(name)):
            return label
    return "기타"

def classify_csv(file_path: str, column_name: str, target_column: str = "분류") -> None:
    """
    CSV 파일의 특정 컬럼을 기반으로 분류를 수행하고,
    결과를 target_column에 기록 후 CSV를 저장
    """
    df = pd.read_csv(file_path, encoding="utf-8-sig")
    df[target_column] = df[column_name].apply(classify_name)
    df.to_csv(file_path, index=False, encoding="utf-8-sig")
