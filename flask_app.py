import base64
import io
import cv2
import numpy as np
from flask import Flask, request, jsonify
from PIL import Image
from scipy.spatial.distance import cosine, euclidean, cityblock


app = Flask(__name__)

# Hàm để trích xuất vector từ ảnh sử dụng OpenCV (trích xuất histogram của ảnh)
def extract_vector_from_image(image):
    # Chuyển ảnh PIL thành định dạng OpenCV (numpy array)
    image_cv = np.array(image)
    
    # Chuyển đổi ảnh từ RGB sang Grayscale
    gray_image = cv2.cvtColor(image_cv, cv2.COLOR_RGB2GRAY)
    
    # Tính toán histogram của ảnh (ví dụ trích xuất đặc trưng histogram)
    hist = cv2.calcHist([gray_image], [0], None, [256], [0, 256])
    
    # Chuẩn hóa histogram (vector)
    hist = hist / hist.sum()  # Chuẩn hóa để đảm bảo tổng bằng 1

    # Trả về vector của histogram (đây là một vector mô tả đặc trưng của ảnh)
    return hist.flatten().tolist()  # Chuyển sang list để trả về dưới dạng JSON

@app.route('/extract-vector', methods=['POST'])
def extract_vector():
    try:
        # Nhận ảnh từ body request dưới dạng JSON
        data = request.json
        image_data = data['image']
        
        # Giải mã ảnh từ chuỗi Base64
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))

        # Trích xuất vector từ ảnh
        image_vector = extract_vector_from_image(image)
        
        # Trả về vector dưới dạng chuỗi JSON
        return jsonify({"vector": image_vector})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Hàm tách chuỗi thành vector
def parse_vector(vector_string):
    return np.array(list(map(float, vector_string.split(","))))

# Hàm tính khoảng cách
def calculate_distance(input_vector, target_vector, metric):
    if metric == "cosine":
        return cosine(input_vector, target_vector)
    elif metric == "euclidean":
        return euclidean(input_vector, target_vector)
    elif metric == "manhattan":
        return cityblock(input_vector, target_vector)
    else:
        raise ValueError("Unsupported distance metric")

@app.route("/calculate-similarity", methods=["POST"])
def calculate_similarity():
    try:
        # Lấy dữ liệu từ request
        data = request.get_json()
        input_vector = parse_vector(data["input_vector"])
        vector_list = [parse_vector(vec) for vec in data["vector_list"]]
        metric = data.get("distance_metric", "cosine")  # Mặc định là cosine

        # Tính khoảng cách
        results = []
        for vec in vector_list:
            distance = calculate_distance(input_vector, vec, metric)
            results.append({
                "vector": vec,  # Giữ nguyên vector dưới dạng danh sách số
                "distance": distance
            })

        # Sắp xếp theo độ tương tự giảm dần (tức khoảng cách tăng dần)
        sorted_results = sorted(results, key=lambda x: x["distance"])

        # Chuyển đổi định dạng vector thành chuỗi phân tách bằng dấu chấm phẩy
        formatted_vectors = ";".join(
            ",".join(map(str, result["vector"])) for result in sorted_results
        )

        # Trả về chuỗi trực tiếp
        return formatted_vectors, 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True)
