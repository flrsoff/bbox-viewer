from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import base64
from parser_yaml import parse_yaml_to_pairs
import cv2

base_abs_path = None
images_path, labels_path = None, None
images_info = None
img_idx = -1
is_upload = False
num_img = 0

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

def load_image(img_name):
    img_path, lbl_path = get_paths(
        base_abs_path,
        images_path, labels_path,
        img_name, 
        images_info[img_name][0], images_info[img_name][1]
    )
    return load_annotated_image(img_path, lbl_path)

def load_data_file(path):
    global base_abs_path, images_path, labels_path, images_info, img_names, img_idx, is_upload, num_img
    base_abs_path, (images_path, labels_path), images_info = parse_yaml_to_pairs(path, True) 
    img_names = sorted(images_info.keys())
    num_img = len(img_names)
    if num_img: img_idx = 0; is_upload = True
    else: is_upload = False

app = Flask(__name__)
app.config['cache-paths'] = {
    'data-file': 'cache/data.yaml'
}
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data', methods=['GET'])
def api_data():
    sample_data = {"name": "Flask", "version": "1.0"}
    return jsonify(sample_data)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        file.save(app.config['cache-paths']['data-file'])
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/image/<navigation>', methods=['GET'])
def get_image(navigation):
    global img_idx, num_img, is_upload
    try:
        if navigation == 'first':     
            load_data_file(app.config['cache-paths']['data-file'])
            if is_upload: return jsonify({'file_name': f'{img_names[img_idx]}', "data": load_image(img_names[img_idx])})
            else        : return jsonify({"error"    : 'no files'})
        elif num_img:
            if    navigation == 'next': img_idx = (img_idx + 1) % num_img
            elif  navigation == 'prev': img_idx = (img_idx - 1) % num_img
            else: return jsonify({'error': f'undefined request: {navigation}'})
            return       jsonify({'file_name': f'{img_names[img_idx]}', "data": load_image(img_names[img_idx])})
        else: return     jsonify({"error": 'no files'})
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
