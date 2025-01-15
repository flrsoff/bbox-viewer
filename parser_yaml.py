import yaml
import os

VALID_IMAGES_FORMATS = (
    '.bmp' , # Microsoft BMP File Format
    '.dng' , # Adobe DNG
    '.jpeg', # JPEG
    '.jpg' , # JPEG
    '.mpo' , # Multi Picture Object
    '.png' , # Portable Network Graphics
    '.tif' , # Tag Image File Format
    '.tiff', # Tag Image File Format
    '.webp', # WebP
    '.pfm' , # Portable FloatMap
    '.HEIC', # High Efficiency Image Format
)

def parse_yaml_to_pairs(yaml_file):
    if not os.path.isfile(yaml_file): return
    
    with open(yaml_file, "r") as file:
        config = yaml.safe_load(file)

    base_rel_path = config['path']  # Базовый путь
    images_path = config['images']  # Папки с изображениями
    labels_path = config['labels']  # Папки с метками

    base_abs_path = os.path.join(os.path.dirname(yaml_file), base_rel_path)
    
    images_abs_path = os.path.join(base_abs_path, images_path)
    labels_abs_path = os.path.join(base_abs_path, labels_path)
    
    if not os.path.exists(images_abs_path): return

    images: dict[str, tuple[str, bool]] = dict()
    for img_file in os.listdir(images_abs_path):
        img_path = os.path.join(images_abs_path, img_file)
        dot_index = img_file.rfind('.')
        if dot_index != -1 and os.path.isfile(img_path):
            name, extension = img_file[:dot_index], img_file[dot_index:]
            if extension in VALID_IMAGES_FORMATS:
                label_path = os.path.join(labels_abs_path, f'{name}.txt')
                images[name] = (extension, os.path.isfile(label_path))
                
    return base_abs_path, (images_path, labels_path), images        

