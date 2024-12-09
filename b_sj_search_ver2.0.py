# 鸣谢 Coconut_Cake 在 https://blog.csdn.net/Asimoedeus/article/details/134785699 一文中提出的header抓取思路作出的贡献
# 本脚本由飯野龍馬制作完成

import os
import time
import random
import requests
import json
from tkinter import *
from tkinter import messagebox, scrolledtext
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# 全局变量
scraping_active = False
next_id = None
seen_c2c_items_ids = set()
i_want = []
exclude_words = []

# 请求头
headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'content-type': 'application/json',
    'cookie': 'buvid3=EF225A10-0811-1895-C3D7-06F81F1EB53954001infoc; b_nut=1722854354; _uuid=42A1065C7-2E71-31C5-69EB-214F1026816B653742infoc; enable_web_push=DISABLE; buvid4=5C6B8457-9890-60C4-3ED8-4079B6F4FCF154726-024080510-Ci0iq%2FDXwzywKLE%2F2NhRmw%3D%3D; header_theme_version=CLOSE; rpdid=|(u|Jkm~~lkk0J\'u~kk)lRRkR; DedeUserID=27118504; DedeUserID__ckMd5=813cef00b93f795d; buvid_fp_plain=undefined; hit-dyn-v2=1; CURRENT_BLACKGAP=0; fingerprint=a30a652c7f7923d13d9e2fbf9720e987; buvid_fp=a30a652c7f7923d13d9e2fbf9720e987; is-2022-channel=1; match_float_version=ENABLE; share_source_origin=COPY; bsource=search_google; home_feed_column=4; browser_resolution=1177-939; CURRENT_QUALITY=80; SESSDATA=1fafd16f%2C1749050792%2Cfbe83%2Ac1CjDWlT0oJHOFr49Ag18etHfE9vdntOAUAZ3hmoCsBl4kuy6MHvyUq0L8s2jq5CHllAwSVlo2ZGNOUDI5eFI1ODNSU2tHV3FIS1BkNml4R1lwVXNjbDZ1U2xRZkpkOVJPZkZ5M09HRlgzUFZ4YlpPNTBpVDBDNGVqUXpmZ2VBRTlwRlJJemZGM3lBIIEC; bili_jct=da4f50a7c65e7a11dfa104c9cd15bc4d; sid=6lcbnhpo; b_lsid=AF7939B4_1939D1DBB5A; bp_t_offset_27118504=1007898407689256960; CURRENT_FNVAL=2000',
    'origin': 'https://mall.bilibili.com',
    'priority': 'u=1, i',
    'referer': 'https://mall.bilibili.com/neul-next/index.html?page=magic-market_index',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1 Edg/131.0.0.0'
}


# 初始化HTML文件（用于保存符合条件的商品）
def initialize_html():
    with open("items_index.html", "w", encoding="utf-8") as file:
        file.write('<html><head><meta http-equiv="refresh" content="5"></head><body><h1>商品列表</h1>')

# 初始化日志HTML文件（记录所有抓取的商品，符合的标绿，不符合的标红）
def initialize_log_html():
    with open("scraping_log.html", "w", encoding="utf-8") as file:
        file.write('<html><head><meta http-equiv="refresh" content="10"></head><body><h1>抓取日志</h1>')

# 关闭HTML文件
def close_html():
    with open("items_index.html", "a", encoding="utf-8") as file:
        file.write('</body></html>')

# 关闭日志HTML文件
def close_log_html():
    with open("scraping_log.html", "a", encoding="utf-8") as file:
        file.write('</body></html>')

