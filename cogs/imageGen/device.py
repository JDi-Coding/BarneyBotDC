import torch

def get_device():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return device

#this class will Output the current Device
class Device:
    def __init__(self):
        self.currentdevice = get_device()