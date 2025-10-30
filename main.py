from astrbot.api.all import *
from astrbot.api.event import filter, AstrMessageEvent
import random
import aiohttp
import asyncio
import tempfile
import os


@register("astrbot_plugin_qyws", "mingrixiangnai", "随机千原万神语音", "1.1", "https://github.com/mingrixiangnai/qyws")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.api_url = "http://api.ocoa.cn/api/sjyy.php?type=voice"

    @filter.regex(r".*千原万神.*")
    async def wsde_handler(self, message: AstrMessageEvent):
        """千原万神 随机播放语音"""
        try:
            yield message.plain_result("正在获取随机音乐...")
            
            # 下载音频文件
            temp_path = None
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.api_url) as response:
                        if response.status == 200:
                            # 创建临时文件
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                                temp_path = temp_file.name
                                audio_content = await response.read()
                                temp_file.write(audio_content)
                            
                            # 发送语音
                            chain = [Record.fromFileSystem(temp_path)]
                            yield message.chain_result(chain)
                            
                        else:
                            yield message.plain_result("获取语音失败，请稍后重试")
            except Exception as e:
                yield message.plain_result(f"获取语音时出错：{str(e)}")
            finally:
                # 清理临时文件
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except:
                        pass
                        
        except Exception as e:
            yield message.plain_result(f"播放语音时出错：{str(e)}")