# 抓取数据函数
def fetch_data():
    global next_id
    payload = {
        "priceFilters": ["40000-90000"],
        "categoryFilter": "2312",
        "sortType": "TIME_DESC",
        "nextId": next_id
    }
    try:
        response = requests.post("https://mall.bilibili.com/mall-magic-c/internet/c2c/v2/list",
                                 headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        log_message("成功获取数据。", status=None)
        return response.json()
    except requests.RequestException as e:
        log_message(f"网络请求失败: {e}", status="Error")
        messagebox.showerror("错误", f"网络请求失败: {e}")
        stop_scraping()
        return None

# 商品处理函数
def process_items(items):
    for item in items:
        c2c_items_id = item.get("c2cItemsId")
        c2c_items_name = item.get("c2cItemsName")
        show_price = item.get("showPrice")

        if c2c_items_id and c2c_items_id not in seen_c2c_items_ids:
            seen_c2c_items_ids.add(c2c_items_id)
            # 检查是否符合“想要”的词语
            if any(keyword in c2c_items_name for keyword in i_want):
                save_to_html(c2c_items_id, c2c_items_name, show_price)
                log_item_to_html(c2c_items_name, show_price, matched=True)
                log_message(f"添加商品（符合想要关键词）: {c2c_items_name} - 价格: {show_price}", status="Yes")
            # 不符合“想要”的，则检查“不想要”的词语
            elif not any(exclude_word in c2c_items_name for exclude_word in exclude_words):
                # 不符合“想要”，但也不包含“不想要”关键词，不保存到HTML
                log_item_to_html(c2c_items_name, show_price, matched=False)
                log_message(f"添加商品（不含排除关键词）: {c2c_items_name} - 价格: {show_price}", status="No")
            else:
                # 包含“不想要”关键词，不记录
                log_message(f"跳过商品（包含排除关键词）: {c2c_items_name}", status="No")

# 保存数据到HTML（仅保存符合条件的商品）
def save_to_html(c2c_items_id, c2c_items_name, show_price):
    with open("items_index.html", "a", encoding="utf-8") as file:
        file.write(
            f'<p><a href="https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId={c2c_items_id}">{c2c_items_name}</a></p>'
            f'<p>价格: {show_price}</p>'
        )

# 保存日志到日志HTML文件
def log_item_to_html(c2c_items_name, show_price, matched):
    color = "green" if matched else "red"
    with open("scraping_log.html", "a", encoding="utf-8") as file:
        file.write(
            f'<p style="color:{color};"><strong>{c2c_items_name}</strong> - 价格: {show_price}</p>'
        )

# 记录日志到GUI和日志HTML文件
def log_message(message, status=None):
    """
    记录日志信息。
    :param message: 日志内容
    :param status: 可选，"Yes"、"No"、"Error" 或 "Info"，用于前缀和日志显示
    """
    if status == "Error":
        prefix = "Error: "
    elif status == "Yes":
        prefix = "Yes: "
    elif status == "No":
        prefix = "No: "
    elif status == "Info":
        prefix = "Info: "
    else:
        prefix = ""

    full_message = f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {prefix}{message}\n"

    log_area.config(state=NORMAL)
    log_area.insert(END, full_message)
    log_area.yview(END)
    log_area.config(state=DISABLED)

# 执行抓取
def scrape():
    global next_id
    if not scraping_active:
        return  # 如果停止抓取，退出函数

    response_data = fetch_data()
    if response_data is None:
        return  # 如果请求失败，退出函数

    data = response_data.get("data", {})
    next_id = data.get("nextId")
    items = data.get("data", [])

    if items:
        process_items(items)
        # 生成1000到5000毫秒之间的随机延迟，避免被叔叔抓到
        random_delay = random.randint(1000, 5000)
        log_message(f"下一次抓取将在 {random_delay} 毫秒后进行。", status="Info")
        # 调度下一次抓取，使用随机抓取间隔
        root.after(random_delay, scrape)
    else:
        log_message("所有商品已抓取完毕。", status="Yes")
        messagebox.showinfo("完成", "所有商品已抓取完毕。")
        stop_scraping()

# 开始抓取
def start_scraping():
    global scraping_active, next_id
    scraping_active = True
    next_id = None  # 重置 next_id
    seen_c2c_items_ids.clear()
    initialize_html()
    initialize_log_html()
    log_message("开始抓取商品...", status="Yes")
    # 添加提醒信息到日志
    log_message("index索引链接需要先登录哔哩哔哩才能查看 / To check out index, you need to sign in bilibili", status="Info")
    # 生成初始随机延迟
    initial_delay = random.randint(1000, 5000)
    log_message(f"第一次抓取将在 {initial_delay} 毫秒后进行。", status="Info")
    root.after(initial_delay, scrape)
    start_button.config(text="暂停抓取")

# 停止抓取
def stop_scraping():
    global scraping_active
    scraping_active = False
    close_html()
    close_log_html()
    log_message("已暂停抓取。", status="No")
    start_button.config(text="开始抓取")

# 暂停或继续抓取
def toggle_scraping():
    if scraping_active:
        stop_scraping()
    else:
        start_scraping()

# 用户输入“想要”和“不想要”的关键字
def set_keywords():
    global i_want, exclude_words
    i_want = [keyword.strip() for keyword in want_entry.get().split(",") if keyword.strip()]
    exclude_words = [word.strip() for word in exclude_entry.get().split(",") if word.strip()]
    if not i_want and not exclude_words:
        messagebox.showinfo("提示", "请输入想要的或不想要的关键词！")
        return
    log_message(f"设置关键词 - 想要: {i_want}, 不想要: {exclude_words}", status="Yes")
    start_button.config(state=NORMAL)

# 自动打开Chrome浏览器，同时打开 items_index.html 和 www.bilibili.com
def open_browser():
    service = Service("C:/Users/10066/Downloads/chromedriver_win32/chromedriver.exe")  # 更新为您的chromedriver路径
    try:
        driver = webdriver.Chrome(service=service)
        html_path = os.path.abspath("items_index.html")
        # 打开 items_index.html
        driver.get(f"file:///{html_path}")
        # 打开 www.bilibili.com 在新标签页
        driver.execute_script("window.open('https://www.bilibili.com', '_blank');")
        log_message("已在浏览器中打开HTML文件和www.bilibili.com。", status="Yes")
    except Exception as e:
        log_message(f"无法打开浏览器: {e}", status="No")
        messagebox.showerror("错误", f"无法打开浏览器: {e}")

# GUI设置
root = Tk()
root.title("商品抓取")
root.geometry("800x700")

# 关键词输入区域
Label(root, text="想要的关键词 (用逗号分隔):").grid(row=0, column=0, padx=10, pady=10, sticky=E)
Label(root, text="不想要的关键词 (用逗号分隔):").grid(row=1, column=0, padx=10, pady=10, sticky=E)

want_entry = Entry(root, width=50)
want_entry.grid(row=0, column=1, padx=10, pady=10)
exclude_entry = Entry(root, width=50)
exclude_entry.grid(row=1, column=1, padx=10, pady=10)

set_button = Button(root, text="设置关键词", command=set_keywords)
set_button.grid(row=2, column=0, columnspan=2, pady=10)

# 控制按钮区域
start_button = Button(root, text="开始抓取", state=DISABLED, command=toggle_scraping)
start_button.grid(row=3, column=0, columnspan=2, pady=10)

open_button = Button(root, text="打开HTML", command=open_browser)
open_button.grid(row=4, column=0, columnspan=2, pady=10)

# 日志显示区域
log_area = scrolledtext.ScrolledText(root, width=100, height=30, state=DISABLED)
log_area.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

# 确保 "打开HTML" 按钮在有内容时可用
def update_open_button_state():
    if os.path.exists("items_index.html"):
        open_button.config(state=NORMAL)
    else:
        open_button.config(state=DISABLED)
    root.after(5000, update_open_button_state)  # 每5秒检查一次

# 初始化 "打开HTML" 按钮状态
open_button.config(state=DISABLED)
update_open_button_state()

# 运行 Tkinter 事件循环
root.mainloop()