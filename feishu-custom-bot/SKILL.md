---
name: feishu-custom-bot
description: 本技能用于向飞书自定义机器人Webhook地址发送markdown格式卡片消息，当用户需要通过自定义机器人发送消息时触发 
---

# 飞书自定义机器人发送消息

通过用户提供的自定义机器人Webhook地址发送markdown格式卡片消息

## 开始

首次使用前请先安装依赖项：

```bash
python -m pip install request
```

## 卡片消息json格式

```json
{
  "msg_type": "interactive",
  "card": {
    "schema": "2.0",
    "config": {
      "update_multi": true,
      "style": {
        "text_size": {
          "normal_v2": {
            "default": "normal",
            "pc": "normal",
            "mobile": "heading"
          }
        }
      }
    },
    "body": {
      "direction": "vertical",
      "padding": "12px 12px 12px 12px",
      "elements": [
        {
          "tag": "markdown",
          "content": "【此处是markdown内容】",
          "text_align": "left",
          "text_size": "normal_v2",
          "margin": "0px 0px 0px 0px"
        },
      ]
    },
    "header": {
      "title": {
        "tag": "plain_text",
        "content": "【此处是标题】"
      },
      "subtitle": {
        "tag": "plain_text",
        "content": ""
      },
      "template": "blue",
      "padding": "12px 12px 12px 12px"
    }
  }
}
```

# 脚本

### scripts/send_message.py - 发送飞书自定义机器人消息

如果用户没有说明飞书自定义机器人Webhook地址，需要主动询问用户地址是多少

```bash
usage: send_message.py [-h] -u WEBHOOK_URL -f FILE

Send feishu custom boot message

options:
  -h, --help            show this help message and exit
  -u WEBHOOK_URL, --webhook_url WEBHOOK_URL
                        URL of custom bot webhook
  -f FILE, --file FILE  Text file for saving json of message
```