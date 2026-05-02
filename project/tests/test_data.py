from src.data.loader import EmotionImageDataset
from PIL import Image
import torch

def test_dataset_length():
    ds = EmotionImageDataset("data", split="train")
    assert len(ds) > 0, "Train dataset is empty"

def test_item_shape_and_dtype():
    ds = EmotionImageDataset("data", split="train")
    img, label = ds[0]
    assert img.dtype == torch.float32
    assert img.shape == (1, 48, 48), f"Expected (1,48,48), got {img.shape}"
    assert 0 <= label <= 6

def test_label_consistency():
    ds = EmotionImageDataset("data", split="train")
    unique_labels = set(ds.samples[i][1] for i in range(len(ds)))
    assert unique_labels == set(range(7)), "Missing emotion classes in train set"