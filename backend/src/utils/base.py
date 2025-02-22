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
