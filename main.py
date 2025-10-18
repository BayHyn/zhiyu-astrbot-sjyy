from astrbot.api.all import *
from astrbot.api.event import filter, AstrMessageEvent
import random
import os
import tempfile
import httpx
from typing import Optional


@register("music_sjyy", "知鱼", "随机音乐", "1.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.api_url = "http://api.ocoa.cn/api/sjyy.php"  

    async def _fetch_random_voice(self) -> Optional[str]:

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.api_url)
                response.raise_for_status()

                content_type = response.headers.get('content-type', '').lower()
                if 'audio' not in content_type and 'octet-stream' not in content_type:                    
                    pass
             
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                    tmp_file.write(response.content)
                    return tmp_file.name

        except Exception as e:
            logger.error(f"获取语音 API 失败: {e}")
            return None

    @filter.regex(r".*随机音乐.*") 
    async def wsde_handler(self, message: AstrMessageEvent):
        
        try:
            voice_path = await self._fetch_random_voice()
            if not voice_path:
                yield message.plain_result("获取语音失败，请稍后再试。")
                return

            

            async for msg in self.send_voice_message(message, voice_path):
                yield msg

          

        except Exception as e:
            yield message.plain_result(f"播放语音时出错：{str(e)}")

    async def send_voice_message(self, event: AstrMessageEvent, voice_file_path: str):
    
        try:
            chain = [Record.fromFileSystem(voice_file_path)]
            yield event.chain_result(chain)
        except Exception as e:
            yield event.plain_result(f"发送语音失败：{str(e)}")
