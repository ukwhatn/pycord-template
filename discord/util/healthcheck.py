import logging

import discord
from aiohttp import web


class HealthCheckServer:
    def __init__(self, client: discord.Client, port: int, latency_threshold: float):
        self.client = client
        self.port = port
        self.latency_threshold = latency_threshold
        self.app = web.Application()
        self.app.router.add_get('/', self.handle)
        self.logger = logging.getLogger("HealthCheckServer")

    async def handle(self, request):
        if self.client.is_ready() and self.client.latency < self.latency_threshold:
            return web.Response(text="OK")
        else:
            return web.Response(status=500, text="NOT OK")

    async def start(self):
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', self.port)
        await site.start()
        self.logger.info(f"Health check server started on port {self.port}")


async def start_server(client: discord.Client, port: int, latency_threshold: float):
    server = HealthCheckServer(client, port, latency_threshold)
    await server.start()
