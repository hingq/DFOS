# 工具

本文档两层用途：**（一）** 产品工作里常用的方法与载体；**（二）** 情报流水线里判断「可指认的工具 / 产品」时的 **参考词表**（与 `context/deep_dive.md`、`processing` 的 `anchor_product` / `anchor_capability` 对齐）。下列 **AI 工具分类与示例名** 便于模型与编辑统一称呼，**非穷尽列表**，新工具以可核验的官方命名为准。

---

## 一、AI 工具分类清单（参考词表）

以下为 **主流 AI 产品形态** 分类，每类附 **常见可指认产品名**（用于标题、实体提取与深挖锚点）。**同类内不限于所列**，收录原则是：有稳定品牌名、有明确入口（官网/应用/插件市场）、能力边界相对可描述。

### 1. 聊天机器人 / 通用助手

| 常见产品或系列（示例） |
|------------------------|
| ChatGPT（OpenAI）、Claude（Anthropic）、Microsoft Copilot、Google Gemini、Perplexity、xAI Grok、DeepSeek、Meta AI、Notion AI、Ajelix 等 |

**典型能力关键词**：对话、检索、多模态、办公集成、长文本、代码辅助（与「编程助手」有交叉时，以**主场景**归类）。

### 2. 写作与文本

| 常见产品或系列（示例） |
|------------------------|
| Jasper、Scalenut、Writesonic、Wordtune、Copy.ai、Grammarly、Rytr 等 |

**典型能力关键词**：营销文案、SEO、润色、模板化写作、语法与风格建议。

### 3. 编程助手 / AI 原生开发

| 常见产品或系列（示例） |
|------------------------|
| GitHub Copilot、Cursor、Codeium、Windsurf、Tabnine（及同类 IDE 内助手）等 |

**典型能力关键词**：代码补全、多文件编辑、Agent 式任务、调试、仓库级上下文。

### 4. 设计、图像与品牌视觉

| 常见产品或系列（示例） |
|------------------------|
| Midjourney、DALL·E 3、Canva（Magic Design 等）、Adobe Firefly、Stable Diffusion、Leonardo.ai、Runway（图像/视效相关）、Uizard、Khroma、Looka、Figma（含 AI 相关能力）、Lovart、Liblib 等 |

**典型能力关键词**：文生图、模板与品牌套件、UI/原型、配色、Logo、设计系统相关自动化。

### 5. 视频生成与数字人

| 常见产品或系列（示例） |
|------------------------|
| Sora、Runway Gen-2、Pika、Synthesia、HeyGen、D-ID、Colossyan、DeepBrain AI、InVideo AI、Fliki 等 |

**典型能力关键词**：文生视频、数字人、口型同步、模板成片、营销/培训视频。

### 6. 音频、语音与其他效率

| 常见产品或系列（示例） |
|------------------------|
| **语音/TTS**：ElevenLabs、Descript、Murf.ai 等 |
| **数据**：Julius AI、Akkio 等 |
| **自动化/会议**：Zapier AI、Otter.ai 等 |

**说明**：与「设计+AI」主线弱相关条目可进简报，但是否进入 **值得深挖** 仍须满足 `deep_dive.md` 与 processing 规则（工具/宿主新功能 + AI 强相关 + 官宣等）。

### 7. 套件、平台与「宿主产品」

许多能力以 **大产品内子能力** 发布（如 Claude 内 Design 模式、Figma 内某 AI 功能）。此时 **锚点** 应写清：**宿主**（`anchor_product`）+ **能力名**（`anchor_capability`），避免只写泛称「AI 设计」。

---

## 二、与流水线对齐的用法（编辑提示）

- **可指认**：读者能回答「我用 **X** 来做什么」；`anchor_product` 优先与上表或官方命名一致（大小写/中英文品牌以常见中文环境为准时可统一为一种写法）。
- **不可把「能力描述」当工具名**：如仅「用 AI 做界面」而无具体产品，不单独作为深挖锚点。
- **深挖与长文**：入选「值得深挖」及后续单篇长文的主题，应能从上表或同等层级的 **具体产品/能力** 落点；细则见 `context/deep_dive.md`。

---

## 三、经典产品工作方法（原 tool.md 骨架）

以下保留作 **产品分析/调研** 时的方法提醒，与 AI 词表互不冲突。

### 产品

- 行为数据

### 用户画像

- 用户的定性和定量调研

### 体验设计

- 用户旅程地图

### 商业认知

- 精益画布
- 商业画布
- SWOT
