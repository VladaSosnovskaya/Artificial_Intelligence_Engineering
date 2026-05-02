import torch
import yaml
from PIL import Image
import numpy as np
from torchvision import transforms
from src.models.cnn import EmotionCNN
from src.constants import NUM_CLASSES, CONFIG_PATH, EMOTION_LABELS, CHECKPOINTS_PATH

class InferenceEngine:
    def __init__(self):
        with open(f"{CONFIG_PATH}/inference_config.yaml") as f:
            self.config = yaml.safe_load(f)
            
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.model = EmotionCNN(num_classes=NUM_CLASSES)

        model_name = self.config["model_name"]
        model_path = f"{CHECKPOINTS_PATH}/{model_name}"
        self.model.load_state_dict(torch.load(model_path, map_location=self.device, weights_only=True))
        self.model.to(self.device)
        self.model.eval()
        
        self.preprocess = transforms.Compose([
            transforms.Resize((self.config["image_size"], self.config["image_size"])),
            transforms.Grayscale(num_output_channels=1),
            transforms.ToTensor()
        ])

        print(f"InferenceEngine загружен на {self.device}")

    def predict(self, image):
        tensor = self.preprocess(image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            logits = self.model(tensor)
            probs = torch.softmax(logits, dim=1)[0]
            pred_idx = probs.argmax().item()
            confidence = probs[pred_idx].item()
            
        emotion = EMOTION_LABELS[pred_idx]
        is_confident = confidence >= self.config["confidence_threshold"]
        
        return {
            "emotion": emotion if is_confident else "unknown",
            "confidence": round(confidence, 4),
            "is_confident": is_confident,
            "device": str(self.device)
        }

engine = InferenceEngine()