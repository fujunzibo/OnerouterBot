# WebApp 部署指南

## 升级说明

本升级为机器人添加了 WebApp 模式支持，用户可以在 Telegram 内部直接打开精美的卡片商城。

## 部署步骤

### 1. 安装 WebApp 依赖

```bash
cd webapp
npm install
```

### 2. 构建 WebApp

```bash
npm run build
```

构建产物会生成在 `webapp/dist/` 目录。

### 3. 更新 Nginx 配置

确保 Nginx 配置正确转发请求：

```nginx
location /webapp {
    proxy_pass http://127.0.0.1:8080;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

location /api {
    proxy_pass http://127.0.0.1:8080;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### 4. 更新环境变量

确保 `.env` 文件包含：

```env
BOT_TOKEN=your_bot_token
WEBHOOK_HOST=https://yourdomain.com
WEBHOOK_PORT=8080
WEBHOOK_PATH=/webhook
WEBHOOK_SECRET=your_secret_token
```

### 5. 重启服务

```bash
sudo systemctl stop onerouterbot
cd /home/epay/bot
npm run build --prefix webapp
sudo systemctl start onerouterbot
```

## 功能说明

### 新命令

| 命令 | 功能 |
|------|------|
| `/start` | 欢迎语，显示库存和 WebApp 按钮 |
| `/help` | 帮助信息，售后保障说明 |
| `/status` | 查看已购卡片订单状态 |

### WebApp 特性

- 🛒 **购物车功能**：支持添加多个商品
- 💳 **多种支付方式**：Telegram Wallet Pay、Crypto、信用卡
- 📱 **响应式设计**：支持移动端和桌面端
- 🎨 **精美界面**：渐变背景、卡片式布局
- ⚡ **即时发货**：支付成功后立即显示卡片密匙

### 菜单按钮

机器人启动后会自动设置菜单按钮（Menu Button），用户可以通过底部菜单直接打开商城。

## 支付集成

### Telegram Wallet Pay

WebApp 已集成 Telegram Wallet Pay 支持，用户可以使用 Telegram 钱包余额支付。

### Crypto (USDT-TRC20)

如需集成加密货币支付，需要：
1. 部署 TRC20 收款地址监控服务
2. 添加自动充值回调 API
3. 在支付成功后标记订单为已支付

### Credit/Debit Card

如需集成信用卡支付，需要：
1. 在 BotFather 中配置支付提供商
2. 设置 PAYMENT_PROVIDER_TOKEN 环境变量

## 数据库更新

升级后数据库会自动创建必要的表，无需手动操作。

## 测试

启动后测试流程：

1. 发送 `/start` 命令，确认显示 WebApp 按钮
2. 点击 "🛒 Open Store" 打开 WebApp
3. 浏览商品，添加到购物车
4. 完成支付流程
5. 检查订单状态 `/status`

## 故障排除

### WebApp 无法打开

1. 检查 `WEBHOOK_HOST` 是否正确设置
2. 确保 Nginx 配置正确转发 `/webapp` 路径
3. 检查 SSL 证书是否有效

### 支付失败

1. 检查支付提供商配置
2. 查看日志：`journalctl -u onerouterbot -f`
3. 确认库存充足

### 卡片显示为 0

1. 检查数据库连接
2. 确认数据已正确导入
3. 运行 `/restock` 导入卡片数据