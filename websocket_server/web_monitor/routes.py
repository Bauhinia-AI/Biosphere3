from aiohttp import web
from datetime import datetime
import os
from pathlib import Path

class WebMonitor:
    def __init__(self, heartbeat_manager, task_manager):
        self.heartbeat_manager = heartbeat_manager
        self.task_manager = task_manager
        self.template_dir = Path(__file__).parent / "templates"

    async def index(self, request):
        """返回监控页面的 HTML"""
        with open(self.template_dir / "index.html") as f:
            html = f.read()
        return web.Response(text=html, content_type="text/html")

    async def get_status(self, request):
        """返回服务器状态的 JSON 数据"""
        try:
            heartbeat_status = await self.heartbeat_manager.get_status()
            orphaned_task_status = await self.task_manager.get_status()

            status = {
                "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "heartbeat_monitor": heartbeat_status,
                "orphaned_tasks": orphaned_task_status,
            }

            return web.json_response(status)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def setup(self, host="localhost", port=8000):
        """设置并启动 HTTP 服务器"""
        app = web.Application()
        app.router.add_get("/", self.index)
        app.router.add_get("/status", self.get_status)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        return site
