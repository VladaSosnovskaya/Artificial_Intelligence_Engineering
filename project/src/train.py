import argparse
import yaml
from src.data.loader import create_dataloaders
from src.models.cnn import train_cnn, eval_cnn
from src.constants import DATA_PATH, CONFIG_PATH
from src.features.image_transforms import get_train_transform
from src.utils.experiment_logger import log_experiment

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="None")
    parser.add_argument("--model_name", default="None")
    parser.add_argument("--epochs", default="None")
    parser.add_argument("--lr", default="None")
    parser.add_argument("--wd", default="None")
    parser.add_argument("--patience", default="None")
    parser.add_argument("--batch_size", default="None")
    parser.add_argument("--augmentation", default="base")

    args = parser.parse_args()

    config = f"{CONFIG_PATH}/training_best.yaml" if args.config == "None" else args.config

    with open(config) as f: cfg = yaml.safe_load(f)

    epochs = cfg["epochs"] if args.epochs == "None" else args.epochs
    name = cfg["model_name"]
    model_name=f"{name}_finetuning" if args.model_name == "None" else args.model_name
    lr = cfg["lr"] if args.lr == "None" else args.lr
    wd = cfg["wd"] if args.wd == "None" else args.wd
    patience = cfg["patience"] if args.patience == "None" else args.patience
    batch_size = cfg["batch_size"] if args.batch_size == "None" else args.batch_size
    augmentation = cfg["augmentation"] if args.augmentation == "base" else args.augmentation

    print(f"Выбранный конфиг: {config}. Параметры обучения: model_name = {model_name}, epochs = {epochs}, lr = {lr}, wd = {wd}, patience = {patience}, batch_size = {batch_size}, augs = {augmentation}")

    augmentation = get_train_transform(augmentation)
    train_loader, val_loader, test_loader = create_dataloaders(DATA_PATH, batch_size=int(batch_size))

    model, hist = train_cnn(train_loader, val_loader, epochs=int(epochs), lr=float(lr), name=model_name, 
                            weight_decay=float(wd), patience=int(patience))
    
    y_true, y_pred = eval_cnn(model, test_loader)
    experiment_name = "user_train"
    training_cfg = {
        "experiment_name": experiment_name,
        "model_name": model_name,
        "epochs": len(hist["train_loss"]),
        "lr": lr,
        "wd": wd,
        "patience": patience,
        "batch_size": batch_size,
        "augmentation": name
    }

    log_experiment(experiment_name, model_name, y_true, y_pred, training_cfg)

if __name__ == "__main__":
    main()