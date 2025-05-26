import { promises as fs } from "fs";
import path from "path";

import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

// CSV文件路径
const CSV_FILE_PATH = path.join(process.cwd(), "users.csv");

// 确保CSV文件存在，如果不存在则创建一个默认的
async function ensureCSVFile() {
  try {
    await fs.access(CSV_FILE_PATH);
  } catch {
    // 文件不存在，创建默认用户
    const defaultUsers = "username,password\nadmin,admin123\nuser,password\n";
    await fs.writeFile(CSV_FILE_PATH, defaultUsers, "utf8");
  }
}

// 解析CSV文件
async function parseCSV(): Promise<Array<{ username: string; password: string }>> {
  await ensureCSVFile();
  const csvContent = await fs.readFile(CSV_FILE_PATH, "utf8");
  const lines = csvContent.trim().split("\n");
  
  const users = lines.slice(1).map(line => {
    const values = line.split(",");
    return {
      username: values[0]?.trim() ?? "",
      password: values[1]?.trim() ?? "",
    };
  });
  
  return users.filter(user => user.username && user.password);
}

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
    const user = users.find(
      u => u.username === username && u.password === password
    );

    if (user) {
      return NextResponse.json(
        { message: "登录成功", username: user.username },
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