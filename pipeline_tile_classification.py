import os
import sys
from PIL import Image
from classify.recognizer import load_all_embeddings_from_folders, classify_by_knn

# Adiciona 'src' ao path para importar o módulo 'levels'
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
src_path = os.path.join(repo_root, "src")
sys.path.append(src_path)
from mapping import get_level_file_name
from levels import encode_txt_to_levels, encode_levels_to_txt

# === Constantes ===
cols, rows = 19, 15
tile_size = 20
resized_size = (cols * tile_size, rows * tile_size)

input_dir = os.path.join(repo_root, "data", "pictures", "screenshots")
ref_dir = os.path.join(repo_root, "data", "pictures", "tiles", "labels")
output_txt_dir = os.path.join(repo_root, "data", "predict", "predict_txt")
rebuild_dir = os.path.join(repo_root, "data", "predict", "predict_jpg")

os.makedirs(output_txt_dir, exist_ok=True)
os.makedirs(rebuild_dir, exist_ok=True)

image_files = [
    "img_01a.png", "img_01b.png", "img_02a.png", "img_03a.png", "img_03b.png",
    "img_04a.png", "img_04b.png", "img_05a.png", "img_05b.png",
    "img_06a.png", "img_06b.png", "img_07a.png", "img_07b.png",
    "img_08a.png", "img_08b.png", "img_09a.png", "img_09b.png",
    "img_10a.png", "img_10b.png", "img_11a.png", "img_11b.png",
    "img_12a.png", "img_12b.png", "img_13a.png", "img_13b.png",
    "img_14a.png", "img_14b.png", "img_15a.png", "img_15b.png",
    "img_16a.png", "img_16b.png", "img_17a.png", "img_17b.png",
    "img_18a.png", "img_18b.png", "img_19a.png"
]

mapping_name_txt = {
    name: f"level_{i:03d}.txt"
    for i, name in enumerate(image_files)
}

mapping_name_jpg = {
    name: f"level_{i:03d}.jpg"
    for i, name in enumerate(image_files)
}

def carregar_tiles_de_referencia(ref_dir):
    tile_examples = {}
    for label in os.listdir(ref_dir):
        label_dir = os.path.join(ref_dir, label)
        if os.path.isdir(label_dir):
            imgs = [f for f in os.listdir(label_dir) if f.endswith(".png")]
            if imgs:
                tile_path = os.path.join(label_dir, imgs[0])
                tile_img = Image.open(tile_path).resize((tile_size, tile_size), Image.NEAREST)
                tile_examples[label] = tile_img
    return tile_examples

def classificar_tiles(image, embeddings):
    image = image.resize(resized_size, Image.NEAREST)
    label_matrix = []
    for i in range(rows):
        row_labels = []
        for j in range(cols):
            left = j * tile_size
            top = i * tile_size
            right = left + tile_size
            bottom = top + tile_size
            tile = image.crop((left, top, right, bottom))
            label_char = classify_by_knn(tile, embeddings)
            row_labels.append(label_char)
        label_matrix.append(row_labels)
    return label_matrix

def salvar_txt(label_matrix, output_txt_path):
    with open(output_txt_path, "w") as f:
        for row in label_matrix:
            f.write("".join(row) + "\n")

def reconstruir_imagem(label_matrix, tile_examples, output_path):
    reconstructed = Image.new("RGB", (cols * tile_size, rows * tile_size))
    for i, row in enumerate(label_matrix):
        for j, label in enumerate(row):
            tile = tile_examples.get(label)
            if tile:
                reconstructed.paste(tile, (j * tile_size, i * tile_size))
    reconstructed.save(output_path)

def processar_imagem(image_file, idx, embeddings, tile_examples):
    input_path = os.path.join(input_dir, image_file)
    output_txt_path = os.path.join(output_txt_dir, mapping_name_txt[image_file])
    output_jpg_path = os.path.join(rebuild_dir, mapping_name_jpg[image_file])

    image = Image.open(input_path).convert("RGB")
    label_matrix = classificar_tiles(image, embeddings)
    
    salvar_txt(label_matrix, output_txt_path)
    print(f"[✓] {image_file} → {output_txt_path}")
    
    reconstruir_imagem(label_matrix, tile_examples, output_jpg_path)
    print(f"[🖼️] Imagem reconstruída salva em: {output_jpg_path}")
    
    level = encode_txt_to_levels(output_txt_path, idx)
    encode_levels_to_txt(level, idx)

def main():
    print("[INFO] Carregando embeddings de referência...")
    embeddings = load_all_embeddings_from_folders(ref_dir)
    tile_examples = carregar_tiles_de_referencia(ref_dir)

    for idx, image_file in enumerate(image_files):
        processar_imagem(image_file, idx, embeddings, tile_examples)

if __name__ == "__main__":
    main()
