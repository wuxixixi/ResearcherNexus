import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import { parseCSV, writeCSV } from "~/lib/csv-utils";

export async function POST(request: NextRequest) {
  try {
    const { username, daily_limit } = await request.json();

    if (!username || daily_limit === undefined) {
      return NextResponse.json(
        { error: "用户名和每日限制不能为空" },
        { status: 400 }
      );
    }

    if (daily_limit < 0) {
      return NextResponse.json(
        { error: "每日限制不能为负数" },
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

    // 更新用户的每日限制
    users[userIndex]!.daily_limit = parseInt(daily_limit.toString());
    
    // 写回CSV文件
    await writeCSV(users);

    return NextResponse.json(
      { 
        message: "每日限制已更新",
        username: users[userIndex]!.username,
        daily_limit: users[userIndex]!.daily_limit
      },
      { status: 200 }
    );
  } catch (error) {
    console.error("更新每日限制错误:", error);
    return NextResponse.json(
      { error: "服务器内部错误" },
      { status: 500 }
    );
  }
} 