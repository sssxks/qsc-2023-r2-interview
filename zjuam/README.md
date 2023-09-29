# ZJUSession 实现文档

## 简介
ZJUSession 是一个简单的 Python class，实现了根据用户名和密码自动登录[浙江大学统一身份认证](https://zjuam.zju.edu.cn/cas/login)并使用依赖于这个认证系统的 Web 服务，包括[appservice](http://appservice.zju.edu.cn)、[教务网](http://zdbk.zju.edu.cn/jwglxt/xtgl/login_ssologin.html)、[学在浙大](https://courses.zju.edu.cn/user/index)等。

## 项目结构
```
archive/ 记录了艰辛的探索历程，包括对 RSA 库的失败移植
rsaapi/ 一个基于 express.js 的 NodeJS API 服务端，用于 RSA 加密
ZJUSession.ipynb 方便玩耍的笔记本文件，因为笔记本可以保证每一步执行都是对的
zjusession.py 笔记本导出的代码，可以 import 到未来开发的项目里
```

## 使用方式
先运行
```
cd ./rsaapi
npm init -y
node security.js
```
再打开 `ZJUSession.ipynb` 玩，或者把 zjusession.py 拷贝到你的项目里面。

## 探索路径
先用开发者工具看了一下发的请求是什么，因为readme里面已经剧透了发的请求是post，然后表单结构也告诉了，但是花了很久没有在network里找到，然后猜可以筛选method为post，就找到了，这是遇到的第一个难点，然后get pub key也就顺利找到了
第二个难点是rsa，首先是找了一波python的rsa库，然后发现他那个security.js的实现是不一样的，所以又想把security.js的实现移植到python里面，可惜发现有亿点点难度，还让chatGpt帮忙，然而写的代码都不能用，最后只能用express.js开了一个API服务器，原模原样跑那个js文件，让python去调用
第三个难点是什么都弄完了，发现就是登不上去，然后反复的尝试各种各样的header, cookies的设置，出来了各种各样千奇百怪的错误，最后当猴子，改一下请求参数运行一下，但是还是error decoding flow execution，最后发现get pub key的时候忘记把/cas/login/得到的cookies传给他了，改了之后还不知道登录上去了，然后仔细的看了一遍response，然后才发现登录上去了

登录上去之后就比较简单了，首先把登录过程和访问具体的网站的过程解耦，然后把代码整理了一遍，用requests库的session类很好的把这个cookies保存给他重写了，然后尝试了appservice之外的网站，发现都可以用

主要难点：
- 定位登录请求
- 移植浏览器端代码
- 填写请求参数

体会就是实现了一个人肉浏览器，下次绝对不干这种活了，直接selenium

## 登录学在浙大时发生了什么
重定向路径:
```
https://courses.zju.edu.cn/user/index
https://identity.zju.edu.cn/auth/realms/zju/protocol/cas/login?service=https%3A//courses.zju.edu.cn/user/index&locale=zh_CN&ts=1695969071.105981
https://identity.zju.edu.cn/auth/realms/zju/broker/cas-client/login?session_code=-1ptb7gv9NqNZQw6ST55O-uJ8YpceB4mI8ujiw6Ibfk&client_id=TronClass&tab_id=GlT-2s5R4tE
https://zjuam.zju.edu.cn/cas/login?service=https%3A%2F%2Fidentity.zju.edu.cn%2Fauth%2Frealms%2Fzju%2Fbroker%2Fcas-client%2Fendpoint?state%3DcYc4Cw_stXlFfM7ZYVeo-KFMpPTr9sg0w31uiRxRsis.GlT-2s5R4tE.TronClass
https://identity.zju.edu.cn/auth/realms/zju/broker/cas-client/endpoint?state=cYc4Cw_stXlFfM7ZYVeo-KFMpPTr9sg0w31uiRxRsis.GlT-2s5R4tE.TronClass&ticket=ST-32652361-DlZn7FOPBUKW0oiCwuA2-zju.edu.cn
https://courses.zju.edu.cn/user/index?ticket=ST-123686fa-bf36-497c-ae4f-b682ee42a1e6.6f4fdd86-4aa6-417b-93f5-e8dfbeecfa3b.818132fc-7f3a-49de-b1dd-3fe43bff7371
```
跳到zjuam时如果登陆了，会直接跳回service里面的地址，同时附加一个ticket参数，然后一路跳回去
如果访问zjuam时不加service，会访问protalredirect，然后无限重定向，因此需要禁止requests自动重定向

## Q&A

1. 你觉得解决这个任务的过程有意思吗？
挺有意思，非常有成就感，因为浙大登录是写各种自动脚本的基础

2. 你在网上找到了哪些资料供你学习？你觉得去哪里/用什么方式搜索可以比较有效的获得自己想要的资料？
时代变了，问chatGPT，gpt-4和bing chat覆盖绝大部分需求，当然LLM不能帮你把活都干完，一些文档还是自己得看的

3. 在过程中，你遇到最大的困难是什么？你是怎么解决的？
- 定位登录请求
- 移植浏览器端代码
- 填写请求参数
都很困难〒▽〒

4. 完成任务之后，再回去阅读你写下的代码和文档，有没有看不懂的地方？如果再过一年，你觉得那时你还可以看懂你的代码吗？
100行不到的东西不可能看不懂，
而且文档和注释会被我的英语能力限制

5. 其他想说的想法或者建议。
今天早上真的做着做着就想哭(。・ω・。)
特别是连怎么出错都没有头绪的时候(≧﹏ ≦)