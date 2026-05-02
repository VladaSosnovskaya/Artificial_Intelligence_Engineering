import argparse
import yaml
from src.data.loader import create_dataloaders
from src.models.cnn import train_cnn, eval_cnn
from src.constants import DATA_PATH, CONFIG_PATH

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=f"{CONFIG_PATH}/training_best.yaml")
    parser.add_argument("--model_name", default=f"CNN_model")

    args = parser.parse_args()

    with open(args.config) as f: cfg = yaml.safe_load(f)

    train_loader, val_loader, test_loader = create_dataloaders(DATA_PATH, batch_size=cfg["batch_size"])

    train_cnn(train_loader, val_loader, epochs=cfg["epochs"], lr=cfg["lr"], name=args.model_name, 
                            weight_decay=cfg["wd"], patience=cfg["patience"])

if __name__ == "__main__":
    main()