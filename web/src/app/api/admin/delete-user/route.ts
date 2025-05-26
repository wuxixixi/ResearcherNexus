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

    // 检查是否尝试删除管理员账户
    if (users[userIndex]!.role === "admin") {
      return NextResponse.json(
        { error: "不能删除管理员账户" },
        { status: 403 }
      );
    }

    // 删除用户
    users.splice(userIndex, 1);
    
    // 写回CSV文件
    await writeCSV(users);

    return NextResponse.json(
      { 
        message: "用户已删除",
        username: username
      },
      { status: 200 }
    );
  } catch (error) {
    console.error("删除用户错误:", error);
    return NextResponse.json(
      { error: "服务器内部错误" },
      { status: 500 }
    );
  }
} 