import re, os
import pandas as pd
from typing import List, Dict, Tuple
from util.path_utils import get_config_path, folder_to_csv_name


def _compile_keyword(kw: str):
    kw = kw.strip()
    if not kw:
        return None
    if kw.lower().startswith("re:"):  
        return re.compile(kw[3:].strip(), flags=re.IGNORECASE)
  
    if re.search(r'[.^$*+?{}\[\]\\|()]', kw):
        return re.compile(kw, flags=re.IGNORECASE)
    return re.compile(re.escape(kw), flags=re.IGNORECASE)

def load_rules_from_txt(config_file: str) -> List[Dict]:
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"키워드 설정 파일이 없습니다: {config_file}")

    rules: List[Dict] = []
    with open(config_file, "r", encoding="utf-8") as f:
        for lineno, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue

            label, values_str = line.split(":", 1)
            label = label.strip()
            tokens = [v.strip() for v in values_str.split(",") if v.strip()]

            if len(tokens) >= 3:   
                cat1, cat2 = tokens[0], tokens[1]
                kws = tokens[2:]
            else:                  
                cat1 = cat2 = label
                kws = tokens

            pats = [_compile_keyword(k) for k in kws]
            pats = [p for p in pats if p is not None]
            if not pats:
                print(f"[경고] {config_file}:{lineno} 키워드 없음. 건너뜀 -> {line}")
                continue

            rules.append({"label": label, "type1": cat1,
                          "type2": cat2, "patterns": pats})

    if not rules:
        raise ValueError("유효한 규칙이 없습니다.")
    # print(f"[INFO] 규칙 {len(rules)}개 로드 완료")
    return rules


def classify_row(row: pd.Series, rules: List[Dict],
                 search_cols: Tuple[str, str] = ("name", "address")) -> Tuple[str, str, str]:
    name = str(row.get(search_cols[0], "")).strip()
    addr = str(row.get(search_cols[1], "")).strip()
    haystack = f"{name} {addr}"

    for rule in rules:   # TXT 순서 = 우선순위
        for pat in rule["patterns"]:
            if pat.search(haystack):
                return rule["type1"], rule["type2"], rule["label"]
    return "미분류", "미분류", ""

def save_classification(csv_in: str, config_file: str, log_func=print) -> pd.DataFrame:
    rules = load_rules_from_txt(config_file)
    try:
        df = pd.read_csv(csv_in, encoding="utf-8-sig", na_values=["Nan", "nan", "NaN", "미분류"])
    except UnicodeDecodeError:
        df = pd.read_csv(csv_in, encoding="cp949")

    df_nan = df[df['type2'].isna()]


    # 분류 결과를 기존 csv_in 파일에 덮어쓰기
    cat1_list, cat2_list, matched = [], [], []

    for _, row in df_nan.iterrows():
        c1, c2, lb = classify_row(row, rules)
        cat1_list.append(c1)
        cat2_list.append(c2)
        matched.append(lb)

    df['type1'] = df['type1'].astype(str)
    df['type2'] = df['type2'].astype(str)
    
    # 기존 데이터프레임에 분류된 값 추가
    df.loc[df['type2'].isna(), "type1"] = cat1_list
    df.loc[df['type2'].isna(), "type2"] = cat2_list

    # csv_in 파일에 덮어쓰기 (기존 파일을 수정)
    df.to_csv(csv_in, index=False, encoding="utf-8-sig")

    # 분류 통계 출력
    stats = df.groupby(["type1", "type2"]).size().reset_index(name="Count")
    # print("=== 분류 통계 ===")
    # print(stats.to_string(index=False))
    # print(f"\n결과 저장: {csv_in}")

    return df

# if __name__ == "__main__":
#     CSV_IN = "수원시 권선구_parking_area.csv"
#     TXT    = "keywords_config.txt"

#     preview(CSV_IN, TXT, n=5)
#     save_classification(CSV_IN, TXT)

def text_sorting(CSV_IN, log_func=print):
    TXT = os.path.join(get_config_path(), "text_keywords.txt")
    csv_path = os.path.join(CSV_IN, folder_to_csv_name(CSV_IN))
    log_func(f"\"{csv_path}\"에 텍스트 분류 저장합니다.")
    save_classification(csv_path, TXT, log_func)
    # print(f"텍스트 분류 완료: {CSV_IN}")
