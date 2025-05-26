import { NextResponse } from "next/server";

export async function POST() {
  try {
    return NextResponse.json(
      { message: "登出成功" },
      { status: 200 }
    );
  } catch (error) {
    console.error("登出错误:", error);
    return NextResponse.json(
      { error: "服务器内部错误" },
      { status: 500 }
    );
  }
} 