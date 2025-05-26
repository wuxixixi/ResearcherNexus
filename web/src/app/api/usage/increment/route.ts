import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import { parseCSV, writeCSV, checkAndResetDailyUsage } from "~/lib/csv-utils";

export async function POST(request: NextRequest) {
  try {
    const { username } = await request.json();

    if (!username) {
      return NextResponse.json(
        { error: "用户名不能为空" },
        { status: 400 }
      );
    }

    // 读取所有用户
    const users = await parseCSV();
    
    // 找到目标用户
    const userIndex = users.findIndex(u => u.username === username);
    
    if (userIndex === -1) {
      return NextResponse.json(
        { error: "用户不存在" },
        { status: 404 }
      );
    }

    let user = users[userIndex]!;
    
    // 检查并重置每日使用次数
    user = checkAndResetDailyUsage(user);
    
    // 检查是否超过每日限制
    if (user.used_today >= user.daily_limit) {
      return NextResponse.json(
        { 
          error: "今日使用次数已达上限",
          daily_limit: user.daily_limit,
          used_today: user.used_today,
          remaining_today: 0
        },
        { status: 429 }
      );
    }

    // 增加使用次数
    user.used_today += 1;
    user.last_used_date = new Date().toISOString().split('T')[0]!;
    
    // 更新用户数组
    users[userIndex] = user;
    
    // 写回CSV文件
    await writeCSV(users);

    return NextResponse.json(
      { 
        message: "使用次数已更新",
        daily_limit: user.daily_limit,
        used_today: user.used_today,
        remaining_today: user.daily_limit - user.used_today
      },
      { status: 200 }
    );
  } catch (error) {
    console.error("更新使用次数错误:", error);
    return NextResponse.json(
      { error: "服务器内部错误" },
      { status: 500 }
    );
  }
} 