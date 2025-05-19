// Copyright (c) 2025 SASS and/or its affiliates
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
      🤓 您好！
      </h3>
      <div className="text-muted-foreground px-4 text-center text-lg">
        欢迎使用{" "}
        <a
          href="https://github.com/wuxixixi/ResearcherNexus"
          target="_blank"
          rel="noopener noreferrer"
          className="hover:underline"
        >
          🔍 ResearcherNexus
        </a>
        , 一款基于尖端语言模型的深度研究助手，助您实现网络搜索、信息浏览及复杂任务处理。
      </div>
    </motion.div>
  );
}
