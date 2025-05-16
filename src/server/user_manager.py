import os
import csv
import json
import logging
import re # 导入 re 模块用于正则表达式
from typing import List, Dict, Optional, Any
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

# 用户数据CSV文件路径
USER_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
USER_DATA_FILE = os.path.join(USER_DATA_DIR, "users.csv")

# 确保数据目录存在
os.makedirs(USER_DATA_DIR, exist_ok=True)

# 用户字段列表
USER_FIELDS = [
    "id", "username", "email", "password", "role", "daily_limit", "usage_data", "created_at"
]

# 密码强度校验函数
def is_password_strong_enough(password: str) -> bool:
    """
    检查密码是否满足强度要求。
    规则:
    - 最小长度为8位
    - 至少包含一个大写字母 (A-Z)
    - 至少包含一个小写字母 (a-z)
    - 至少包含一个数字 (0-9)
    """
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    return True

def _ensure_csv_exists():
    """确保CSV文件存在，如果不存在则创建"""
    if not os.path.exists(USER_DATA_FILE):
        # 创建文件并写入表头
        with open(USER_DATA_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=USER_FIELDS)
            writer.writeheader()
        
        # 创建默认管理员账户
        create_user(
            username="admin",
            email="wuxi@sass.org.cn",
            password="admin123",
            role="admin",
            daily_limit=9999
        )
        logger.info(f"Created users CSV file at {USER_DATA_FILE} with default admin user")

