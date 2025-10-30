from astrbot.api.all import *
from astrbot.api.event import filter, AstrMessageEvent
import httpx
from typing import Optional
import json

@register("music_sjyy", "知鱼", "随机音乐", "1.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.api_url = "http://api.ocoa.cn/api/sjyy.php"

    async def _fetch_random_voice(self) -> Optional[bytes]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.api_url)
                response.raise_for_status()
                data = response.json()
                audio_url = data.get("url")
                if not audio_url:
                    return None
                audio_resp = await client.get(audio_url, timeout=30.0)
                audio_resp.raise_for_status()
                return audio_resp.content
        except Exception as e:
            logger.error(f"获取语音 API 失败: {e}")
            return None

    @filter.regex(r".*随机音乐.*")
    async def wsde_handler(self, message: AstrMessageEvent):
        try:
            voice_data = await self._fetch_random_voice()
            if not voice_data:
                yield message.plain_result("获取语音失败 请稍后再试")
                return
            chain = [Record.fromBytes(voice_data, "audio.mp3")]
            yield message.chain_result(chain)
        except Exception as e:
            yield message.plain_result(f"播放语音时出错：{str(e)}")