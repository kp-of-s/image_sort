import os
import torch
import clip
from PIL import Image
from tqdm import tqdm
import sys
import pandas as pd
from util.path_utils import folder_to_csv_name, get_config_path
import json


"""텍스트 쿼리 => 타입 변환 매핑"""
with open(os.path.join(get_config_path(), "query_to_category.json"), 'r', encoding='utf-8') as f:
    query_to_category = json.load(f)

"""타입2기반 타입1 입력"""
with open(os.path.join(get_config_path(), "typetwo_to_typeone.json"), 'r', encoding='utf-8') as f:
    typetwo_to_typeone = json.load(f)

"""clip이 분류할 내용"""
with open(os.path.join(get_config_path(), "category_rayer.json"), 'r', encoding='utf-8') as f:
    category_rayer = json.load(f)

"""누락된 이미지 등 수색"""

def validate_and_update_image_categories(csv_path, input_folder):
    df = pd.read_csv(csv_path)
    # type2 컬럼을 문자열로 변환하되, NaN은 그대로 유지
    df["type2"] = df["type2"].astype('string')

    for idx, row in df.iterrows():
        filename = row["image"]

        if pd.isna(filename) or not isinstance(filename, str) or filename.strip() == "":
            df.at[idx, "type2"] = "missing_image"
            continue

        img_path = os.path.join(input_folder, filename)
        if not os.path.isfile(img_path):
            df.at[idx, "type2"] = "file_not_found"
            continue

    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    # 이미지 누락 전처리 완료


"""텍스트 쿼리 > 카테고리 변환 함수"""
def map_query_to_category(query, mapping_dict):
    if query in mapping_dict:
        return mapping_dict[query]
    else:
        return query

"""클립을 사용한 이미지 카테고리 변환 함수."""

import unicodedata

def extract_numbers_from_filenames(csv_path, input_folder, categories, log_func=print):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-L/14", device=device)
    # model, preprocess = clip.load("ViT-B/32", device=device)

    classific_column, categories_item = categories[0], categories[1:]

    text_tokens = clip.tokenize(categories_item).to(device)
    with torch.no_grad():
        text_features = model.encode_text(text_tokens)
        text_features /= text_features.norm(dim=-1, keepdim=True)

    CONFIDENCE_THRESHOLD = 0.25

    df = pd.read_csv(csv_path, na_values=["Nan", "nan", "NaN", "미분류"])

    # 첫 번째 분류에서는 모든 NaN 값들을 대상으로 함
    if classific_column == "NaN":
        target_condition = df['type2'].isna()
    else:
        target_condition = (df['type2'] == classific_column) | (df['type2'].isna())
    
    target_filenames = set(
      unicodedata.normalize('NFC', str(name))
      for name in df[target_condition]["image"]
    )
    log_func(f"대상 이미지 수: {len(target_filenames)}")
    log_func(f"분류 조건: {classific_column}인 경우")

    results = []

    log_func("모델 분류 시작")

    if sys.stdout is None:
        sys.stdout = open(os.devnull, 'w')
    if sys.stderr is None:
        sys.stderr = open(os.devnull, 'w')

    for filename in tqdm(os.listdir(input_folder), file=sys.stdout):
        filename = unicodedata.normalize('NFC', filename.strip())
        if filename not in target_filenames:
            continue
        img_path = os.path.join(input_folder, filename)
        try:
            image = preprocess(Image.open(img_path).convert("RGB")).unsqueeze(0).to(device)
            with torch.no_grad():
                image_features = model.encode_image(image)
                image_features /= image_features.norm(dim=-1, keepdim=True)

                similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
                top_score, top_index = similarity[0].max(0)
                top_score = top_score.item()

                if top_score < CONFIDENCE_THRESHOLD:
                    # 확인
                    results.append({'image': filename, 'type2': '미분류'})
                else:
                    category = categories_item[top_index.item()]
                    results.append({'image': filename, 'type2': category, 'autoSortRow': 'true'})
        except Exception as e:
            results.append({'image': filename, 'type2': '미분류'})

    log_func("모델 분류 완료, 결과 저장 중")
    results_df = pd.DataFrame(results)
    
    # 분류 결과 통계 출력
    log_func("=" * 50)
    log_func("분류 결과 통계:")
    category_counts = results_df['type2'].value_counts()
    for category, count in category_counts.items():
        log_func(f"  {category}: {count}개")
    log_func("=" * 50)
    try:
        df = df.merge(results_df, on='image', how='left', suffixes=('', '_new'))
        df['type2'] = df['type2_new'].combine_first(df['type2'])
        df = df.drop(columns=['type2_new'])
    except Exception as e:
        # Error merging DataFrames: {e}
        pass

    # 변경된 데이터프레임 저장
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    log_func("결과 CSV 저장 완료")

"""카테고리 변환"""

import pandas as pd
def category_to_csv_category(csv_path):
    """
    분류된 카테고리를 최종 카테고리로 변환하여 원본 CSV에 저장
    """
    df = pd.read_csv(csv_path)
    
    # type2 컬럼을 최종 카테고리로 변환
    df['type2'] = df['type2'].apply(
        lambda x: map_query_to_category(x, query_to_category)
    )
    df['type1'] = df['type2'].apply(
        lambda x: map_query_to_category(x, typetwo_to_typeone)
    )
    # 원본 CSV 파일에 저장 (덮어쓰기)
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    # 결과 CSV 저장 완료: {csv_path}

"""메인 셀. 추가할 내용은 상단에 함수형으로 셀 추가, 메인 셀에서 실행."""
def image_sorting(folder_path, log_func=print):
    base_dir = folder_path
    images_folder = os.path.join(base_dir, 'images')
    csv_path = os.path.join(base_dir, folder_to_csv_name(base_dir))

    log_func("이미지 분류 시작...")
    validate_and_update_image_categories(csv_path, images_folder)

    log_func(f"분류 단계: {len(category_rayer)}개")
    for i, categories in enumerate(category_rayer, 1):
        log_func(f"분류 단계 {i}/{len(category_rayer)}: {categories[0]} 시작")
        extract_numbers_from_filenames(csv_path, images_folder, categories, log_func)

    log_func("최종 카테고리 변환 중...")
    category_to_csv_category(csv_path)

    log_func("모델 분류 완료")