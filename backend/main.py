import os

from aiohttp import web

from src.app import init_app
from src.utils.settings import base_settings

app = init_app()

if __name__ == '__main__':
    try:
        web.run_app(
            app,
            host='0.0.0.0',
            port=int(os.environ.get('PORT', 5173)),
        )
    except KeyboardInterrupt:
        base_settings.logger.info('Received keyboard interrupt...')
    except Exception as e:
        base_settings.logger.error(f'Server error: {e}')
    finally:
        base_settings.logger.info('Server shutdown complete.')
