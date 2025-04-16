import os
# import openai  # 標記掉 openai
from groq import Groq
# from replit import db
# 引入 TaiwanLotteryCrawler
from TaiwanLottery import TaiwanLotteryCrawler
from my_commands.CaiyunfangweiCrawler import CaiyunfangweiCrawler

# 運彩
import requests

# 設定 API 金鑰
# openai.api_key = os.getenv("OPENAI_API_KEY")  # 標記掉 openai
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 建立 GPT 模型
def get_reply(messages):
    try:
        # openai 相關程式碼被標記
        # response = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo-1106",
        #     messages=messages
        # )
        # reply = response["choices"][0]["message"]["content"]

        # 直接使用 groq
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages,
            max_tokens=2000,
            temperature=1.2
        )
        reply = response.choices[0].message.content
    except groq.GroqError as groq_err:
        reply = f"GROQ API 發生錯誤: {groq_err.message}"
    return reply

# 初始化 TaiwanLotteryCrawler
crawler = TaiwanLotteryCrawler()

# 初始化 CaiyunfangweiCrawler
caiyunfangwei_crawler = CaiyunfangweiCrawler()

def lottoExecrise():
    params = {'sport': 'NBA', 'date': '2024-05-16', 'names': ['洛杉磯湖人', '金州勇士'], 'limit': 6}
    headers = {'X-JBot-Token': 'FREE_TOKEN_WITH_20_TIMES_PRE_DAY'}
    url = 'https://api.sportsbot.tech/v2/records'
    res = requests.get(url, headers=headers, params=params)
    return res.json()

# 建立訊息指令(Prompt)
def generate_content_msg(lottery_type):
    if "威力" in lottery_type:
        last_lotto = crawler.super_lotto()
    elif "大樂" in lottery_type:
        last_lotto = crawler.lotto649()
    elif "539" in lottery_type:
        last_lotto = crawler.daily_cash()
    elif "雙贏彩" in lottery_type:
        last_lotto = crawler.lotto1224()
    elif "3星彩" in lottery_type or "三星彩" in lottery_type:
        last_lotto = crawler.lotto3d()
    elif "4星彩" in lottery_type:
        last_lotto = crawler.lotto4d()
    elif "38樂合彩" in lottery_type:
        last_lotto = crawler.lotto38m6()
    elif "39樂合彩" in lottery_type:
        last_lotto = crawler.lotto39m5()
    elif "49樂合彩" in lottery_type:
        last_lotto = crawler.lotto49m6()
    elif "運彩" in lottery_type:
        last_lotto = lottoExecrise()

    if "運彩" not in lottery_type:
        caiyunfangwei_info = caiyunfangwei_crawler.get_caiyunfangwei()
        content_msg = f'你現 in是一位專業的樂透彩分析師, 使用{lottery_type}的資料來撰寫分析報告:\n'
        content_msg += f'近幾期號碼資訊:\n{last_lotto}\n'
        content_msg += f'顯示今天國歷/農歷日期：{caiyunfangwei_info["今天日期"]}\n'
        content_msg += f'今日歲次：{caiyunfangwei_info["今日歲次"]}\n'
        content_msg += f'財神方位：{caiyunfangwei_info["財神方位"]}\n'
        content_msg += '最冷號碼，最熱號碼\n'
        content_msg += '請給出完整的趨勢分析報告，最近所有每次開號碼,'
        content_msg += '並給3組與彩類同數位數字隨機號和不含特別號(如果有的彩種,)\n'
        content_msg += '第1組最冷組合:給與該彩種開獎同數位數字隨機號和(數字小到大)，威力彩多顯示二區才顯示，其他彩種不含二區\n'
        content_msg += '第2組最熱組合:給與該彩種開獎同數位數字隨機號和(數字小到大)，威力彩多顯示二區才顯示，其他彩種不含二區\n'
        content_msg += '第3組隨機組合:給與該彩種開獎同數位數字隨機號和(數字小到大)，威力彩多顯示二區才顯示，其他彩種不含二區\n'
        content_msg += '請寫詳細的數字，1不要省略\n'
        content_msg += '{發財的吉祥句20字內要有勵志感}\n'
        # content_msg += '用我提供的歷史資料得知開獎星期：{{星期二}}、{{星期五}}'
        content_msg += """example:   ***財神方位提示***
        國歷：2024/06/19（星期三）
        農曆甲辰年五月十四號
        根據財神方位 :東北
        """
        content_msg += '使用台灣繁體中文。'
    else:
        content_msg = f'你現 in是一位專業的運彩分析師, 使用{lottery_type}的資料來撰寫分析報告:\n'
        content_msg += f'近幾運彩資料資訊:\n{last_lotto}\n'
        content_msg += '{發財的吉祥句20字內要有勵志感}\n'
        content_msg += '使用台灣用詞的繁體中文。'

    return content_msg

def lottery_gpt(lottery_type):
    content_msg = generate_content_msg(lottery_type)
    msg = [{
        "role": "system",
        "content": f"你現 in是一位專業的透券彩分析師, 使用{lottery_type}近期的號碼進行分析，生成一份專業的趨勢分析報告。"
    }, {
        "role": "user",
        "content": content_msg
    }]

    reply_data = get_reply(msg)
    return reply_data
