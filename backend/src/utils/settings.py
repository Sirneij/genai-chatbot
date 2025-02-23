import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

logger = logging.getLogger(__name__)


class Settings:
    logger = logger
    FACT_CHECK_TRIGGERS = {
        'capital': ['capital', 'city'],
        'historical': ['invented', 'discovered', 'founded'],
        'scientific': ['physics', 'chemistry', 'biology'],
    }
    WARNING_MESSAGES = {
        'date': "Note: My knowledge cutoff is 2020-01",
        'uncertain': "I cannot verify this with absolute certainty",
        'opinion': "Different perspectives exist on this matter",
    }
    SYSTEM_PROMPT = 'You are an expert Q&A assistant. Provide accurate answers based on the context.'


base_settings = Settings()
MODEL_NAME = 'microsoft/Phi-3-mini-4k-instruct'
tokenizer, model = None, None
