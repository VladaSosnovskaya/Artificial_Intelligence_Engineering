from pathlib import Path
from typing import Tuple, List
import numpy as np
from PIL import Image
from torch.utils.data import Dataset, DataLoader, Subset
import torch
from torchvision import transforms
from sklearn.model_selection import train_test_split
from src.constants import EMOTION_LABELS, LABEL_TO_IDX

class EmotionImageDataset(Dataset):
    def __init__(self, root_dir, split = "train", image_size = 48, transform = None):
        self.root = Path(root_dir) / split
        self.image_size = image_size
        self.transform = transform
        self.samples: List[Tuple[str, int]] = []

        for emotion in EMOTION_LABELS:
            emotion_path = self.root / emotion
            if not emotion_path.exists():
                print(f"Папка {emotion_path} не найдена")
                continue
            
            for ext in ["*.jpg", "*.jpeg", "*.png"]:
                for img_file in emotion_path.glob(ext):
                    self.samples.append((str(img_file), LABEL_TO_IDX[emotion]))
    
    def __len__(self) -> int:
        return len(self.samples)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        img_path, label = self.samples[idx]
        
        image = Image.open(img_path).convert("L")       
        image = image.resize((self.image_size, self.image_size), Image.Resampling.LANCZOS)
        
        if self.transform:
            image = self.transform(image)
        else:
            image = transforms.ToTensor()(image)
            
        # гарантируем форму (1, H, W)
        if image.dim() == 2:
            image = image.unsqueeze(0)
            
        return image, label


def create_dataloaders(data_dir, image_size = 48, batch_size = 64, random_state=42, val_size=0.2,
                       train_transform = None, num_workers = 4):
    if train_transform is None:
        train_transform = transforms.Compose([
            transforms.ToTensor() 
        ])
    
    test_transform = transforms.Compose([
        transforms.ToTensor()
    ])

    base_dataset = EmotionImageDataset(data_dir, split="train", image_size=image_size, transform=None)
    labels = [label for _, label in base_dataset.samples]
    # Индексы для разделения
    train_idx, val_idx = train_test_split(
        np.arange(len(base_dataset)),
        test_size=val_size,
        random_state=random_state,
        stratify=labels
    )

    train_dataset_full = EmotionImageDataset(data_dir, split="train", image_size=image_size, transform=train_transform)
    val_dataset_full = EmotionImageDataset(data_dir, split="train", image_size=image_size, transform=test_transform)

    train_dataset = Subset(train_dataset_full, train_idx)
    val_dataset = Subset(val_dataset_full, val_idx)
    test_dataset = EmotionImageDataset(data_dir, split="test", image_size=image_size, transform=test_transform)

    pin_mem = torch.cuda.is_available()
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers, pin_memory=pin_mem)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers, pin_memory=pin_mem)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers, pin_memory=pin_mem)
    
    return train_loader, val_loader, test_loader