import aiohttp
from urllib.parse import quote
from astrbot.api.all import *

# API 配置
API_KEY = "c60b5ffa3d6b63056c772584ca1c8acb5369d75a967f14b9f72e03fabc97cb72"
AI_API_URL = "https://missqiu.icu/API/aitl.php"
HEADIMG_URL_TEMPLATE = "http://q.qlogo.cn/headimg_dl?dst_uin={user_id}&spec=640&img_type=jpg"
PROMPT = "解读一下这个头像，不要输出markdown格式，要纯文本返回"

@register("avatar_interpreter", "解读头像", "AI解读用户头像", "1.0")
class AvatarInterpreterPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @event_message_type(EventMessageType.GROUP_MESSAGE)
    async def on_group_message(self, event: AstrMessageEvent):
        msg = event.message_str.strip()
        if msg != "解读头像":
            return

        user_id = event.sender.user_id  # 获取用户 QQ 号
        if not user_id:
            yield event.chain_result([Plain(text="❌ 无法获取您的 QQ 号。")])
            return

        # 构造头像 URL
        avatar_url = HEADIMG_URL_TEMPLATE.format(user_id=user_id)
        
        # URL 编码（防止特殊字符）
        encoded_avatar_url = quote(avatar_url, safe='')

        # 构造完整 AI 请求 URL
        full_url = f"{AI_API_URL}?apikey={API_KEY}&text={quote(PROMPT, safe='')}&url={encoded_avatar_url}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(full_url, timeout=30) as resp:
                    if resp.status != 200:
                        text = await resp.text()
                        self.context.logger.error(f"AI API error ({resp.status}): {text}")
                        yield event.chain_result([Plain(text="❌ AI 解读失败，请稍后再试。")])
                        return
                    result = await resp.text()
                    # 确保结果非空
                    if not result.strip():
                        yield event.chain_result([Plain(text="⚠️ AI 返回内容为空。")])
                        return
                    yield event.chain_result([Plain(text=result.strip())])
        except asyncio.TimeoutError:
            yield event.chain_result([Plain(text="❌ 请求超时，请稍后再试。")])
        except Exception as e:
            self.context.logger.error(f"AI request failed: {e}")
            yield event.chain_result([Plain(text="❌ 网络异常，请稍后再试。")])
