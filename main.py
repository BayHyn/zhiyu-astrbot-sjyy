async def _fetch_random_voice(self) -> Optional[str]:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 第一步：获取 JSON
            response = await client.get(self.api_url)
            response.raise_for_status()
            
            data = response.json()
            audio_url = data.get("url")
            if not audio_url:
                logger.error("API 返回的 JSON 中缺少 url 字段")
                return None

            # 第二步：下载音频，添加 headers 模拟浏览器
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
                "Referer": "http://ovoc.cn/"  # 关键！告诉服务器来源是它自己
            }
            audio_resp = await client.get(audio_url, headers=headers)
            audio_resp.raise_for_status()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                tmp_file.write(audio_resp.content)
                return tmp_file.name

    except Exception as e:
        logger.error(f"获取语音 API 失败: {e}", exc_info=True)
        return None
