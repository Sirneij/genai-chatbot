import json
from weakref import WeakSet

from aiohttp import WSCloseCode, web
from aiohttp.web import Request, Response, WebSocketResponse

from src.utils.auto_chat_engine import gpt_question_and_answer
from src.utils.base import cleanup_model
from src.utils.chat_engine import squad_question_answering

WEBSOCKETS = web.AppKey("websockets", WeakSet[WebSocketResponse])


async def start_background_tasks(app: web.Application) -> None:
    """Initialize application background tasks."""
    app[WEBSOCKETS] = WeakSet()


async def cleanup_app(app: web.Application) -> None:
    """Cleanup WebSocket connections on shutdown."""
    # Cleanup models
    await cleanup_model()
    # Close all WebSocket connections
    for websocket in set(app[WEBSOCKETS]):  # type: ignore
        await websocket.close(code=WSCloseCode.GOING_AWAY, message=b'Server shutdown')


async def chat_handler(request: Request) -> Response:
    """Handle WebSocket connections."""
    ws = WebSocketResponse()
    await ws.prepare(request)

    request.app[WEBSOCKETS].add(ws)

    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            try:
                data = json.loads(msg.data)
                question_type = data.get('type')
                question = data.get('question', '').strip()
                if not question:
                    await ws.send_str('Error: No question provided.')
                    continue

                if question_type == 'auto':
                    # Stream response token by token.
                    async for token in gpt_question_and_answer(question):
                        await ws.send_json({'answer': token})
                elif question_type == 'masked':
                    # Use squad question answering (non-streamed).
                    answer = await squad_question_answering(question)
                    await ws.send_json({'answer': answer})
                else:
                    await ws.send_str('Error: Unknown question type.')
            except Exception as e:
                await ws.send_str(f'Error processing message: {str(e)}')
        elif msg.type == web.WSMsgType.ERROR:
            request.app[WEBSOCKETS].remove(ws)
            break

    request.app[WEBSOCKETS].remove(ws)

    return ws


def init_app() -> web.Application:
    """Initialize the application."""
    app = web.Application()

    app.router.add_get('/ws', chat_handler)

    # Add startup/cleanup handlers
    app.on_startup.append(start_background_tasks)
    app.on_shutdown.append(cleanup_app)

    return app
