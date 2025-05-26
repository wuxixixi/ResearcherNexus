import { promises as fs } from "fs";
import path from "path";

// CSV文件路径
const CSV_FILE_PATH = path.join(process.cwd(), "users.csv");

// 用户接口
export interface User {
  username: string;
  password: string;
  role: string;
  daily_limit: number;
  used_today: number;
  last_used_date: string;
}

// 文件锁管理
class FileLock {
  private locks = new Map<string, Promise<void>>();

  async withLock<T>(key: string, fn: () => Promise<T>): Promise<T> {
    // 等待之前的操作完成
    const existingLock = this.locks.get(key);
    if (existingLock) {
      await existingLock;
    }

    // 创建新的锁
    let resolve: () => void;
    const lockPromise = new Promise<void>((res) => {
      resolve = res;
    });
    this.locks.set(key, lockPromise);

    try {
      const result = await fn();
      return result;
    } finally {
      // 释放锁
      this.locks.delete(key);
      resolve!();
    }
  }
}

const fileLock = new FileLock();

// 确保CSV文件存在，如果不存在则创建一个默认的
async function ensureCSVFile() {
  try {
    await fs.access(CSV_FILE_PATH);
  } catch {
    // 文件不存在，创建默认用户
    const defaultUsers = "username,password,role,daily_limit,used_today,last_used_date\nadmin,admin123,admin,999,0,\nuser,password,user,10,0,\n";
    await fs.writeFile(CSV_FILE_PATH, defaultUsers, "utf8");
  }
}

// 解析CSV文件
export async function parseCSV(): Promise<User[]> {
  return fileLock.withLock(CSV_FILE_PATH, async () => {
    await ensureCSVFile();
    const csvContent = await fs.readFile(CSV_FILE_PATH, "utf8");
    const lines = csvContent.trim().split("\n");
    
    const users = lines.slice(1).map(line => {
      const values = line.split(",");
      return {
        username: values[0]?.trim() ?? "",
        password: values[1]?.trim() ?? "",
        role: values[2]?.trim() ?? "user",
        daily_limit: parseInt(values[3]?.trim() ?? "10"),
        used_today: parseInt(values[4]?.trim() ?? "0"),
        last_used_date: values[5]?.trim() ?? "",
      };
    });
    
    return users.filter(user => user.username && user.password);
  });
}

// 写入CSV文件
export async function writeCSV(users: User[]): Promise<void> {
  return fileLock.withLock(CSV_FILE_PATH, async () => {
    const header = "username,password,role,daily_limit,used_today,last_used_date";
    const lines = users.map(user => 
      `${user.username},${user.password},${user.role},${user.daily_limit},${user.used_today},${user.last_used_date}`
    );
    const csvContent = [header, ...lines].join("\n");
    
    // 使用临时文件写入，然后重命名，避免写入过程中的文件损坏
    const tempPath = CSV_FILE_PATH + '.tmp';
    await fs.writeFile(tempPath, csvContent, "utf8");
    await fs.rename(tempPath, CSV_FILE_PATH);
  });
}

// 检查并重置每日使用次数
export function checkAndResetDailyUsage(user: User): User {
  const today = new Date().toISOString().split('T')[0]!;
  
  if (user.last_used_date !== today) {
    return {
      ...user,
      used_today: 0,
      last_used_date: today
    };
  }
  
  return user;
} 