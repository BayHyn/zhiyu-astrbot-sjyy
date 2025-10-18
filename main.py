from astrbot.api.all import *
from astrbot.api.event import filter, AstrMessageEvent
import httpx
import tempfile


@register("music_sjyy", "知鱼", "随机音乐", "1.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.api_url = "http://api.ocoa.cn/api/sjyy.php"

    async def _fetch_random_voice(self) -> str:
        """从接口获取音频文件"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.api_url)
                response.raise_for_status()
                
                # 直接保存为临时文件
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                    tmp_file.write(response.content)
                    return tmp_file.name
                    
        except Exception as e:
            logger.error(f"获取音频失败: {e}")
            return None

    @filter.regex(r".*随机音乐.*")
    async def wsde_handler(self, message: AstrMessageEvent):
        """处理音乐请求"""
        voice_path = await self._fetch_random_voice()
        if not voice_path:
            yield message.plain_result("获取音乐失败，请稍后再试。")
            return
        
        try:
            # 直接发送语音消息
            chain = [Record.fromFileSystem(voice_path)]
            yield event.chain_result(chain)
        except Exception as e:
            yield message.plain_result(f"播放音乐时出错：{str(e)}")
