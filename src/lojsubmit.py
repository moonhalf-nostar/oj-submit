import asyncio
import httpx


class AsyncLojCrawler:
    def __init__(self, aclient: httpx.AsyncClient):
        self.aclient = aclient

    async def submit(self):
        """提交代码，返回 submission_id"""
        # 重复提交有被拒绝连接的情况出现，需注意
        loj_submit_url = "https://api.loj.ac/api/submission/submit"
        payload = {
            "problemId": 1,
            "content": {
                "code": '#include <iostream>\nint main() {\n    long long a, b;\n    std::cin >> a >> b;\n    printf("%lld\\n", a + b % 13);\n    return 0;\n}',
                "language": "cpp",
                "compileAndRunOptions": {
                    "compiler": "g++",
                    "std": "c++11",
                    "O": "2",
                    "m": "64",
                },
            },
            "uploadInfo": None,
        }
        # 提交并获取提交 id
        resp = await self.aclient.post(loj_submit_url, json=payload)
        submission_id = resp.json()["submissionId"]
        print(f"{submission_id = }")
        return submission_id

    async def get_sm_info(self, sm_id: int):
        sm_info_url = "https://api.loj.ac/api/submission/getSubmissionDetail"
        smi_payload = {"submissionId": str(sm_id), "locale": "zh_CN"}
        smi_resp = await self.aclient.post(sm_info_url, json=smi_payload)
        sm_info = smi_resp.json()
        # print(sm_info)
        while (
            not sm_info["progress"] or sm_info["progress"]["progressType"] != "Finished"
        ):
            smi_resp = await self.aclient.post(sm_info_url, json=smi_payload)
            sm_info = smi_resp.json()
            # print(sm_info)
            print("judge pending... wait 1s")
            await asyncio.sleep(1)
        return sm_info


async def main():
    async with httpx.AsyncClient() as aclient:
        aclient.headers.update(
            {
                "accept": "application/json, text/plain, */*",
                "accept-language": "zh-CN,zh;q=0.9",
                # 需要登录的用户
                "authorization": "",
                "content-type": "application/json",
                "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                # "cookie": "_ga=GA1.2.659647178.1747556898; _gid=GA1.2.2004860713.1747556898",
                "Referer": "https://api.loj.ac/api/cors/xdomain.html",
                "Referrer-Policy": "strict-origin-when-cross-origin",
            }
        )
        crawler = AsyncLojCrawler(aclient)
        sm_id = await crawler.submit()
        sm_info = await crawler.get_sm_info(sm_id)
        print(sm_info)


if __name__ == "__main__":
    asyncio.run(main())
