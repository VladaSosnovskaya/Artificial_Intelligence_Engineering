import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import accuracy_score, f1_score
from src.constants import CHECKPOINTS_PATH

class EmotionCNN(nn.Module):
    def __init__(self, num_classes: int = 7, dropout_rate: float = 0.4):
        super().__init__()
        self.features = nn.Sequential(
            # Блок 1
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.Conv2d(32, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Dropout2d(0.2),
            
            # Блок 2
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Dropout2d(0.2),
            
            # Блок 3
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d(1),  # Глобальный пулинг -> (128, 1, 1)
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128, 64),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate),
            nn.Linear(64, num_classes)
        )
    
    def forward(self, x):
        x = self.features(x)
        return self.classifier(x)


def train_cnn(train_loader, val_loader, epochs=30, lr=1e-3, name="cnn", weight_decay=1e-4, patience=8, device="cpu"):
    model = EmotionCNN().to(device)
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max", factor=0.5, patience=5)
    
    best_f1, patience_cnt, history = 0, 0, {"train_loss": [], "val_acc": [], "val_f1": []}

    print(f"Начало эксперимента {name}. Число эпох = {epochs}")
    
    for epoch in range(epochs):
        model.train()
        loss_sum = 0
        for xb, yb in train_loader:
            xb, yb = xb.to(device), yb.to(device)
            optimizer.zero_grad()
            out = model(xb)
            loss = criterion(out, yb)
            loss.backward(); optimizer.step()
            loss_sum += loss.item()
            
        model.eval()
        val_preds, val_labels = [], []
        with torch.no_grad():
            for xb, yb in val_loader:
                xb = xb.to(device)
                val_preds.extend(model(xb).argmax(1).cpu().numpy())
                val_labels.extend(yb.numpy())
                
        v_acc = accuracy_score(val_labels, val_preds)
        v_f1 = f1_score(val_labels, val_preds, average="macro")
        scheduler.step(v_f1)
        
        history["train_loss"].append(loss_sum/len(train_loader))
        history["val_acc"].append(v_acc)
        history["val_f1"].append(v_f1)

        print(f"Эпоха {epoch+1}. Валидационные метрики: acc = {v_acc}, f1 = {v_f1}")
        
        if v_f1 > best_f1:
            best_f1 = v_f1; patience_cnt = 0
            torch.save(model.state_dict(), f"{CHECKPOINTS_PATH}/{name}_checkpoint.pth")
        else:
            patience_cnt += 1
        if patience_cnt >= patience:
            print("Ранняя остановка")
            break
            
    return model, history

def eval_cnn(model, test_loader):
    model.eval()
    y_true, y_pred = [], []
    device = next(model.parameters()).device
    with torch.no_grad():
        for xb, yb in test_loader:
            xb = xb.to(device)
            y_pred.extend(model(xb).argmax(1).cpu().numpy())
            y_true.extend(yb.numpy())
    return y_true, y_pred