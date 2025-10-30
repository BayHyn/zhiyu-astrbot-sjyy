from astrbot.api.all import *
from astrbot.api.event import filter, AstrMessageEvent
import random
import os
import tempfile
import httpx
import json
from typing import Optional


@register("music_sjyy", "知鱼", "随机音乐", "1.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.api_url = "http://api.ocoa.cn/api/sjyy.php"  

    async def _fetch_random_voice(self) -> Optional[str]:
        """获取随机音乐并返回本地文件路径"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.api_url)
                response.raise_for_status()
                
                # 解析JSON响应
                json_data = response.json()
                audio_url = json_data.get("url")
                
                if not audio_url:
                    logger.error("JSON响应中未找到音频URL")
                    return None
                
                # 下载音频文件
                audio_response = await client.get(audio_url)
                audio_response.raise_for_status()
                
                # 保存到临时文件
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                    tmp_file.write(audio_response.content)
                    return tmp_file.name

        except httpx.RequestError as e:
            logger.error(f"网络请求失败: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            return None
        except Exception as e:
            logger.error(f"获取语音失败: {e}")
            return None

    @filter.regex(r".*随机音乐.*") 
    async def wsde_handler(self, message: AstrMessageEvent):
        """处理随机音乐请求"""
        try:
            voice_path = await self._fetch_random_voice()
            if not voice_path:
                yield message.plain_result("获取语音失败，请稍后再试。")
                return

            # 发送语音消息
            async for msg in self.send_voice_message(message, voice_path):
                yield msg

            # 清理临时文件
            try:
                if os.path.exists(voice_path):
                    os.unlink(voice_path)
            except Exception as e:
                logger.warning(f"清理临时文件失败: {e}")

        except Exception as e:
            yield message.plain_result(f"播放语音时出错：{str(e)}")

    async def send_voice_message(self, event: AstrMessageEvent, voice_file_path: str):
        """发送语音消息"""
        try:
            chain = [Record.fromFileSystem(voice_file_path)]
            yield event.chain_result(chain)
        except Exception as e:
            yield event.plain_result(f"发送语音失败：{str(e)}")