import aiohttp
from urllib.parse import quote
from astrbot.api.all import *

# 配置
API_KEY = "c60b5ffa3d6b63056c772584ca1c8acb5369d75a967f14b9f72e03fabc97cb72"
AI_API_URL = "https://missqiu.icu/API/aitl.php"
HEADIMG_URL_TEMPLATE = "http://q.qlogo.cn/headimg_dl?dst_uin={qq}&spec=640&img_type=jpg"
PROMPT = "解读一下这个头像，不要输出markdown格式，要纯文本返回"

@register("avatar_interpreter", "解读头像", "AI解读用户头像", "1.0")
class AvatarInterpreterPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @event_message_type(EventMessageType.GROUP_MESSAGE)
    async def on_group_message(self, event: AstrMessageEvent):
        if event.message_str.strip() != "解读头像":
            return

        # 获取用户 QQ 号（sender_id 在 AstrBot 中通常是字符串形式的 QQ 号）
        qq = str(event.sender.sender_id)
        if not qq.isdigit():
            yield event.chain_result([Plain(text="❌ 无法识别您的 QQ 号。")])
            return

        # 构造头像 URL
        avatar_url = HEADIMG_URL_TEMPLATE.format(qq=qq)
        encoded_avatar_url = quote(avatar_url, safe='')

        # 构造完整请求 URL
        request_url = (
            f"{AI_API_URL}"
            f"?apikey={API_KEY}"
            f"&text={quote(PROMPT, safe='')}"
            f"&url={encoded_avatar_url}"
        )

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(request_url, timeout=30) as resp:
                    result_text = await resp.text()
                    if resp.status != 200:
                        self.context.logger.error(f"AI API error {resp.status}: {result_text}")
                        yield event.chain_result([Plain(text="❌ AI 解读失败，请稍后再试。")])
                        return
                    # 返回纯文本结果（已要求接口不返回 markdown）
                    output = result_text.strip()
                    if not output:
                        yield event.chain_result([Plain(text="⚠️ AI 返回内容为空。")])
                    else:
                        yield event.chain_result([Plain(text=output)])
        except asyncio.TimeoutError:
            yield event.chain_result([Plain(text="❌ 请求超时，请稍后再试。")])
        except Exception as e:
            self.context.logger.error(f"请求 AI 接口出错: {e}")
            yield event.chain_result([Plain(text="❌ 网络异常，请稍后再试。")])
