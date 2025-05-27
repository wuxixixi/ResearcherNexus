// Copyright (c) 2025 SASS and/or its affiliates
// SPDX-License-Identifier: MIT

import { Loader2 } from "lucide-react";
import { useCallback, useState } from "react";

import { Button } from "~/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "~/components/ui/dialog";
import { Textarea } from "~/components/ui/textarea";
import { queryMCPServerMetadata } from "~/core/api";
import {
  MCPConfigSchema,
  type MCPServerMetadata,
  type SimpleMCPServerMetadata,
  type SimpleSSEMCPServerMetadata,
  type SimpleStdioMCPServerMetadata,
} from "~/core/mcp";

export function AddMCPServerDialog({
  onAdd,
}: {
  onAdd?: (servers: MCPServerMetadata[]) => void;
}) {
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [validationError, setValidationError] = useState<string | null>("");
  const [error, setError] = useState<string | null>(null);
  const [processing, setProcessing] = useState(false);
  const handleChange = useCallback((value: string) => {
    setInput(value);
    if (!value.trim()) {
      setValidationError(null);
      return;
    }
    setValidationError(null);
    try {
      const parsed = JSON.parse(value);
      if (!("mcpServers" in parsed)) {
        setValidationError("Missing `mcpServers` in JSON");
        return;
      }
    } catch {
      setValidationError("Invalid JSON");
      return;
    }
    const result = MCPConfigSchema.safeParse(JSON.parse(value));
    if (!result.success) {
      if (result.error.errors[0]) {
        const error = result.error.errors[0];
        if (error.code === "invalid_union") {
          if (error.unionErrors[0]?.errors[0]) {
            setValidationError(error.unionErrors[0].errors[0].message);
            return;
          }
        }
      }
      const errorMessage =
        result.error.errors[0]?.message ?? "Validation failed";
      setValidationError(errorMessage);
      return;
    }

    const keys = Object.keys(result.data.mcpServers);
    if (keys.length === 0) {
      setValidationError("Missing server name in `mcpServers`");
      return;
    }
  }, []);
  const handleAdd = useCallback(async () => {
    const config = MCPConfigSchema.parse(JSON.parse(input));
    setInput(JSON.stringify(config, null, 2));
    const addingServers: SimpleMCPServerMetadata[] = [];
    for (const [key, server] of Object.entries(config.mcpServers)) {
      if ("command" in server) {
        const metadata: SimpleStdioMCPServerMetadata = {
          transport: "stdio",
          name: key,
          command: server.command,
          args: server.args,
          env: server.env,
        };
        addingServers.push(metadata);
      } else if ("url" in server) {
        const metadata: SimpleSSEMCPServerMetadata = {
          transport: "sse",
          name: key,
          url: server.url,
        };
        addingServers.push(metadata);
      }
    }
    setProcessing(true);

    const results: MCPServerMetadata[] = [];
    let processingServer: string | null = null;
    try {
      setError(null);
      for (const server of addingServers) {
        processingServer = server.name;
        const metadata = await queryMCPServerMetadata(server);
        
        if (!metadata.tools || metadata.tools.length === 0) {
          throw new Error(`服务器 "${processingServer}" 没有返回任何工具。这可能是因为：\n1. 服务器启动失败\n2. 命令或参数不正确\n3. Windows环境下的兼容性问题\n4. 网络连接问题\n\n请检查服务器配置或查看控制台日志获取更多信息。`);
        }
        
        results.push({ ...metadata, name: server.name, enabled: true });
      }
      if (results.length > 0) {
        onAdd?.(results);
      }
      setInput("");
      setOpen(false);
    } catch (e) {
      console.error(e);
      const errorMessage = e instanceof Error ? e.message : `Failed to add server: ${processingServer}`;
      setError(errorMessage);
    } finally {
      setProcessing(false);
    }
  }, [input, onAdd]);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm">添加服务</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[560px]">
        <DialogHeader>
          <DialogTitle>添加新的MCP服务</DialogTitle>
        </DialogHeader>
        <DialogDescription>
          ResearcherNexus使用标准的JSON MCP配置来创建一个新服务器。
          <br />
          将您的配置粘贴到下方，然后点击&ldquo;添加&rdquo;以添加新服务器。
        </DialogDescription>

        <main>
          <Textarea
            className="h-[360px]"
            placeholder={
              'Windows环境推荐配置示例:\n\n{\n  "mcpServers": {\n    "memory-server": {\n      "command": "npx",\n      "args": [\n        "@modelcontextprotocol/server-memory"\n      ]\n    },\n    "filesystem-server": {\n      "command": "npx",\n      "args": [\n        "@modelcontextprotocol/server-filesystem",\n        "C:\\\\Users"\n      ]\n    }\n  }\n}\n\n注意：\n1. Windows环境下某些MCP服务器可能不兼容\n2. 如果添加失败，请检查命令和参数是否正确\n3. 可以查看控制台日志获取详细错误信息'
            }
            value={input}
            onChange={(e) => handleChange(e.target.value)}
          />
        </main>

        <DialogFooter>
          <div className="flex h-auto w-full items-start justify-between gap-2">
            <div className="text-destructive flex-grow overflow-hidden text-sm">
              {(validationError ?? error) && (
                <div className="whitespace-pre-wrap break-words max-h-32 overflow-y-auto p-2 bg-red-50 dark:bg-red-950 rounded border border-red-200 dark:border-red-800">
                  {validationError ?? error}
                </div>
              )}
            </div>
            <div className="flex items-center gap-2 flex-shrink-0">
              <Button variant="outline" onClick={() => setOpen(false)}>
                取消
              </Button>
              <Button
                className="w-24"
                type="submit"
                disabled={!input.trim() || !!validationError || processing}
                onClick={handleAdd}
              >
                {processing && <Loader2 className="animate-spin" />}
                添加
              </Button>
            </div>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
