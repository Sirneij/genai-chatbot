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


async def prepare_tokenizer_and_model(model_name: str) -> tuple[AutoTokenizer, AutoModelForCausalLM]:
    """
    Prepare and load the tokenizer and model with hardware-specific optimizations.

    Args:
        model_name (str): The name of the model to load.

    Returns:
        tuple: The loaded tokenizer and model.
    """
    device, _ = get_device()

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side='left', truncation_side='left', use_fast=True)
    tokenizer.pad_token = tokenizer.eos_token

    # Model-specific settings
    load_kwargs = {}
    if 'phi-3' in model_name.lower():
        load_kwargs['trust_remote_code'] = True
        load_kwargs['attn_implementation'] = 'eager'  # No CUDA, so use eager mode
    elif 'starcoder' in model_name.lower():
        load_kwargs['trust_remote_code'] = True

    # Load model based on device
    if device.type == 'cpu':
        # Use float32 for CPU and apply dynamic quantization
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32,
            **load_kwargs,
        )
        model = torch.quantization.quantize_dynamic(model, {torch.nn.Linear}, dtype=torch.qint8)
    elif device.type == 'mps':
        # Use bfloat16 for MPS
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16,
            **load_kwargs,
        ).to(device)

    model.eval()
    return tokenizer, model


async def cleanup_model() -> None:
    """Clear model from memory, important for Apple Silicon"""
    global global_tokenizer, global_model
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
    del global_model
    global_model = None
    global_tokenizer = None


async def get_stopping_strings(type: str, question: str) -> tuple[str, list[str]]:
    """Get stopping strings based on the question type."""
    STOPPING_STRINGS = {
        'normal': {
            'prompt': f'Q: {question}\nA:',
            'end': ['\nQuestion:', '\nQ', '\nB', '\nC', '\nD'],
        },
        'exNormal': {
            'prompt': f'Answer the question using markdown formatting and katex for math.\nAfter providing your complete answer, conclude your response by adding \n==END==\n as the final line, with no text following it. \n\nQ: {question}\n\nA:',
            'end': ['==END==', '\n==END==', '\n==END==\n', '\n==END\n', '\n==END', '\n=='],
        },
    }
    return STOPPING_STRINGS[type]['prompt'], STOPPING_STRINGS[type]['end']
