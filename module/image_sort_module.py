import os
import torch
import clip
from PIL import Image
from tqdm import tqdm
import pandas as pd
from util.path_utils import get_data_root, folder_to_csv_name


"""텍스트 쿼리 => 카테고리 변환 매핑"""
query_to_category = {
    "parking_lot": "야외주차장",
    "street": "재분류",
    "wall": "재분류",
    "many_signboard": "상가",
    "few_signboard": "주택가"
}

category_rayer = [
    ["NaN", "parking_lot", "street", "wall"],
    ["street", "many_signboard", "few_signboard"],
]

"""누락된 이미지 등 수색"""

def validate_and_update_image_categories(csv_path, input_folder):

    df = pd.read_csv(csv_path)
    df["category"] = df["category"].astype(str)

    for idx, row in df.iterrows():
        filename = row["Image"]

        if pd.isna(filename) or not isinstance(filename, str) or filename.strip() == "":
            print(f"이미지 없음: {filename}, 인덱스: {idx}")
            df.at[idx, "category"] = "missing_image"
            continue

        img_path = os.path.join(input_folder, filename)
        if not os.path.isfile(img_path):
            print(f"{img_path} 파일이 존재하지 않습니다.")
            df.at[idx, "category"] = "file_not_found"
            continue

    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print("이미지 누락 전처리 완료")

"""텍스트 쿼리 > 카테고리 변환 함수"""

def map_query_to_category(query, mapping_dict):
    if query in mapping_dict:
        return mapping_dict[query]
    else:
        return "none"

"""클립을 사용한 이미지 카테고리 변환 함수."""

import unicodedata

def extract_numbers_from_filenames(csv_path, input_folder, categories):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-L/14", device=device)
    print("분류 모델 로드 및 시작")

    categories_item = categories[1:]
    print(categories_item)

    text_tokens = clip.tokenize(categories_item).to(device)
    with torch.no_grad():
        text_features = model.encode_text(text_tokens)
        text_features /= text_features.norm(dim=-1, keepdim=True)

    CONFIDENCE_THRESHOLD = 0.25

    # 기존 CSV 불러오기
    df = pd.read_csv(csv_path, na_values=["Nan", "nan", "NaN"])
    print("기존 CSV 불러오기")
    # print(df.columns)

    target_filenames = set(
      unicodedata.normalize('NFC', str(name))
      for name in df[
          (df['category'] == categories[0]) | (df['category'].isna())]["Image"]
    )
    print(f"대상 이미지 수: {len(target_filenames)}")
    # print(target_filenames)

    results = []

    # print(repr(target_filenames))

    print("모델 분류 시작")
    for filename in tqdm(os.listdir(input_folder)):
        # print(repr(filename))
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
                    print("확인")
                    results.append({'Image': filename, 'category': 'none'})
                else:
                    category = categories[top_index.item()]
                    results.append({'Image': filename, 'category': category})
        except Exception as e:
            print(f"Skipping file: {filename} due to error: {e}")
            results.append({'Image': filename, 'category': 'none'})

    print("모델 분류 완료, 결과 저장 중")
    results_df = pd.DataFrame(results)
    print("========================================")
    category = 'category'
    for col in results_df[category]:
        print(col)

    print(df.columns)
    print("========================================")
    print(results_df.columns)
    try:
        df = df.merge(results_df, on='Image', how='left', suffixes=('', '_new'))
        df['category'] = df['category_new'].combine_first(df['category'])
        df = df.drop(columns=['category_new'])
    except Exception as e:
        print(f"Error merging DataFrames: {e}")

    # 변경된 데이터프레임 저장
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print("결과 CSV 저장 완료")

"""카테고리 변환"""

import pandas as pd
def category_to_csv_category(csv_path):

  results = []
  df = pd.read_csv(csv_path)

  for row in df.itertuples(index=False):
      results.append({
          'Address': row.Address,  # set 제거
          'category': map_query_to_category(row.category, query_to_category)
      })

  results_df = pd.DataFrame(results)

  print(results_df)
  output_csv_path = "results.csv"
  results_df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
  print(f"결과 CSV 저장 완료: {output_csv_path}")

"""메인 셀. 추가할 내용은 상단에 함수형으로 셀 추가, 메인 셀에서 실행."""
def image_sorting(folder_path):
    base_dir = folder_path
    input_folder = os.path.join(base_dir, 'image')
    csv_path = os.path.join(base_dir, folder_to_csv_name(base_dir))

    validate_and_update_image_categories(csv_path, input_folder)

    print(category_rayer)

    for categories in category_rayer:
        print(categories[0] + " start")
        extract_numbers_from_filenames(csv_path, input_folder, categories)

    category_to_csv_category(csv_path)

    print("모델 분류 완료")