"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Trash2, Edit, Plus, Search, Filter, XCircle, Save, Ban, Home } from "lucide-react";
import Link from "next/link";

import { useAuth } from "~/lib/auth-context";
import { Button } from "~/components/ui/button";
import { Input } from "~/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "~/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "~/components/ui/dialog";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "~/components/ui/pagination";

export default function AdminPage() {
  const { user, isAdmin, getAllUsers, deleteUser, updateUserLimit } = useAuth();
  const router = useRouter();
  
  const [users, setUsers] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [filteredUsers, setFilteredUsers] = useState<any[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(10);
  const [selectedUser, setSelectedUser] = useState<any | null>(null);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [newDailyLimit, setNewDailyLimit] = useState<number>(10);

  // 检查是否是管理员
  useEffect(() => {
    if (!isAdmin) {
      router.push("/");
    }
  }, [isAdmin, router]);

  // 加载用户数据
  useEffect(() => {
    if (isAdmin) {
      const fetchUsers = async () => {
        try {
          const allUsers = await getAllUsers();
          setUsers(allUsers);
          setFilteredUsers(allUsers);
        } catch (error) {
          console.error("获取用户列表失败:", error);
          setUsers([]); // 出错时设置为空数组
          setFilteredUsers([]);
        }
      };
      fetchUsers();
    }
  }, [isAdmin, getAllUsers]);

  // 搜索和过滤
  useEffect(() => {
    const results = users.filter((user) => {
      return (
        user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.email.toLowerCase().includes(searchTerm.toLowerCase())
      );
    });
    setFilteredUsers(results);
    setCurrentPage(1);
  }, [searchTerm, users]);

  // 获取当前页数据
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = filteredUsers.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(filteredUsers.length / itemsPerPage);

  // 页面导航
  const paginate = (pageNumber: number) => setCurrentPage(pageNumber);

  // 准备删除用户
  const prepareDeleteUser = (user: any) => {
    setSelectedUser(user);
    setIsDeleteDialogOpen(true);
  };

  // 执行删除操作
  const confirmDeleteUser = async () => {
    if (selectedUser) {
      try {
        await deleteUser(selectedUser.id);
        setUsers(users.filter((u) => u.id !== selectedUser.id));
        setIsDeleteDialogOpen(false);
        setSelectedUser(null);
      } catch (error) {
        console.error("删除用户失败:", error);
      }
    }
  };

  // 准备编辑用户配额
  const prepareEditUser = (user: any) => {
    setSelectedUser(user);
    setNewDailyLimit(user.usage?.limit ?? user.dailyLimit ?? 10);
    setIsEditDialogOpen(true);
  };

  // 执行更新操作
  const confirmUpdateLimit = async () => {
    if (selectedUser && newDailyLimit >= 0) {
      try {
        await updateUserLimit(selectedUser.id, newDailyLimit);
        setUsers(
          users.map((u) =>
            u.id === selectedUser.id 
            ? { 
                ...u, 
                dailyLimit: newDailyLimit,
                usage: { 
                  ...(u.usage || {}), 
                  limit: newDailyLimit, 
                  remaining: Math.max(0, newDailyLimit - (u.usage?.used ?? 0))
                } 
              }
            : u
          )
        );
        refreshUsers();
        setIsEditDialogOpen(false);
        setSelectedUser(null);
      } catch (error) {
        console.error("更新用户配额失败:", error);
      }
    }
  };

  // 刷新用户列表
  const refreshUsers = async () => {
    if (isAdmin) {
      try {
        const allUsers = await getAllUsers();
        setUsers(allUsers);
        setFilteredUsers(allUsers);
      } catch (error) {
        console.error("刷新用户列表失败:", error);
      }
    }
  };

  if (!isAdmin) {
    return null; // 不是管理员则不显示内容
  }

  return (
    <div className="container mx-auto p-6">
      <header className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold mb-2">用户管理后台</h1>
          <p className="text-muted-foreground">管理所有注册用户和使用限制</p>
        </div>
        <Link href="/">
          <Button variant="outline" className="flex items-center gap-2">
            <Home className="h-4 w-4" />
            返回主页
          </Button>
        </Link>
      </header>

      <div className="flex justify-between mb-6">
        <div className="relative w-1/3">
          <Search className="absolute left-2 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="搜索用户名或邮箱..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-8"
          />
          {searchTerm && (
            <button
              onClick={() => setSearchTerm("")}
              className="absolute right-2 top-1/2 -translate-y-1/2"
            >
              <XCircle className="h-4 w-4 text-muted-foreground" />
            </button>
          )}
        </div>

        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={refreshUsers}
            className="flex items-center gap-1"
          >
            <Filter className="h-4 w-4" />
            刷新
          </Button>
        </div>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>用户ID</TableHead>
              <TableHead>用户名</TableHead>
              <TableHead>邮箱</TableHead>
              <TableHead>角色</TableHead>
              <TableHead>每日使用限制</TableHead>
              <TableHead>已用次数(今日)</TableHead>
              <TableHead className="text-right">操作</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {currentItems.length > 0 ? (
              currentItems.map((user) => {
                // 使用后端直接提供的 usage 对象中的信息
                const usedToday = user.usage?.used ?? 0;
                const dailyLimit = user.usage?.limit ?? user.dailyLimit ?? 0; // 优先用 usage.limit，其次用顶层 dailyLimit

                return (
                  <TableRow key={user.id}>
                    <TableCell className="font-mono text-xs">{user.id}</TableCell>
                    <TableCell className="font-medium">{user.username}</TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>
                      <span
                        className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${user.role === "admin" ? "bg-blue-100 text-blue-800" : "bg-green-100 text-green-800"}`}
                      >
                        {user.role === "admin" ? "管理员" : "普通用户"}
                      </span>
                    </TableCell>
                    <TableCell>{dailyLimit}</TableCell>
                    <TableCell>
                      {usedToday}
                      {usedToday >= dailyLimit && user.role !== "admin" && (
                        <span className="ml-2 inline-flex items-center rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-medium text-red-800">
                          已达上限
                        </span>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => prepareEditUser(user)}
                          disabled={user.role === "admin"}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => prepareDeleteUser(user)}
                          disabled={user.role === "admin"}
                        >
                          <Trash2 className="h-4 w-4 text-red-500" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                );
              })
            ) : (
              <TableRow>
                <TableCell colSpan={7} className="h-24 text-center">
                  没有找到用户
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {totalPages > 1 && (
        <Pagination className="mt-4">
          <PaginationContent>
            <PaginationItem>
              <PaginationPrevious
                onClick={() => paginate(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
              />
            </PaginationItem>
            {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
              <PaginationItem key={page}>
                <PaginationLink
                  onClick={() => paginate(page)}
                  isActive={page === currentPage}
                >
                  {page}
                </PaginationLink>
              </PaginationItem>
            ))}
            <PaginationItem>
              <PaginationNext
                onClick={() => paginate(Math.min(totalPages, currentPage + 1))}
                disabled={currentPage === totalPages}
              />
            </PaginationItem>
          </PaginationContent>
        </Pagination>
      )}

      {/* 删除用户对话框 */}
      <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>确认删除用户</DialogTitle>
            <DialogDescription>
              您确定要删除用户 "{selectedUser?.username}"（{selectedUser?.email}）吗？此操作不可撤销。
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsDeleteDialogOpen(false)}
            >
              取消
            </Button>
            <Button variant="destructive" onClick={confirmDeleteUser}>
              <Trash2 className="mr-2 h-4 w-4" />
              删除
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 编辑用户配额对话框 */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>修改用户每日使用限额</DialogTitle>
            <DialogDescription>
              设置用户 "{selectedUser?.username}"（{selectedUser?.email}）的每日使用次数限制：
            </DialogDescription>
          </DialogHeader>
          <div className="my-4">
            <label htmlFor="dailyLimit" className="block mb-2">
              每日使用次数：
            </label>
            <Input
              id="dailyLimit"
              type="number"
              min="0"
              value={newDailyLimit}
              onChange={(e) => setNewDailyLimit(parseInt(e.target.value) || 0)}
            />
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsEditDialogOpen(false)}
            >
              取消
            </Button>
            <Button variant="default" onClick={confirmUpdateLimit}>
              <Save className="mr-2 h-4 w-4" />
              保存
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
} 