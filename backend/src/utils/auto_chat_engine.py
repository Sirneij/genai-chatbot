import asyncio

import torch
from torch.cuda.amp import autocast
from transformers import PreTrainedTokenizerFast

from src.utils.base import get_stopping_strings, prepare_tokenizer_and_model
from src.utils.settings import MODEL_NAME


def top_k_top_p_filtering(logits, top_k=0, top_p=1.0, filter_value=-float("Inf")):
    """
    Filter a distribution of logits using top-k and nucleus (top-p) filtering.
    """
    if top_k > 0:
        values, _ = torch.topk(logits, top_k)
        kth_value = values[..., -1, None]
        logits = torch.where(logits < kth_value, torch.full_like(logits, filter_value), logits)

    if top_p < 1.0:
        sorted_logits, sorted_indices = torch.sort(logits, descending=True)
        cumulative_probs = torch.cumsum(torch.softmax(sorted_logits, dim=-1), dim=-1)
        sorted_indices_to_remove = cumulative_probs > top_p
        sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
        sorted_indices_to_remove[..., 0] = 0
        indices_to_remove = sorted_indices[sorted_indices_to_remove]
        logits[indices_to_remove] = filter_value
    return logits


async def stream_chat_response(
    prompt: str,
    tokenizer: PreTrainedTokenizerFast,
    model,
    stopping_strings: list[str],
    max_new_tokens: int = 100,
    temperature: float = 0.7,
    top_k: int = 50,
    top_p: float = 0.9,
    repetition_penalty: float = 1.5,
    repetition_window: int = 10,
) :
    device = next(model.parameters()).device
    eos_token_id = tokenizer.eos_token_id
    inputs = tokenizer(prompt, return_tensors='pt')
    input_ids = inputs['input_ids'].to(device)
    attention_mask = inputs['attention_mask'].to(device)
    full_generated_ids = input_ids
    previous_generated_text = ''
    generated_tokens = []

    for _ in range(max_new_tokens):
        with torch.no_grad():
            if device.type == 'cuda':
                with torch.autocast(device_type='cuda', dtype=torch.float16):
                    outputs = model(full_generated_ids, attention_mask=attention_mask)
            elif device.type == 'mps':
                with torch.autocast(device_type='mps', dtype=torch.bfloat16):
                    outputs = model(full_generated_ids, attention_mask=attention_mask)
            else:  # CPU
                outputs = model(full_generated_ids, attention_mask=attention_mask)

        next_token_logits = outputs.logits[:, -1, :]
        # Apply repetition penalty
        if repetition_penalty != 1.0:
            for token in set(generated_tokens[-20:]):
                next_token_logits[:, token] /= repetition_penalty

        scaled_logits = next_token_logits / temperature
        filtered_logits = top_k_top_p_filtering(scaled_logits[0], top_k=top_k, top_p=top_p)
        probabilities = torch.softmax(filtered_logits, dim=-1)
        next_token = torch.multinomial(probabilities, num_samples=1).unsqueeze(0)
        current_token = next_token.item()

        full_generated_ids = torch.cat([full_generated_ids, next_token], dim=-1)
        attention_mask = torch.cat([attention_mask, torch.ones_like(next_token)], dim=-1)
        generated_tokens.append(current_token)

        if current_token == eos_token_id:
            break

        current_generated_text = tokenizer.decode(
            full_generated_ids[0][input_ids.shape[1] :].cpu(), skip_special_tokens=True
        )

        # Check stopping conditions
        if any(stop_str in current_generated_text for stop_str in stopping_strings):
            break
        if (
            len(generated_tokens) >= 2 * repetition_window
            and generated_tokens[-repetition_window:] == generated_tokens[-2 * repetition_window : -repetition_window]
        ):
            break

        diff = current_generated_text[len(previous_generated_text) :]
        if diff:
            yield diff
            previous_generated_text = current_generated_text

        if device.type == 'mps':
            await asyncio.sleep(0.001)  # Yield event loop for MPS
        elif device.type == 'cpu':
            await asyncio.sleep(0.005)  # Reduce CPU load
        else:
            await asyncio.sleep(0)

    # Return the final text
    yield '[END]'


async def gpt_question_and_answer(question: str) :
    """Stream an answer with repetition penalty and better stopping checks."""
    tokenizer, model = await prepare_tokenizer_and_model(MODEL_NAME)
    prompt, stopping_strings = await get_stopping_strings('exNormal', question)
    async for chunk in stream_chat_response(
        prompt,
        tokenizer,
        model,
        stopping_strings=stopping_strings,
        max_new_tokens=2000,  # Increase this for longer outputs
        top_p=0.95,
    ):
        yield chunk
