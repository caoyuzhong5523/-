import requests
import json
import hashlib
import random
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

APP_ID = "%%%" # <-- 请替换为真实AppID

API_KEY = "%%%"   # <-- 请替换为真实API_KEY

# 百度翻译 API 的通用翻译接口 URL
API_URL = "https://fanyi-api.baidu.com/api/trans/vip/translate"

# 语言代码与中文名称的映射表
# 键是API使用的语言代码，值是界面显示的中文名称
LANG_MAP = {
    'auto': '自动检测',
    'zh': '中文',
    'en': '英语',
    'jp': '日语',
    'kor': '韩语',
    'fra': '法语',
    'de': '德语',
    'ru': '俄语',
    'spa': '西班牙语',
    'pt': '葡萄牙语',
    'it': '意大利语',
    'vie': '越南语',
    'th': '泰语',
    'ara': '阿拉伯语',
    'hi': '印地语',
    'yue': '粤语',
    'wyw': '文言文',
    'zh_cht': '繁体中文',
    'est': '爱沙尼亚语',
    'bul': '保加利亚语',
    'pl': '波兰语',
    'dan': '丹麦语',
    'fin': '芬兰语',
    'nl': '荷兰语',
    'cs': '捷克语',
    'swe': '瑞典语',
    'hu': '匈牙利语',
    'el': '希腊语',
    'slo': '斯洛文尼亚语',
    'cht': '繁体中文',
    'he': '希伯来语'

}

# 创建一个反向映射表，用于将中文名称转换回语言代码
REVERSE_LANG_MAP = {v: k for k, v in LANG_MAP.items()}

# 用于Combobox显示的语言名称列表
DISPLAY_LANGUAGES = list(LANG_MAP.values())

# 翻译逻辑函数
def generate_sign(query, salt):
    """
    生成百度翻译 API 请求的签名 (Sign)。
    MD5(AppID + query + salt + 密钥)
    """
    sign_str = APP_ID + query + str(salt) + API_KEY
    m = hashlib.md5()
    m.update(sign_str.encode('utf-8'))
    return m.hexdigest()

def translate_text(text, from_lang_code, to_lang_code):
    """
    调用百度翻译 API 进行文本翻译。
    :param text: 待翻译的文本
    :param from_lang_code: 源语言代码，如 'auto', 'zh', 'en'
    :param to_lang_code: 目标语言代码，如 'en', 'zh'
    :return: 翻译后的文本，或错误信息字符串
    """
    if APP_ID == "%%%" or API_KEY == "%%%":
        return "错误：请在代码中配置您的真实 AppID 和 密钥！"

    salt = random.randint(32768, 65536)
    sign = generate_sign(text, salt)

    params = {
        'q': text,
        'from': from_lang_code,
        'to': to_lang_code,
        'appid': APP_ID,
        'salt': salt,
        'sign': sign
    }

    try:
        response = requests.get(API_URL, params=params, timeout=5) # 增加超时设置，避免长时间等待
        response.raise_for_status() # 检查 HTTP 响应状态码 (2xx表示成功，否则抛出异常)

        result = response.json()

        if 'trans_result' in result and len(result['trans_result']) > 0:
            return result['trans_result'][0]['dst']
        elif 'error_code' in result:
            error_code = result['error_code']
            error_msg = result.get('error_msg', '未知错误')
            # 常见错误码提示
            if error_code == '52003':
                return "翻译失败：未授权用户（AppID 或 密钥不正确）。"
            elif error_code == '54000':
                return "翻译失败：签名错误（请检查AppID、密钥或代码中的签名算法）。"
            elif error_code == '54001':
                return "翻译失败：请求频率过高，请稍后重试。"
            elif error_code == '52001':
                return "翻译失败：请求超时，请检查网络。"
            elif error_code == '58002':
                return "翻译失败：服务当前不可用，请稍后重试。"
            elif error_code == '90100':
                return "翻译失败：API服务未开通或余额不足。"
            else:
                return f"API 错误代码: {error_code}, 错误信息: {error_msg}"
        else:
            return f"未知 API 响应结构: {json.dumps(result, ensure_ascii=False, indent=2)}"

    except requests.exceptions.ConnectionError:
        return "网络连接错误，请检查您的网络连接。"
    except requests.exceptions.Timeout:
        return "请求超时，API 服务器响应缓慢或网络不稳定。"
    except requests.exceptions.RequestException as e:
        return f"请求失败: {e}"
    except json.JSONDecodeError:
        return "API 返回的数据不是有效的 JSON 格式。"
    except Exception as e:
        return f"发生未预期错误: {e}"

# GUI 界面部分
def on_translate_button_click():
    """
    当翻译按钮被点击时调用的函数。
    """
    input_text = input_text_widget.get("1.0", tk.END).strip() # 获取文本框所有内容并去除首尾空白

    if not input_text:
        messagebox.showwarning("输入错误", "请输入需要翻译的文本！")
        return

    # 获取用户选择的语言名称（如“中文”，“英语”）
    from_lang_display = from_lang_var.get()
    to_lang_display = to_lang_var.get()

    if not from_lang_display or not to_lang_display:
        messagebox.showwarning("语言选择错误", "请选择源语言和目标语言！")
        return

    # 将中文名称转换回API所需的语言代码
    from_lang_code = REVERSE_LANG_MAP.get(from_lang_display, 'auto') # 如果找不到，默认'auto'
    to_lang_code = REVERSE_LANG_MAP.get(to_lang_display, 'zh')     # 如果找不到，默认'zh'

    # 清空之前的翻译结果，并显示“翻译中...”
    result_text_widget.config(state=tk.NORMAL) # 允许修改
    result_text_widget.delete("1.0", tk.END)
    result_text_widget.insert(tk.END, "翻译中，请稍候...")
    result_text_widget.config(state=tk.DISABLED) # 禁用修改
    root.update_idletasks() # 强制Tkinter更新界面，显示“翻译中...”

    # 调用翻译函数
    translated_result = translate_text(input_text, from_lang_code, to_lang_code)

    # 显示翻译结果
    result_text_widget.config(state=tk.NORMAL) # 允许修改
    result_text_widget.delete("1.0", tk.END)   # 清空旧内容
    result_text_widget.insert(tk.END, translated_result) # 无论成功失败，都显示返回的结果
    result_text_widget.config(state=tk.DISABLED) # 再次禁用修改


