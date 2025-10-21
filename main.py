import aiohttp
import asyncio
from astrbot.api.all import *

@register("avatar_interpreter", "解读头像", "AI解读用户头像", "1.0")
class AvatarInterpreterPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
    
    @event_message_type(EventMessageType.GROUP_MESSAGE)
    async def on_group_message(self, event: AstrMessageEvent):
        msg = event.message_str.strip()
        if msg != "解读头像":
            return

        # 获取用户 QQ 号（sender_id）
        user_id = event.sender.sender_id
        if not user_id:
            yield event.chain_result([Plain(text="❌ 无法获取您的 QQ 号。")])
            return

        # 构造头像链接
        avatar_url = f"http://q.qlogo.cn/headimg_dl?dst_uin={user_id}&spec=640&img_type=jpg"

        # 构造 AI 接口 URL（text 已固定，url 直接拼接）
        api_url = (
            "https://missqiu.icu/API/aitl.php"
            "?apikey=c60b5ffa3d6b63056c772584ca1c8acb5369d75a967f14b9f72e03fabc97cb72"
            "&text=解读一下这个头像，不要输出markdown格式，要纯文本返回"
            f"&url={avatar_url}"
        )

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as response:
                    if response.status == 200:
                        result_text = await response.text()
                        if result_text.strip():
                            yield event.chain_result([Plain(text=result_text.strip())])
                        else:
                            yield event.chain_result([Plain(text="⚠️ AI 返回内容为空。")])
                    else:
                        self.context.logger.error(f"AI接口返回状态码: {response.status}")
                        yield event.chain_result([Plain(text="❌ AI 解读失败，请稍后再试。")])
        except Exception as e:
            self.context.logger.error(f"请求AI接口出错: {str(e)}")
            yield event.chain_result([Plain(text="❌ 网络请求异常，请稍后再试。")])
