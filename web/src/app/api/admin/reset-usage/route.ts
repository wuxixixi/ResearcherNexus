import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import { parseCSV, writeCSV } from "~/lib/csv-utils";

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

    // 重置用户的今日使用次数
    users[userIndex]!.used_today = 0;
    users[userIndex]!.last_used_date = new Date().toISOString().split('T')[0]!;
    
    // 写回CSV文件
    await writeCSV(users);

    return NextResponse.json(
      { 
        message: "今日使用次数已重置",
        username: users[userIndex]!.username,
        used_today: users[userIndex]!.used_today,
        remaining_today: users[userIndex]!.daily_limit - users[userIndex]!.used_today
      },
      { status: 200 }
    );
  } catch (error) {
    console.error("重置使用次数错误:", error);
    return NextResponse.json(
      { error: "服务器内部错误" },
      { status: 500 }
    );
  }
} 