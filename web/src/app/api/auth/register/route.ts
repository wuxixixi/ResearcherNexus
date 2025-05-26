import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import { parseCSV, writeCSV, type User } from "~/lib/csv-utils";

export async function POST(request: NextRequest) {
  try {
    const { username, password } = await request.json();

    // 验证输入
    if (!username || !password) {
      return NextResponse.json(
        { error: "用户名和密码不能为空" },
        { status: 400 }
      );
    }

    if (username.length < 3) {
      return NextResponse.json(
        { error: "用户名长度至少为3位" },
        { status: 400 }
      );
    }

    if (password.length < 6) {
      return NextResponse.json(
        { error: "密码长度至少为6位" },
        { status: 400 }
      );
    }

    // 验证用户名格式（只允许字母、数字和下划线）
    if (!/^[a-zA-Z0-9_]+$/.test(username)) {
      return NextResponse.json(
        { error: "用户名只能包含字母、数字和下划线" },
        { status: 400 }
      );
    }

    // 读取现有用户
    const users = await parseCSV();
    
    // 检查用户名是否已存在
    const existingUser = users.find(u => u.username === username);
    if (existingUser) {
      return NextResponse.json(
        { error: "用户名已存在" },
        { status: 409 }
      );
    }

    // 创建新用户
    const newUser: User = {
      username,
      password,
      role: "user",
      daily_limit: 10,
      used_today: 0,
      last_used_date: "",
    };

    // 添加到用户列表
    users.push(newUser);
    
    // 写回CSV文件
    await writeCSV(users);

    return NextResponse.json(
      { 
        message: "注册成功",
        username: newUser.username
      },
      { status: 201 }
    );
  } catch (error) {
    console.error("注册错误:", error);
    return NextResponse.json(
      { error: "服务器内部错误" },
      { status: 500 }
    );
  }
} 