def _read_users() -> List[Dict]:
    """从CSV文件读取所有用户数据"""
    _ensure_csv_exists()
    
    users = []
    try:
        with open(USER_DATA_FILE, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # 处理usage_data字段，将其转换为Python对象
                if row.get('usage_data'):
                    try:
                        row['usage_data'] = json.loads(row['usage_data'])
                    except json.JSONDecodeError:
                        row['usage_data'] = []
                else:
                    row['usage_data'] = []
                
                # 转换daily_limit为整数
                if 'daily_limit' in row:
                    try:
                        row['daily_limit'] = int(row['daily_limit'])
                    except (ValueError, TypeError):
                        row['daily_limit'] = 10  # 默认限制
                
                users.append(row)
    except Exception as e:
        logger.error(f"Error reading users CSV: {e}")
        return []
    
    return users

def _write_users(users: List[Dict]):
    """将用户数据写入CSV文件"""
    try:
        with open(USER_DATA_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=USER_FIELDS)
            writer.writeheader()
            
            for user in users:
                # 处理usage_data字段，将其转换为JSON字符串
                user_copy = user.copy()
                if 'usage_data' in user_copy:
                    user_copy['usage_data'] = json.dumps(user_copy['usage_data'])
                
                writer.writerow(user_copy)
        
        logger.info(f"Successfully wrote {len(users)} users to CSV file")
    except Exception as e:
        logger.error(f"Error writing users to CSV: {e}")
        raise

def get_user_by_username(username: str) -> Optional[Dict]:
    """根据用户名查找用户"""
    users = _read_users()
    for user in users:
        if user.get('username') == username:
            return user
    return None

def get_user_by_id(user_id: str) -> Optional[Dict]:
    """根据用户ID查找用户"""
    users = _read_users()
    for user in users:
        if user.get('id') == user_id:
            return user
    return None

def get_all_users() -> List[Dict]:
    """获取所有用户，并为每个用户计算当前的具体使用情况"""
    users = _read_users()
    processed_users = []
    for user in users:
        # 移除密码字段
        user_info = {k: v for k, v in user.items() if k != 'password'}
        
        # 为每个用户计算详细的当日使用情况
        # get_user_remaining_usage 需要用户ID，并且会处理管理员的特殊情况
        current_usage_details = get_user_remaining_usage(user['id'])
        user_info['usage'] = current_usage_details # {used, limit, remaining}
        
        # daily_limit 字段可以保留，也可以考虑如果 usage.limit 始终等于 daily_limit，则前端只用 usage.limit
        # 为了清晰，我们暂时保留 user_info 中的 daily_limit 字段，但前端应优先使用 user.usage.limit

        processed_users.append(user_info)
    return processed_users

def create_user(username: str, email: str, password: str, role: str = "user", daily_limit: int = 10) -> Dict:
    """创建新用户"""
    # 检查用户名是否已存在
    if get_user_by_username(username):
        raise ValueError(f"用户名 '{username}' 已存在")

    # 检查密码强度
    if not is_password_strong_enough(password):
        raise ValueError("密码强度不足。密码必须至少8位，且包含大写字母、小写字母和数字。")
    
    # 读取现有用户
    users = _read_users()
    
    # 创建新用户
    user_id = f"user-{int(datetime.now().timestamp())}"
    new_user = {
        "id": user_id,
        "username": username,
        "email": email,
        "password": password,
        "role": role,
        "daily_limit": daily_limit,
        "usage_data": [],
        "created_at": datetime.now().isoformat()
    }
    
    # 添加到用户列表
    users.append(new_user)
    
    # 写入文件
    _write_users(users)
    
    # 返回不包含密码的用户信息
    return {k: v for k, v in new_user.items() if k != 'password'}

def update_user(user_id: str, user_data: Dict) -> Optional[Dict]:
    """更新用户信息"""
    users = _read_users()
    
    for i, user in enumerate(users):
        if user.get('id') == user_id:
            # 更新用户数据但保持ID不变
            users[i].update({k: v for k, v in user_data.items() if k != 'id'})
            _write_users(users)
            return {k: v for k, v in users[i].items() if k != 'password'}
    
    return None

def delete_user(user_id: str) -> bool:
    """删除用户"""
    users = _read_users()
    
    # 检查是否是管理员账号
    for user in users:
        if user.get('id') == user_id and user.get('role') == 'admin':
            raise ValueError("不能删除管理员账号")
    
    # 过滤掉要删除的用户
    updated_users = [user for user in users if user.get('id') != user_id]
    
    # 如果用户数量没变，说明没找到对应ID的用户
    if len(updated_users) == len(users):
        return False
    
    _write_users(updated_users)
    return True

def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """验证用户凭据并返回用户信息"""
    user = get_user_by_username(username)
    
    if user and user.get('password') == password:
        # 返回不包含密码的用户信息
        return {k: v for k, v in user.items() if k != 'password'}
    
    return None

def update_user_usage(user_id: str) -> Dict:
    """更新用户的使用次数
    
    返回: 
        Dict: 包含 success 和可选的 message 字段
    """
    user = get_user_by_id(user_id)
    
    if not user:
        return {"success": False, "message": "用户未找到"}
    
    # 管理员不限制使用次数
    if user.get('role') == 'admin':
        return {"success": True}
    
    # 获取今天的日期
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 获取用户的使用情况
    usage_data = user.get('usage_data', [])
    
    # 查找今天的使用记录
    today_usage = None
    for usage in usage_data:
        if usage.get('date') == today:
            today_usage = usage
            break
    
    # 如果没有今天的记录，创建一个
    if not today_usage:
        today_usage = {"date": today, "count": 0}
        usage_data.append(today_usage)
    
    # 检查是否超过每日限制
    if today_usage['count'] >= user.get('daily_limit', 10):
        return {
            "success": False, 
            "message": f"您今日的使用次数已达上限({user.get('daily_limit', 10)}次)，请明天再试或联系管理员增加配额"
        }
    
    # 更新使用次数
    today_usage['count'] += 1
    
    # 更新用户数据
    user['usage_data'] = usage_data
    update_user(user_id, user)
    
    # 获取更新后的数据
    updated_user = get_user_by_id(user_id)
    if not updated_user:
        return {"success": False, "message": "更新用户数据失败"}
    
    # 计算剩余使用次数
    used = 0
    for usage in updated_user.get('usage_data', []):
        if usage.get('date') == today:
            used = usage.get('count', 0)
            break
    
    limit = updated_user.get('daily_limit', 10)
    remaining = max(0, limit - used)
    
    return {
        "success": True,
        "usage": {
            "used": used,
            "limit": limit,
            "remaining": remaining
        }
    }

def get_user_remaining_usage(user_id: str) -> Dict:
    """获取用户剩余使用次数"""
    user = get_user_by_id(user_id)
    
    if not user:
        return {"used": 0, "limit": 0, "remaining": 0}
    
    # 管理员不限制使用次数
    if user.get('role') == 'admin':
        return {"used": 0, "limit": 9999, "remaining": 9999}
    
    # 获取今天的日期
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 计算已使用次数
    used = 0
    for usage in user.get('usage_data', []):
        if usage.get('date') == today:
            used = usage.get('count', 0)
            break
    
    limit = user.get('daily_limit', 10)
    remaining = max(0, limit - used)
    
    return {"used": used, "limit": limit, "remaining": remaining} 