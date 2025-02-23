import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

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
    """Prepare tokenizer and model with hardware-optimized settings."""
    global global_tokenizer, global_model

    if global_tokenizer is None or global_model is None:
        # Detect hardware
        device, _ = get_device()

        # Model-specific configuration
        load_kwargs = {}
        if 'phi-3' in model_name.lower():
            load_kwargs.update({'trust_remote_code': True, 'attn_implementation': 'eager'})  # Better for CPU/MPS
        elif 'starcoder' in model_name.lower():
            load_kwargs['trust_remote_code'] = True

        # Quantization config
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type='nf4',
            bnb_4bit_compute_dtype=torch.bfloat16,
        )

        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            model_name, padding_side='left', truncation_side='left', use_fast=True
        )
        tokenizer.pad_token = tokenizer.eos_token

        # Load model with hardware-specific optimizations
        if device.type == 'cpu':
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                quantization_config=bnb_config if 'phi-3' in model_name else None,
                torch_dtype=torch.float32,
                **load_kwargs,
            )
        elif device.type == 'mps':
            model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.bfloat16, **load_kwargs).to(
                device
            )
        else:  # CUDA
            model = AutoModelForCausalLM.from_pretrained(
                model_name, torch_dtype=torch.float16, device_map='auto', **load_kwargs
            )

        # Apple Silicon optimizations
        if device.type == 'mps':
            # Add these MPS-specific optimizations
            torch.mps.set_per_process_memory_fraction(0.4)  # Prevent OOM
            torch.mps.empty_cache()
            torch.mps.synchronize()

        model.eval()
        global_tokenizer, global_model = tokenizer, model

    return global_tokenizer, global_model


async def cleanup_model():
    """Clear model from memory, important for Apple Silicon"""
    global global_tokenizer, global_model
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
    del global_model
    global_model = None
    global_tokenizer = None


async def get_stopping_strings(type: str, question: str) -> list[str]:
    """Get stopping strings based on the question type."""
    STOPPING_STRINGS = {
        'normal': {
            'prompt': f'Q: {question}\nA:',
            'end': ['\nQuestion:', '\nQ', '\nB', '\nC', '\nD'],
        },
        'markdownPhind': {
            'prompt': f"""
                Write a detailed technical response in proper markdown format. Include headers, bullet points, and code blocks.
                
                Content: {question}
                
                Format:
                ```
                # Main Topic
                
                ## Section 1
                - Point 1
                - Point 2
                
                ```python
                # Code examples go here
                ```
                
                ## Section 2
                More content...
                ```
                """,
            'end': [
                '\n## Conclusion',
                '\n# References',
                '\n## Summary',
                '\n=== END ===',
                '\n## Final Thoughts',
                '\n# End of Document',
                '\n## Last Updated',
                '\n# Change Log',
                '\n## Revision History',
                '\n=== DONE ===',
                '\n## THE END',
                '\n# Completed',
            ],
        },
        'markdownDeep': {
            'prompt': f'''Q: {question}

                    Please format your answer using markdown with:
                    - Headings (##)
                    - Lists (• or 1.)
                    - Code blocks (```)
                    - Bold/**emphasis**

                    When you're done, end your response with === END ===
                    
                    A:
                    ''',
            'end': [
                '\n```\n\n',  # Code block ending
                '\n## ',  # Next heading
                '\n**Q:',  # New question
                '\n=== END ===',  # End of response
            ],
        },
        'exNormal': {
            'prompt': f'Q: {question}\n\nPlease answer using markdown formatting.\nWhen you are done, let your response be === END ===\nA:',
            'end': ['\nQuestion:', '\nQ', '\nA' '\nB', '\nC', '\nD', '\n=== END ==='],
        },
    }
    return STOPPING_STRINGS[type]['prompt'], STOPPING_STRINGS[type]['end']
