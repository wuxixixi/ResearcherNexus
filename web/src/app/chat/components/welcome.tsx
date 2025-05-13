// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { motion } from "framer-motion";

import { cn } from "~/lib/utils";

export function Welcome({ className }: { className?: string }) {
  return (
    <motion.div
      className={cn("flex flex-col", className)}
      style={{ transition: "all 0.2s ease-out" }}
      initial={{ opacity: 0, scale: 0.85 }}
      animate={{ opacity: 1, scale: 1 }}
    >
      <h3 className="mb-2 text-center text-3xl font-medium">
        👋 您好!
      </h3>
      <div className="text-muted-foreground px-4 text-center text-lg">
        欢迎来到{" "}
        <a
          href="🔍https://github.com/wuxixixi/ResearcherNexus"
          target="_blank"
          rel="noopener noreferrer"
          className="hover:underline"
        >
          🔍 ResearcherNexus
        </a>
        ，这是一款基于前沿语言模型构建的深度研究助手，可帮助您在网络上搜索、浏览信息并处理复杂任务。
      </div>
    </motion.div>
  );
}
