from astrbot.api.all import *
from astrbot.api.event import filter, AstrMessageEvent
import random
import os
import tempfile
import httpx
from typing import Optional


@register("astrbot_plugin_qyws", "mingrixiangnai", "随机千原万神语音", "1.1", "https://github.com/mingrixiangnai/qyws")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.api_url = "http://api.ocoa.cn/api/sjyy.php"  # 随机语音 API

    async def _fetch_random_voice(self) -> Optional[str]:
        """从 API 获取语音，保存为临时文件，返回临时文件路径"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.api_url)
                response.raise_for_status()

                # 检查是否是音频内容
                content_type = response.headers.get('content-type', '').lower()
                if 'audio' not in content_type and 'octet-stream' not in content_type:
                    # 有些 API 不带正确 Content-Type，但能返回 mp3，所以也允许无类型或 application/octet-stream
                    pass

                # 创建临时文件（后缀 .mp3）
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                    tmp_file.write(response.content)
                    return tmp_file.name

        except Exception as e:
            logger.error(f"获取语音 API 失败: {e}")
            return None

    @filter.regex(r".*千原万神.*")  # 匹配关键词
    async def wsde_handler(self, message: AstrMessageEvent):
        """千原万神：通过 API 获取并发送随机语音"""
        try:
            voice_path = await self._fetch_random_voice()
            if not voice_path:
                yield message.plain_result("获取语音失败，请稍后再试。")
                return

            # 可选：记录日志或语音信息（这里不发送文件名）
            # yield message.plain_result("正在发送语音...")

            async for msg in self.send_voice_message(message, voice_path):
                yield msg

            # 可选：发送后删除临时文件（注意：有些平台可能异步发送，删太早会出错）
            # 建议保留，或由系统定期清理临时文件
            # os.unlink(voice_path)

        except Exception as e:
            yield message.plain_result(f"播放语音时出错：{str(e)}")

    async def send_voice_message(self, event: AstrMessageEvent, voice_file_path: str):
        """发送语音消息"""
        try:
            chain = [Record.fromFileSystem(voice_file_path)]
            yield event.chain_result(chain)
        except Exception as e:
            yield event.plain_result(f"发送语音失败：{str(e)}")
