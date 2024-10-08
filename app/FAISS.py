import faiss
import numpy as np
import os

# FAISS 인덱스를 불러오는 함수
def load_faiss_index(index_filename="app/data/faiss_indices/faiss_index.bin"):
    index_filename = os.path.join(os.path.dirname(__file__), 'data/faiss_indices/faiss_index.bin')
    index = faiss.read_index(index_filename)
    return index

# 데이터베이스에서 이미지 URL을 가져오는 함수
def get_image_urls_from_db(image_ids, db_connection, cursor):
    # Convert numpy.int64 to int and format IDs with 'PF'
    formatted_image_ids = ['PF' + str(int(image_id)) for image_id in image_ids]
    format_strings = ','.join(['%s'] * len(formatted_image_ids))
    
    cursor.execute(f"SELECT ID, image_url FROM images_main WHERE ID IN ({format_strings})", tuple(formatted_image_ids))

    image_urls = {}
    for row in cursor.fetchall():
        image_id, image_url = row
        image_urls[image_id] = image_url

    return image_urls

# 가장 유사한 이미지 찾기
def find_similar_images(query_vector, index, top_n=5):
    try:
        query_vector = query_vector.numpy()
        
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)
        elif query_vector.ndim > 2:
            raise ValueError(f"Expected 1D or 2D array, got {query_vector.ndim}D array")
        
        if query_vector.dtype != np.float32:
            query_vector = query_vector.astype(np.float32)

        # 인덱스 차원과 쿼리 벡터의 차원 확인
        index_dimension = index.d
        if query_vector.shape[1] != index_dimension:
            raise ValueError(f"query_vector 차원 ({query_vector.shape[1]})이 FAISS 인덱스 차원 ({index_dimension})과 일치하지 않습니다.")
        
        # 쿼리 벡터를 정규화
        faiss.normalize_L2(query_vector)
        
        k = top_n  # 상위 n개의 유사한 벡터를 찾기
        
        # 상위 N개의 벡터를 찾기
        distances, indices = index.search(query_vector, k)
        
        # 인덱스에서 유사한 이미지 ID 추출
        similar_image_ids = indices[0]
    except Exception as e:
        print(e)
    
    return similar_image_ids, distances[0]

# 이미지 URL 출력
def print_image_urls(similar_image_ids, image_urls):
    for image_id in similar_image_ids:
        # FAISS 인덱스에서 얻은 ID에 'PF' 접두사 추가
        if image_id in image_urls:
            print(f"Image ID: {image_id}, URL: {image_urls[image_id]}")
        else:
            print(f"Image ID: {image_id}의 URL을 찾을 수 없습니다.")