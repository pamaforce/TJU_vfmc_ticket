import json
from urllib.parse import quote, urlencode
import requests
import time

# 设置变量
dateadd = 1 # 表示从今天开始往后推 dateadd 天的日子
TimePeriod = 1 # 0表示上午 1表示下午 2表示晚上
VenueNo = '001' # 001表示卫津路体育馆
FieldTypeNo = '001' # 001表示羽毛球场

# 设置 Cookie 和 headers，这里需要换成你自己的 Cookie，参考 https://rapr5wizcgi.feishu.cn/wiki/HmXnwDwt0iBU7xkWfSRc8aNsnUb
cookies = {
    'WXOpenId': '换成你自己的',
    'LoginSource': '0',
    'JWTUserToken': '这里也是',
    'UserId': '还有这里',
    'LoginType': '0'
}

headers = {
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Referer': f'http://vfmc.tju.edu.cn/Views/Field/FieldOrder.html?VenueNo={VenueNo}&FieldTypeNo={FieldTypeNo}&FieldType=Field',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 12; Lenovo L79031 Build/SKQ1.220119.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/126.0.6478.71 Mobile Safari/537.36 XWEB/1260037 MMWEBSDK/20240404 MMWEBID/4282 MicroMessenger/8.0.49.2600(0x2800315A) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64',
    'X-Requested-With': 'XMLHttpRequest'
}

def get_available_fields(dateadd, TimePeriod, VenueNo, FieldTypeNo):
    url = f'http://vfmc.tju.edu.cn/Field/GetVenueStateNew?dateadd={dateadd}&TimePeriod={TimePeriod}&VenueNo={VenueNo}&FieldTypeNo={FieldTypeNo}&_={int(time.time() * 1000)}'
    response = requests.get(url, headers=headers, cookies=cookies)
    response_json = response.json()
    
    if response_json.get("errorcode") == 0:
        try:
            resultdata = json.loads(response_json.get("resultdata", "[]"))
            available_fields = [item for item in resultdata if item["FieldState"] == "0"]
            print(f"获取场馆状态成功，所选条件共有 {len(available_fields)} 个可预订的场地")
            return available_fields
        except json.JSONDecodeError as e:
            print(f"解析 resultdata 时出错: {e}")
            return []
    else:
        print(f"获取场馆状态请求失败：错误代码 {response_json.get('errorcode')}, 错误信息：{response_json.get('message')}")
        return []

def select_field(available_fields):
    if not available_fields:
        print("没有可预订的场地")
        return None
    
    # 这里只选择第一个可预订的场地，你可以根据需要修改选择逻辑
    selected_field = available_fields[0]
    print(f"选择了场地 {selected_field['FieldName']}, 时间段为 {selected_field['BeginTime']} - {selected_field['EndTime']}")
    return selected_field

def book_field(selected_field, dateadd):
    if not selected_field:
        return
    
    checkdata = [
        {
            "FieldNo": selected_field["FieldNo"],
            "FieldTypeNo": selected_field["FieldTypeNo"],
            "FieldName": selected_field["FieldName"],
            "BeginTime": selected_field["BeginTime"],
            "Endtime": selected_field["EndTime"],
            "Price": selected_field["FinalPrice"],
            "DateAdd": dateadd
        }
    ]
    
    query_params = {
        "checkdata": json.dumps(checkdata, ensure_ascii=False),
        "VenueNo": VenueNo,
        "OrderType": "Field"
    }
    
    # 拼装请求体
    payload_items = [f"{quote(key)}={quote(value)}" for key, value in query_params.items()]
    payload = "&".join(payload_items)

    url = "http://vfmc.tju.edu.cn/Field/OrderField"
    
    # 发送预定请求
    headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
    response = requests.post(url, headers=headers,cookies=cookies, data=payload)
    response_json = response.json()
    print(response_json)
    if response_json.get("errorcode") == 0 and response_json.get("message") == "":
        print("预定请求成功，请前往微信网页查看订单详情")
    else:
        print(f"预定请求失败：错误代码 {response_json.get('errorcode')}, 错误信息：{response_json.get('message')}")

# 主程序
if __name__ == "__main__":
    available_fields = get_available_fields(dateadd, TimePeriod, VenueNo, FieldTypeNo)
    selected_field = select_field(available_fields)
    book_field(selected_field, dateadd)