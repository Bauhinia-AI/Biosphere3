from aiohttp import web
from datetime import datetime
from pathlib import Path


class WebMonitor:
    def __init__(self, character_manager):
        self.character_manager = character_manager
        self.template_dir = Path(__file__).parent / "templates"

    async def index(self, request):
        """返回监控页面的 HTML"""
        with open(self.template_dir / "index.html") as f:
            html = f.read()
        return web.Response(text=html, content_type="text/html")

    async def user_messages(self, request):
        """返回特定角色的消息记录页面"""
        with open(self.template_dir / "user_messages.html") as f:
            html = f.read()
        return web.Response(text=html, content_type="text/html")

    async def get_status(self, request):
        """返回服务器状态的 JSON 数据"""
        try:
            character_status = await self.character_manager.get_status()

            status = {
                "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "character_monitor": character_status,
            }

            return web.json_response(status)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def get_user_messages(self, request):
        """返回特定角色的消息记录页面"""
        character_id = int(request.match_info["character_id"])
        character = self.character_manager.get_character(character_id)
        if not character:
            return web.json_response({"error": "Character not found"}, status=404)

        return web.json_response(character.message_log)

    async def setup(self, host="localhost", port=8000):
        """设置并启动 HTTP 服务器"""
        app = web.Application()
        app.router.add_get("/", self.index)
        app.router.add_get("/status", self.get_status)
        app.router.add_get("/user/{character_id}", self.user_messages)
        app.router.add_get("/api/messages/{character_id}", self.get_user_messages)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        return site