# 主窗口设置
if __name__ == "__main__":
    root = tk.Tk()
    root.title("智能语言翻译器 - powered by AI") # 窗口标题
    root.geometry("600x600") # 设置窗口初始大小，可以根据需要调整
    root.resizable(False, False) # 不允许用户改变窗口大小，保持界面布局稳定
    root.configure(bg='#f0f0f0') # 设置背景色

    # 定义颜色和字体
    BG_COLOR = '#f0f0f0'
    PANEL_BG = '#ffffff'
    BUTTON_COLOR = '#4CAF50' # 绿色
    BUTTON_ACTIVE_COLOR = '#45a049'
    TEXT_COLOR = '#333333'
    LABEL_COLOR = '#555555'
    FONT_FAMILY = 'Microsoft YaHei UI' # 尝试使用常见的中文字体
    FONT_SIZE_LABEL = 10
    FONT_SIZE_TEXT = 12
    FONT_SIZE_BUTTON = 12

    # 顶部标题
    title_label = tk.Label(root, text="AI智能语言翻译器", font=(FONT_FAMILY, 18, 'bold'), bg=BG_COLOR, fg=LABEL_COLOR)
    title_label.pack(pady=15)

    # 输入框区域
    input_frame = tk.Frame(root, bg=PANEL_BG, padx=10, pady=10, bd=2, relief=tk.GROOVE)
    input_frame.pack(pady=10, padx=20, fill=tk.X)

    input_label = tk.Label(input_frame, text="输入文本:", font=(FONT_FAMILY, FONT_SIZE_LABEL, 'bold'), bg=PANEL_BG, fg=LABEL_COLOR)
    input_label.pack(anchor='w', pady=5)

    input_text_widget = tk.Text(input_frame, height=6, width=60, font=(FONT_FAMILY, FONT_SIZE_TEXT), bd=1, relief=tk.SOLID, wrap=tk.WORD)
    input_text_widget.pack(fill=tk.BOTH, expand=True)

    # 语言选择区域
    lang_frame = tk.Frame(root, bg=BG_COLOR)
    lang_frame.pack(pady=10)

    from_lang_label = tk.Label(lang_frame, text="源语言:", font=(FONT_FAMILY, FONT_SIZE_LABEL), bg=BG_COLOR, fg=LABEL_COLOR)
    from_lang_label.pack(side=tk.LEFT, padx=5)
    from_lang_var = tk.StringVar(value=LANG_MAP['auto']) # 默认显示“自动检测”
    from_lang_menu = ttk.Combobox(lang_frame, textvariable=from_lang_var, values=DISPLAY_LANGUAGES, state="readonly", font=(FONT_FAMILY, FONT_SIZE_TEXT))
    from_lang_menu.pack(side=tk.LEFT, padx=5)
    from_lang_menu.set(LANG_MAP['auto'])

    arrow_label = tk.Label(lang_frame, text="→", font=(FONT_FAMILY, FONT_SIZE_LABEL + 4, 'bold'), bg=BG_COLOR, fg=LABEL_COLOR)
    arrow_label.pack(side=tk.LEFT, padx=10)

    to_lang_label = tk.Label(lang_frame, text="目标语言:", font=(FONT_FAMILY, FONT_SIZE_LABEL), bg=BG_COLOR, fg=LABEL_COLOR)
    to_lang_label.pack(side=tk.LEFT, padx=5)
    to_lang_var = tk.StringVar(value=LANG_MAP['zh']) # 默认显示“中文”
    to_lang_menu = ttk.Combobox(lang_frame, textvariable=to_lang_var, values=DISPLAY_LANGUAGES, state="readonly", font=(FONT_FAMILY, FONT_SIZE_TEXT))
    to_lang_menu.pack(side=tk.LEFT, padx=5)
    to_lang_menu.set(LANG_MAP['zh'])


    # 翻译按钮
    translate_button = tk.Button(root, text="翻译", command=on_translate_button_click,
                                 font=(FONT_FAMILY, FONT_SIZE_BUTTON, 'bold'),
                                 bg=BUTTON_COLOR, fg="white",
                                 activebackground=BUTTON_ACTIVE_COLOR,
                                 activeforeground="white",
                                 relief=tk.RAISED, bd=3, cursor="hand2")
    translate_button.pack(pady=15)

    # 结果显示区域
    result_frame = tk.Frame(root, bg=PANEL_BG, padx=10, pady=10, bd=2, relief=tk.GROOVE)
    result_frame.pack(pady=10, padx=20, fill=tk.X)

    result_label = tk.Label(result_frame, text="翻译结果:", font=(FONT_FAMILY, FONT_SIZE_LABEL, 'bold'), bg=PANEL_BG, fg=LABEL_COLOR)
    result_label.pack(anchor='w', pady=5)

    result_text_widget = tk.Text(result_frame, height=6, width=60, font=(FONT_FAMILY, FONT_SIZE_TEXT), bd=1, relief=tk.SOLID, wrap=tk.WORD)
    result_text_widget.pack(fill=tk.BOTH, expand=True)
    result_text_widget.config(state=tk.DISABLED)

    # 启动 GUI 事件循环
    root.mainloop()