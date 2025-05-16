#!/bin/bash

# ResearcherNexus 部署脚本
# 此脚本用于在服务器上部署 ResearcherNexus 应用

set -e

# 显示帮助信息
show_help() {
    echo "ResearcherNexus 部署脚本"
    echo "用法: ./deploy.sh [选项]"
    echo "选项:"
    echo "  -i, --init     首次初始化部署"
    echo "  -u, --update   更新现有部署"
    echo "  -r, --restart  重启服务"
    echo "  -d, --down     停止并删除容器"
    echo "  -h, --help     显示此帮助信息"
}

# 检查依赖
check_dependencies() {
    echo "检查依赖..."
    if ! command -v docker &> /dev/null; then
        echo "未发现Docker，正在安装..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker $USER
        echo "请使用新的shell会话，或者使用 'su - $USER' 重新登录后继续"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "未发现Docker Compose，正在安装..."
        sudo curl -L "https://github.com/docker/compose/releases/download/v2.18.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
    fi
    
    echo "所有依赖已满足"
}

# 创建自签名SSL证书（仅用于测试）
create_self_signed_cert() {
    echo "创建自签名SSL证书（仅用于测试环境）..."
    mkdir -p nginx/ssl
    
    # 生成自签名证书
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
      -keyout nginx/ssl/key.pem \
      -out nginx/ssl/cert.pem \
      -subj "/C=CN/ST=State/L=City/O=Organization/CN=localhost"
      
    echo "自签名证书已创建"
}

# 初始化部署
init_deploy() {
    echo "初始化ResearcherNexus部署..."
    
    check_dependencies
    
    # 创建必要的目录
    mkdir -p nginx/conf.d
    mkdir -p nginx/ssl
    mkdir -p data
    
    # 检查是否已有配置文件
    if [ ! -f "nginx/conf.d/default.conf" ]; then
        echo "未找到Nginx配置，请确保 nginx/conf.d/default.conf 文件存在"
        exit 1
    fi
    
    # 检查环境变量文件
    if [ ! -f ".env.production" ]; then
        echo "未找到.env.production文件，请确保它已正确配置"
        exit 1
    fi
    
    # 复制环境变量
    cp .env.production .env
    
    # 创建自签名证书（如果需要）
    if [ ! -f "nginx/ssl/cert.pem" ]; then
        create_self_signed_cert
    fi
    
    # 构建和启动容器
    echo "构建和启动Docker容器..."
    docker-compose build
    docker-compose up -d
    
    echo "ResearcherNexus已成功初始化并启动"
    echo "访问 https://your_server_ip 查看应用（请替换成您的域名或IP）"
}

# 更新部署
update_deploy() {
    echo "更新ResearcherNexus部署..."
    
    # 备份配置文件
    timestamp=$(date +%Y%m%d_%H%M%S)
    mkdir -p backups/$timestamp
    cp .env backups/$timestamp/ 2>/dev/null || true
    
    # 拉取最新代码
    git pull
    
    # 复制环境变量（如果存在）
    if [ -f ".env.production" ]; then
        cp .env.production .env
    fi
    
    # 重新构建和启动容器
    docker-compose build
    docker-compose up -d
    
    echo "ResearcherNexus已成功更新"
}

# 重启服务
restart_services() {
    echo "重启ResearcherNexus服务..."
    docker-compose restart
    echo "服务已重启"
}

# 停止并删除容器
down_services() {
    echo "停止并删除ResearcherNexus容器..."
    docker-compose down
    echo "容器已停止和删除"
}

# 处理命令行参数
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

case "$1" in
    -i|--init)
        init_deploy
        ;;
    -u|--update)
        update_deploy
        ;;
    -r|--restart)
        restart_services
        ;;
    -d|--down)
        down_services
        ;;
    -h|--help)
        show_help
        ;;
    *)
        echo "未知选项: $1"
        show_help
        exit 1
        ;;
esac

exit 0 