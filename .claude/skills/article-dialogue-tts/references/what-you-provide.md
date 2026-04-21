# 你需要提供什么（给助手或自己配置）

以下内容**不要发密钥原文到聊天或提交到 Git**；只在本地终端或 CI Secret 中配置。

## 必配（科大讯飞控制台）

在 [讯飞开放平台](https://www.xfyun.cn/) 创建应用并开通 **在线语音合成（流式版）** 后，记录：

| 环境变量 | 含义 |
|----------|------|
| `XFYUN_APP_ID` | 应用 AppID |
| `XFYUN_API_KEY` | API Key |
| `XFYUN_API_SECRET` | API Secret |

## 选配（发音人）

在控制台 **发音人授权管理** 中为应用添加可用的 **vcn**（男女各一），然后设置：

| 环境变量 | 含义 | 默认（示例，以控制台为准） |
|----------|------|---------------------------|
| `XFYUN_VCN_Q` | **Q**（男声） | `aisjiuxu` |
| `XFYUN_VCN_A` | **A**（女声） | `xiaoyan` |

若报 `11200` 等授权错误，通常是 **vcn 未添加/未试用/过期**，请在控制台核对。

## 日期

| 环境变量 / 参数 | 含义 |
|------------------|------|
| `BRIEFING_DATE` | `YYYY-MM-DD`，与文章文件名日期一致 |
| `python -m tools.article_tts --date YYYY-MM-DD` | 同上 |

## 给助手时建议怎么说

- 「已在本机 export 好 `XFYUN_*`，请从项目根跑 `python -m tools.article_tts --date …`」
- 或：「控制台里 Q 用 vcn `xxx`，A 用 `yyy`」——**只发 vcn 名称，不要发 Secret**
