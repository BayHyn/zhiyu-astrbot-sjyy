from astrbot.api.all import *
from astrbot.api.event import filter, AstrMessageEvent
import random
import aiohttp
import asyncio
from typing import Optional


@register("astrbot_plugin_qyws", "mingrixiangnai", "随机千原万神语音", "1.1", "https://github.com/mingrixiangnai/qyws")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.api_url = "http://api.ocoa.cn/api/sjyy.php?type=voice"

    async def _get_voice_url(self) -> Optional[str]:
        """通过API获取随机语音URL"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(self.api_url) as response:
                    if response.status == 200:
                        # 检查响应类型
                        content_type = response.headers.get('Content-Type', '').lower()
                        
                        # 如果是JSON响应
                        if 'application/json' in content_type:
                            data = await response.json()
                            # 根据API实际返回结构调整
                            # 可能的字段名：url, voice_url, audio_url, data等
                            if isinstance(data, dict):
                                return data.get('url') or data.get('voice_url') or data.get('audio_url') or data.get('data')
                            elif isinstance(data, str):
                                return data
                        # 如果是音频文件
                        elif any(audio_type in content_type for audio_type in ['audio/mpeg', 'audio/wav', 'audio/ogg']):
                            return str(response.url)
                        # 其他情况，直接返回URL（可能是重定向后的URL）
                        else:
                            return str(response.url)
                    else:
                        self.context.logger.error(f"API响应错误: {response.status}")
                        return None
                        
        except asyncio.TimeoutError:
            self.context.logger.error("获取语音API超时")
            return None
        except Exception as e:
            self.context.logger.error(f"获取语音API失败: {str(e)}")
            return None

    @filter.regex(r".*千原万神.*")  # 匹配关键词
    async def wsde_handler(self, message: AstrMessageEvent):
        """千原万神 随机播放语音"""
        try:
            # 显示获取中提示
            yield message.plain_result("正在获取随机音乐...")
            
            voice_url = await self._get_voice_url()
            
            if not voice_url:
                yield message.plain_result("获取语音失败，请稍后重试")
                return

            # 发送语音消息
            async for msg in self.send_voice_message(message, voice_url):
                yield msg

        except Exception as e:
            yield message.plain_result(f"播放语音时出错：{str(e)}")

    async def send_voice_message(self, event: AstrMessageEvent, voice_url: str):
        """发送语音消息"""
        try:
            # 使用Record.fromUrl从URL直接播放音频
            chain = [Record.fromUrl(voice_url)]
            yield event.chain_result(chain)
        except Exception as e:
            yield event.plain_result(f"发送语音失败：{str(e)}")