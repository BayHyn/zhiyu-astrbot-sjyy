import aiohttp
from astrbot.api import logger
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register


@register("avatar_interpreter", "解读头像", "AI解读用户头像", "1.0")
class AvatarInterpreterPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.command("解读头像")
    async def interpret_avatar(self, event: AstrMessageEvent):
        sender_id = event.get_sender_id()
        if not sender_id:
            yield event.plain_result("无法获取您的QQ号")
            return

        yield event.plain_result("头像解读中...")

        # ✅ 使用你指定的、经过验证的头像链接格式
        avatar_url = f"http://q.qlogo.cn/headimg_dl?dst_uin={sender_id}&spec=640&img_type=jpg"

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
                            yield event.plain_result(result_text.strip())
                        else:
                            yield event.plain_result("AI返回内容为空")
                    else:
                        logger.error(f"AI接口返回状态码: {response.status}")
                        yield event.plain_result("头像解读失败 请稍后再试")
        except Exception as e:
            logger.error(f"请求AI接口出错: {str(e)}")
            yield event.plain_result("网络请求异常 请稍后再试")
