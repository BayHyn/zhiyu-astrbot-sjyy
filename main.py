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
            # 第一步：获取 JSON 数据
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.api_url)
                response.raise_for_status()

                # 解析 JSON
                data = response.json()
                audio_url = data.get("url")
                if not audio_url:
                    logger.error("API 返回的 JSON 中没有 'url' 字段")
                    return None

                # 第二步：下载音频文件
                audio_response = await client.get(audio_url)
                audio_response.raise_for_status()

                # 检查是否是音频类型（可选）
                content_type = audio_response.headers.get('content-type', '').lower()
                if 'audio' not in content_type and 'octet-stream' not in content_type:
                    logger.warning(f"返回内容可能不是音频，Content-Type: {content_type}")

                # 保存到临时文件
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                    tmp_file.write(audio_response.content)
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
