import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import { parseCSV, checkAndResetDailyUsage } from "~/lib/csv-utils";

export async function POST(request: NextRequest) {
  try {
    const { username, password } = await request.json();

    if (!username || !password) {
      return NextResponse.json(
        { error: "用户名和密码不能为空" },
        { status: 400 }
      );
    }

    // 读取CSV文件中的用户
    const users = await parseCSV();
    
    // 验证用户
    let user = users.find(
      u => u.username === username && u.password === password
    );

    if (user) {
      // 检查并重置每日使用次数
      user = checkAndResetDailyUsage(user);
      
      return NextResponse.json(
        { 
          message: "登录成功", 
          username: user.username,
          role: user.role,
          daily_limit: user.daily_limit,
          used_today: user.used_today,
          remaining_today: user.daily_limit - user.used_today
        },
        { status: 200 }
      );
    } else {
      return NextResponse.json(
        { error: "用户名或密码错误" },
        { status: 401 }
      );
    }
  } catch (error) {
    console.error("登录错误:", error);
    return NextResponse.json(
      { error: "服务器内部错误" },
      { status: 500 }
    );
  }
} 