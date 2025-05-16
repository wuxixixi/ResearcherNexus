# ResearcherNexus 部署指南

本文档提供了 ResearcherNexus 系统的详细部署说明，适用于支持 50 人同时使用的服务器环境。

## 系统要求

### 硬件要求
- **CPU**: 最低 8 核，建议 16-32 核
- **内存**: 最低 16GB，建议 32GB
- **存储**: 最低 100GB SSD
- **网络带宽**: 最低 100Mbps，建议 1Gbps

### 软件要求
- **操作系统**: Ubuntu 20.04/22.04 LTS 或其他支持 Docker 的 Linux 发行版
- **Docker**: 20.10.x 或更高版本
- **Docker Compose**: 2.x 或更高版本
- **Nginx**: 作为容器运行，无需单独安装

## 部署流程

### 1. 前期准备

1. 确保您有一台满足要求的服务器，并拥有 root 或 sudo 权限
2. 域名（可选但推荐）：为您的服务配置一个域名
3. SSL 证书（可选但推荐）：用于 HTTPS 加密

#### 安装基本工具
```bash
# 更新系统包
sudo apt update && sudo apt upgrade -y

# 安装基本工具
sudo apt install -y git curl wget vim
```

### 2. 获取项目代码

```bash
# 克隆仓库
git clone https://github.com/bytedance/ResearcherNexus.git
cd ResearcherNexus
```

### 3. 配置环境

1. 编辑生产环境配置文件：
```bash
cp .env.example .env.production
nano .env.production
```

2. 填写以下必要信息：
   - LLM API 密钥（OPENROUTER_API_KEY）
   - 搜索引擎 API 密钥（TAVILY_API_KEY 等）
   - LangSmith API 密钥（如果使用）

3. 如果需要使用域名和有效的 SSL 证书，修改 Nginx 配置：
```bash
nano nginx/conf.d/default.conf
```
将 `server_name _` 修改为您的域名，并确保 SSL 证书路径正确。

### 4. 使用部署脚本

我们提供了一个部署脚本来简化部署过程：

```bash
# 在 Linux 系统上添加执行权限
chmod +x deploy.sh

# 初始化部署
./deploy.sh --init
```

如果您使用的是 Windows 系统，可以手动执行以下步骤：

```bash
# 创建目录
mkdir -p nginx/conf.d nginx/ssl data

# 复制配置文件
cp .env.production .env

# 启动容器
docker-compose up -d
```

### 5. 验证部署

部署完成后，您可以通过以下方式验证系统是否正常运行：

1. 检查容器状态：
```bash
docker-compose ps
```

2. 查看日志：
```bash
docker-compose logs -f
```

3. 访问网站：
   - 如果配置了域名：https://您的域名
   - 如果使用 IP 访问：https://服务器IP

### 6. 维护操作

#### 更新系统
```bash
# 使用部署脚本更新
./deploy.sh --update

# 或者手动执行
git pull
docker-compose build
docker-compose up -d
```

#### 重启服务
```bash
./deploy.sh --restart
# 或者 docker-compose restart
```

#### 查看日志
```bash
docker-compose logs -f [service_name]
```

#### 停止服务
```bash
./deploy.sh --down
# 或者 docker-compose down
```

## 系统监控

### 基本监控
```bash
# 查看容器资源使用情况
docker stats
```

### 推荐的监控工具
- **Prometheus + Grafana**: 用于监控系统和应用性能
- **ELK Stack**: 用于日志收集和分析
- **Portainer**: 用于 Docker 容器的可视化管理

## 性能调优

### 容器资源分配
根据实际使用情况，您可以在 `docker-compose.yml` 中调整 CPU 和内存限制：

```yaml
deploy:
  resources:
    limits:
      cpus: '4'  # 调整为适当的值
      memory: 8G  # 调整为适当的值
```

### Nginx 调优
对于高并发场景，可以调整 `nginx/conf.d/default.conf` 中的以下参数：

```
worker_connections 2048;
keepalive_timeout 65;
client_max_body_size 10M;
```

### 应用参数调优
在 `.env.production` 中调整以下参数：

```
MAX_WORKERS=4  # 调整为 CPU 核心数
WORKER_TIMEOUT=300
```

## 故障排除

### 常见问题

1. **无法访问 Web 界面**
   - 检查 Nginx 容器是否运行
   - 确认防火墙是否允许 80/443 端口
   - 检查 SSL 证书配置

2. **API 调用失败**
   - 检查 API 容器日志
   - 验证环境变量中的 API 密钥是否正确

3. **容器无法启动**
   - 检查 Docker 日志: `docker-compose logs`
   - 确认磁盘空间是否充足: `df -h`
   - 检查内存使用情况: `free -m`

### 获取支持
如果您遇到无法解决的问题，请通过以下方式获取支持：

1. 在 GitHub 仓库提交 Issue
2. 检查项目文档或讨论区
3. 联系项目维护者

## 数据备份

### 备份重要数据
```bash
# 创建备份目录
mkdir -p backups/$(date +%Y%m%d)

# 备份环境变量
cp .env backups/$(date +%Y%m%d)/

# 备份数据卷
docker run --rm -v researchernexus_api_data:/source -v $(pwd)/backups/$(date +%Y%m%d):/backup ubuntu tar -zcvf /backup/api_data.tar.gz /source
```

## 安全注意事项

1. **API 密钥保护**：确保 `.env` 文件受到保护，权限设为 600
2. **定期更新**：定期更新 Docker 和所有依赖
3. **限制访问**：通过防火墙和 Nginx 配置限制对管理接口的访问
4. **使用 HTTPS**：始终启用 SSL 和 HTTPS
5. **监控异常活动**：设置日志监控和告警 