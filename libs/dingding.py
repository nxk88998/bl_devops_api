import requests
import json

def dingtalk_msg(content):
    url = 'https://oapi.dingtalk.com/robot/send?access_token=1edfe66190be6584b388dc868cd78dce74f6f52700de2c8150bc504bdac40027'
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    data = {
            "msgtype": "text",
            "text": {
                "content": content
            }
        }
    res = requests.post(url=url, headers=headers, data=json.dumps(data))
    return res.text
if __name__ == "__main__":
    content = "发布通知：电商项目-前端应用，发布成功了！"
    print(dingtalk_msg(content))
