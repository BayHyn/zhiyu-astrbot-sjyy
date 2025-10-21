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

        avatar_url = f"http://api.ocoa.cn/api/qqtx.php?qq={sender_id}"

        api_url = (
            "https://missqiu.icu/API/aitl.php"
            "?apikey=c60b5ffa3d6b63056c772584ca1c8acb5369d75a967f14b9f72e03fabc97cb72"
            "&text=解读一下这个头像，不要输出markdown格式，要纯文本返回"
            f"&url={avatar_url}"
        )

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as response:
                    if response.status != 200:
                        logger.error(f"AI接口HTTP状态码: {response.status}")
                        yield event.plain_result("头像解读失败 请稍后再试")
                        return

                    # ✅ 解析 JSON 并提取 content
                    data = await response.json()
                    content = data["choices"][0]["message"]["content"]
                    if content.strip():
                        yield event.plain_result(content.strip())
                    else:
                        yield event.plain_result("AI返回内容为空")

        except (aiohttp.ClientError, ValueError, KeyError, IndexError) as e:
            logger.error(f"处理AI响应时出错: {str(e)}")
            yield event.plain_result("解析结果失败 请稍后再试")
