import pandas as pd

# 카테고리 csv 기반 보정
def apply_category_corrections(df: pd.DataFrame, category_csv: str,
                               csv_out: str = "수원시_영통구.csv") -> pd.DataFrame:
    category_df = pd.read_csv(category_csv, encoding="utf-8")
 
    # 이름 공백 제거
    df["name_clean"] = df["name"].astype(str).str.replace(" ", "").str.strip()
    category_df["name_clean"] = category_df["name"].astype(str).str.replace(" ", "").str.strip()
 
    merged = df.merge(category_df[["name_clean", "category2"]],
                      on="name_clean", how="left")
 
    def fix_type(row):
        c2 = str(row["category2"]).strip()
        if any(x in c2 for x in ["스포츠시설", "종교"]):
            return ("실외", "야외시설")
        elif any(x in c2 for x in ["주거시설", "아케이드"]):
            return ("골목길", "건물주변")
        return (row["type1"], row["type2"])
 
    merged[["type1", "type2"]] = merged.apply(
        lambda r: pd.Series(fix_type(r)), axis=1
    )
 
    # 필요 없는 컬럼 정리
    merged.drop(columns=["name_clean","category2"], inplace=True, errors="ignore")
 
    merged.to_csv(csv_out, index=False, encoding="utf-8-sig")
    print(f"[INFO] category.csv 보정 적용 후 저장 완료 → {csv_out}")
    return merged