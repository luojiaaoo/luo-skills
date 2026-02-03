---
name: we-mp-rss-export-markdown
description: 本技能用于导出we-mp-rss平台中订阅的微信公众号文章，以markdown文件导出，当用户需要获取we-mp-rss平台中订阅的微信公众号文章时触发
---

# we-mp-rss订阅微信公众号markdown文件导出

通过Python访问已搭建的we-mp-rss平台，平台上订阅的文章以markdown格式导出

## 开始

首次使用前请先安装依赖项：

```bash
python -m pip install drissionpage==4.1.0.19b1
python -m pip install httpx==0.28.1
python -m pip install loguru==0.7.3
python -m pip install pathvalidate==3.3.1
python -m pip install python-dateutil==2.9.0.post0
python -m pip install rss-parser==2.1.1
python -m pip install tenacity==9.1.2
python -m pip install markitdown[pdf]==0.1.4
```

## 脚本

### scripts/export_markdown.py - 保存订阅微信公众号文章为markdown

这个工具脚本不允许并发调用，如需多次调用请串行执行

如果用户没有说明we-mp-rss平台的RSS源url，需要主动询问用户URL是多少

```bash
usage: scripts/export_markdown.py [-h] -u URL -d DATE -o OUTPUT

保存订阅微信公众号文章为markdown

options:
  -h, --help            show this help message and exit
  -u URL, --url URL     we-mp-rss平台的URL地址
  -d DATE, --date DATE  指定文章的发布日期，比如20260203
  -o OUTPUT, --output OUTPUT
                        markdown输出文件路径
```

## 要点

- markdown文件都会放到OUTPUT指定的路径下
- 如果用户指定的OUTPUT路径为相对路径，以项目路径为起始路径