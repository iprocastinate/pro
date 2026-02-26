"""Health check server for cloud deployments - runs independently of main bot"""
import asyncio
from aiohttp import web
import logging

LOGS = logging.getLogger(__name__)

async def health_check(request):
    """Health check endpoint"""
    return web.Response(text="OK", status=200)

async def start_health_server():
    """Start the health check server on port 8000"""
    try:
        app = web.Application()
        app.router.add_get('/health', health_check)
        app.router.add_get('/', health_check)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 8000)
        await site.start()
        
        LOGS.info("Health check server started on port 8000")
        
        # Keep the server running indefinitely
        await asyncio.sleep(float('inf'))
        
    except Exception as e:
        LOGS.error(f"Failed to start health check server: {e}")
        # Still don't fail - health check is not critical
        await asyncio.sleep(float('inf'))
