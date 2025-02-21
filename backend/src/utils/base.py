import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from src.utils.settings import model as global_model
from src.utils.settings import tokenizer as global_tokenizer


def get_device() -> tuple[torch.device, str]:
    if torch.cuda.is_available():
        return torch.device('cuda'), 'CUDA (NVIDIA GPU)'
    elif torch.backends.mps.is_available():
        return torch.device('mps'), 'MPS (Apple Metal)'
    else:
        return torch.device('cpu'), 'CPU'


async def prepare_tokenizer_and_model(model_name: str):
    """Prepare the tokenizer and optimized model based on the device."""
    global global_tokenizer, global_model
    if global_tokenizer is None or global_model is None:
        local_tokenizer = AutoTokenizer.from_pretrained(model_name)
        local_model = AutoModelForCausalLM.from_pretrained(model_name)

        device, device_name = get_device()  # Assume this function returns the device
        if device.type == 'cpu':
            # Apply dynamic quantization for CPU
            local_model = torch.quantization.quantize_dynamic(local_model, {torch.nn.Linear}, dtype=torch.qint8)
        elif device.type == 'cuda' or device.type == 'mps':
            # Convert to FP16 for GPU or MPS
            local_model.half()

        local_model.to(device)
        local_model.eval()
        global_tokenizer, global_model = local_tokenizer, local_model

    return global_tokenizer, global_model
