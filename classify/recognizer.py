# classify/recognizer.py

import os
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# === Transforms para ResNet ===
preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

# === Modelo ===
resnet = models.resnet18(pretrained=True)
feature_extractor = nn.Sequential(*list(resnet.children())[:-1])
feature_extractor.eval()

def get_embedding(img: Image.Image) -> np.ndarray:
    img_tensor = preprocess(img).unsqueeze(0)
    with torch.no_grad():
        feat = feature_extractor(img_tensor)
    return feat.view(-1).numpy()  # vetor 512D

def load_all_embeddings_from_folders(folder_path: str) -> list:
    """
    Retorna uma lista de (vetor, label) para todas as imagens nas subpastas.
    """
    labeled_embeddings = []
    for label in sorted(os.listdir(folder_path)):
        label_dir = os.path.join(folder_path, label)
        if not os.path.isdir(label_dir):
            continue
        for fname in os.listdir(label_dir):
            if fname.lower().endswith((".png", ".jpg", ".jpeg")):
                img_path = os.path.join(label_dir, fname)
                img = Image.open(img_path).convert("RGB")
                emb = get_embedding(img)
                labeled_embeddings.append((emb, label))
    return labeled_embeddings

def classify_by_knn(tile_img: Image.Image, labeled_embeddings: list) -> str:
    tile_emb = get_embedding(tile_img).reshape(1, -1)
    best_label = None
    best_score = -1
    for ref_emb, ref_label in labeled_embeddings:
        score = cosine_similarity(tile_emb, ref_emb.reshape(1, -1))[0][0]
        if score > best_score:
            best_score = score
            best_label = ref_label
    return best_label
