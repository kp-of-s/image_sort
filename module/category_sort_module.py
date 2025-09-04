import os
import pandas as pd
import json
from util.path_utils import get_config_path, folder_to_csv_name

# 1. CSV에서 category 컬럼 존재 로우 필터링
def filter_categories_and_non_type(csv_path, category_csv_path, log_func=print):
    try:
        df_main = pd.read_csv(csv_path, encoding="utf-8-sig", na_values=["Nan", "nan", "NaN", "미분류"])
        df_category = pd.read_csv(category_csv_path, encoding="utf-8-sig")
    except FileNotFoundError as e:
        log_func(f"오류: 파일을 찾을 수 없습니다. ({e})")
        return None
    
    # 1. df_main 필터링: 'type2' 컬럼에 값이 있는 행 제외
    filtered_main = df_main[df_main['type2'].isna()]
    
    # 2. df_category 필터링: 3개의 'category' 컬럼이 모두 비어있는 행 제외
    category_cols = ['category1', 'category2', 'category3']
    filtered_category = df_category[df_category[category_cols].notna().any(axis=1)]
    
    # 3. 두 필터링된 DataFrame 병합
    #    name 컬럼을 기준으로 병합하고, 두 조건을 모두 만족하는 행만 남깁니다.
    final_df = pd.merge(filtered_main, filtered_category, on='name', how='inner')
    
    log_func(f"{len(final_df)}개의 행에 대해 카테고리 분류합니다.")

    return final_df

# 2. JSON 설정 파일 읽어 category 매핑 후 새로운 DataFrame 생성
def apply_category_mapping(df, log_func=print):
    json_path = os.path.join(get_config_path(), "category_keyword.json")
    with open(json_path, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
    
    new_df = pd.DataFrame(columns=['name', 'type1', 'type2'])

    for index, row in df.iterrows():
        combined_text = ' '.join(
            str(row[col]) for col in ['ca1', 'ca2', 'ca3'] if pd.notna(row[col])
        )
        
        found_category = None
        # 설정값(mapping)을 순회하며 키워드 매칭
        for category_name, keywords in mapping.items():
            for keyword in keywords:
                if keyword in combined_text:
                    found_category = category_name
                    break
            if found_category:
                break
        
        # 매칭되는 키워드가 있으면 새로운 DataFrame에 추가
        if found_category:
            new_row = pd.DataFrame(
                [{'name': row['name'], 'type2': found_category}]
            )
            new_df = pd.concat([new_df, new_row], ignore_index=True)

    return new_df

# type2 기반 type1 매핑
def type2_to_type1_mapping(new_df, log_func=print):
    json_path = os.path.join(get_config_path(), "typetwo_to_typeone.json")
    with open(json_path, 'r', encoding='utf-8') as f:
        mapping = json.load(f)

    new_df['type2'] = new_df['type1'].apply(lambda x: mapping.get(x))

    return new_df

# 4. 기존 CSV에 type 업데이트 후 저장
def update_and_save(original_csv_path, df_new, log_func=print):
    try:
        df_orig = pd.read_csv(original_csv_path, encoding="utf-8-sig")
    except FileNotFoundError:
        log_func(f"오류: '{original_csv_path}' 파일을 찾을 수 없습니다.")
        return None

    # 'name'을 인덱스로 설정
    df_orig.set_index('name', inplace=True)
    df_new.set_index('name', inplace=True)

    # df_new의 'type' 값으로 df_orig의 'type' 값을 갱신
    df_orig.update(df_new['type1'])
    df_orig.update(df_new['type2'])

    # 인덱스 초기화
    df_orig.reset_index(inplace=True)

    # 최종 결과 저장
    df_orig.to_csv(original_csv_path, index=False, encoding="utf-8-sig")

# 예시 사용
def category_sorting(folder_path, log_func=print):
    log_func("카테고리 분류 시작...")

    base_dir = folder_path
    origin_file_name = folder_to_csv_name(base_dir)
    name, ext = os.path.splitext(origin_file_name)
    category_file_name = f"{name}_category{ext}"
    category_csv_path = os.path.join(base_dir, category_file_name)
    csv_path = os.path.join(base_dir, origin_file_name)

    filtered_df = filter_categories_and_non_type(csv_path, category_csv_path, log_func)
    name_df = apply_category_mapping(filtered_df, log_func)
    name_df = type2_to_type1_mapping(name_df, log_func)
    update_and_save(csv_path, name_df, log_func)