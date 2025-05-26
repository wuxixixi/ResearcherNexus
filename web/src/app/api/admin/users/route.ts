import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import { parseCSV, checkAndResetDailyUsage } from "~/lib/csv-utils";

export async function GET(_request: NextRequest) {
  try {
    // 读取所有用户
    let users = await parseCSV();
    
    // 检查并重置每日使用次数
    users = users.map(checkAndResetDailyUsage);
    
    // 返回用户列表（不包含密码）
    const userList = users.map(user => ({
      username: user.username,
      role: user.role,
      daily_limit: user.daily_limit,
      used_today: user.used_today,
      last_used_date: user.last_used_date,
    }));

    return NextResponse.json(
      { 
        message: "获取用户列表成功",
        users: userList
      },
      { status: 200 }
    );
  } catch (error) {
    console.error("获取用户列表错误:", error);
    return NextResponse.json(
      { error: "服务器内部错误" },
      { status: 500 }
    );
  }
} 