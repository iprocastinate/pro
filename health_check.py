"""Simple HTTP health check server for cloud deployments"""
import asyncio
from aiohttp import web
import logging

logger = logging.getLogger(__name__)

async def health_check(request):
    """Health check endpoint"""
    return web.Response(text="OK", status=200)

async def start_health_server():
    """Start the health check server on port 8000"""
    app = web.Application()
    app.router.add_get('/health', health_check)
    app.router.add_get('/', health_check)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8000)
    await site.start()
    
    logger.info("Health check server started on port 8000")
    return runner

if __name__ == "__main__":
    async def main():
        await start_health_server()
        await asyncio.sleep(3600)  # Keep running
    
    asyncio.run(main())
