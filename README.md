# AI Frontier Email Briefing

自动生成并发送两类中文邮件：

1. **每日 AI 前沿简报**：每天北京时间 08:00。
2. **每周 AI 与金属计算材料学前沿周报**：每周日北京时间 20:00。

收件邮箱默认建议配置为：

```text
wtm3551017485@qq.com
```

## 工作原理

```text
GitHub Actions 定时触发
        ↓
Python 脚本读取 prompt
        ↓
OpenAI Responses API + Web Search 生成简报
        ↓
SMTP 发送到邮箱
```

GitHub Actions 的定时任务使用 `on.schedule` 和 POSIX cron；GitHub 文档说明定时 workflow 会在默认分支最新 commit 上运行，且 cron 默认按 UTC 执行。OpenAI Responses API 支持通过工具调用 web search 获取实时网络信息。  

## 文件结构

```text
.github/workflows/
  daily-ai-briefing.yml
  weekly-ai-materials-report.yml

scripts/
  generate_and_send.py

prompts/
  daily.md
  weekly.md

docs/
  qq-mail-setup.md

requirements.txt
.env.example
```

## 时间设置

| 任务 | 北京时间 | UTC cron |
|---|---:|---:|
| 每日 AI 简报 | 每天 08:00 | `0 0 * * *` |
| 每周 AI + 材料周报 | 周日 20:00 | `0 12 * * 0` |

## GitHub Secrets 配置

进入你的仓库：

```text
Settings → Secrets and variables → Actions → New repository secret
```

添加这些 Secrets：

| Secret 名称 | 说明 |
|---|---|
| `OPENAI_API_KEY` | OpenAI API Key |
| `OPENAI_MODEL` | 模型名，例如 `gpt-4.1-mini` |
| `SMTP_HOST` | QQ 邮箱填 `smtp.qq.com` |
| `SMTP_PORT` | QQ 邮箱 SSL 一般填 `465` |
| `SMTP_SSL` | `true` |
| `SMTP_USER` | 发件邮箱，例如 `wtm3551017485@qq.com` |
| `SMTP_PASSWORD` | QQ 邮箱授权码，不是登录密码 |
| `MAIL_FROM` | 发件邮箱 |
| `MAIL_TO` | 收件邮箱 |

## 手动测试

上传到 GitHub 后：

1. 打开仓库的 **Actions**。
2. 选择 `Daily AI Frontier Briefing`。
3. 点击 **Run workflow**。
4. 等运行完成后检查 QQ 邮箱。
5. 再测试 `Weekly AI and Computational Materials Report`。

## 本地测试

复制 `.env.example` 为 `.env`，填入真实值后：

```bash
pip install -r requirements.txt
python scripts/generate_and_send.py --kind daily
python scripts/generate_and_send.py --kind weekly
```

## 安全提醒

- 不要把 API Key、QQ 授权码、邮箱密码写进代码。
- 不要上传 `.env`。
- QQ 邮箱 SMTP 需要授权码，不要使用 QQ 登录密码。
- 自动简报仅用于学习和跟踪前沿，不应作为科研或投资决策的唯一依据。

## 后续可扩展

- 增加 arXiv / Semantic Scholar 专项检索。
- 增加只关注材料方向的月报。
- 增加 Markdown 存档，把每次简报保存到 `reports/`。
- 增加失败重试和运行日志。
