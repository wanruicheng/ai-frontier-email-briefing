# QQ 邮箱 SMTP 设置说明

这个项目使用 SMTP 发信。QQ 邮箱通常需要开启 SMTP 服务，并使用“授权码”，不是 QQ 登录密码。

## 需要准备

在 QQ 邮箱网页端：

1. 进入设置。
2. 找到 POP3/SMTP/IMAP 相关服务。
3. 开启 SMTP 或 POP3/SMTP 服务。
4. 生成授权码。
5. 把授权码填入 GitHub Secrets 的 `SMTP_PASSWORD`。

## 推荐 Secrets

| Name | Value |
|---|---|
| `SMTP_HOST` | `smtp.qq.com` |
| `SMTP_PORT` | `465` |
| `SMTP_SSL` | `true` |
| `SMTP_USER` | `wtm3551017485@qq.com` |
| `SMTP_PASSWORD` | QQ 邮箱授权码，不是登录密码 |
| `MAIL_FROM` | `wtm3551017485@qq.com` |
| `MAIL_TO` | `wtm3551017485@qq.com` |

## 安全提醒

- 不要把授权码写进代码。
- 不要把 `.env` 上传到 GitHub。
- 如果授权码泄露，立刻在 QQ 邮箱里关闭/重新生成。
