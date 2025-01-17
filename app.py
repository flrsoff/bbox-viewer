from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import base64
from parser_yaml import parse_yaml_to_pairs
import cv2

def get_paths(base_path, images_rel_path, labels_rel_path, name, extension, has_label):
    return (os.path.join(base_path, images_rel_path, f'{name}{extension}'), 
            os.path.join(base_path, labels_rel_path, f'{name}.txt'       ) if has_label else None)

def load_annotated_image(image_path, label_path,  shape = (640, 480)): 

    image = cv2.imread(image_path)
    height, width, _ = image.shape
    labels: dict[str, list[tuple[int, int, int, int]]] = dict()
    
    if label_path: 
        with open(label_path) as file:
            for line in file:
                id, tx, ty, tw, th = line.strip().split()
                tx = float(tx) * width; ty = float(ty) * height
                tw = float(tw) * width; th = float(th) * height

                left   = int(tx - tw / 2)
                right  = int(tx + tw / 2)
                top    = int(ty - th / 2)
                bottom = int(ty + th / 2)

                if id in labels: labels[id].append((left, right, top, bottom))
                else           : labels[id]     = [(left, right, top, bottom)]
            
    for id in labels:
        for left, right, top, bottom in labels[id]:
            cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)
                
    scale = min(shape[0] / width, shape[1] / height)
    image = cv2.resize(image, (int(scale * width), int(scale * height)))
    
    _, buffer = cv2.imencode(image_path[image_path.rfind('.'):], image)
    return base64.b64encode(buffer.tobytes()).decode('utf-8')

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.form.get('data')
    if data:
        return jsonify({"message": "Данные получены", "data": data})
    else:
        return jsonify({"error": "Нет данных"}), 400

@app.route('/api/data', methods=['GET'])
def api_data():
    sample_data = {"name": "Flask", "version": "1.0"}
    return jsonify(sample_data)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Файл не найден"}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "Файл не выбран"}), 400
    
    if not file.filename.endswith('.yaml'):
        return jsonify({"error": "Файл должен быть в формате .yaml"}), 400

    content = file.read().decode('utf-8') 
    return jsonify({"message": "Файл успешно загружен", "content": content})

base_abs_path, (images_path, labels_path), images_info = parse_yaml_to_pairs('config.yaml') 

img_names = sorted(images_info.keys())
img_idx = 0

def load_image(img_name):
    img_path, lbl_path = get_paths(
        base_abs_path,
        images_path, labels_path,
        img_name, 
        images_info[img_name][0], images_info[img_name][1]
    )
    return load_annotated_image(img_path, lbl_path)



@app.route('/image/<navigation>', methods=['GET'])
def get_image(navigation):
    
    global img_idx
    try:
        if   navigation == 'first' and len(img_names): img_idx = 0
        elif navigation == 'next'                    : img_idx = (img_idx + 1) % len(img_names)
        elif navigation == 'prev'                    : img_idx = (img_idx - 1) % len(img_names)
        else                                  : raise "error"
        return jsonify({'file_name': f'{img_names[img_idx]}', "data": load_image(img_names[img_idx])})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
