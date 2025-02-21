from transformers import pipeline

from src.utils.base import get_device


async def squad_question_answering(question: str, context: str) -> str:
    """Answer a question based on the provided context."""
    qa_pipeline = pipeline(
        'question-answering',
        model='distilbert-base-uncased-distilled-squad',
        tokenizer='distilbert-base-uncased-distilled-squad',
        device=-1 if get_device()[1] == 'CPU' else 0,
    )
    result = qa_pipeline(question=question, context=context)
    return result['answer']
