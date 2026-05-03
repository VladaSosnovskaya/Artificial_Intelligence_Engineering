from torchvision import transforms

_MEAN = [0.508]
_STD  = [0.212]

def get_train_transform(strategy = "base"):
    base = [transforms.ToTensor(), transforms.Normalize(_MEAN, _STD)]
    
    if strategy == "base":
        return transforms.Compose(base)
    elif strategy == "geo":
        return transforms.Compose([
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(10),
            *base
        ])
    elif strategy == "photo":
        return transforms.Compose([
            transforms.ColorJitter(brightness=0.2, contrast=0.2),
            *base
        ])
    elif strategy == "combined":
        return transforms.Compose([
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.ColorJitter(brightness=0.15, contrast=0.15),
            transforms.GaussianBlur(kernel_size=3),
            *base
        ])
    else:
        raise ValueError(f"Неизвестная стратегия аугментаций: {strategy}")

