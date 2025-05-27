// Copyright (c) 2025 SASS and/or its affiliates
// SPDX-License-Identifier: MIT

import { Settings, type LucideIcon } from "lucide-react";

import { AboutTab } from "./about-tab";
import { GeneralTab } from "./general-tab";
import { MCPTab } from "./mcp-tab";

// 定义标签的中文名称映射
const TAB_LABELS: Record<string, string> = {
  General: "通用",
  MCP: "MCP",
  About: "关于",
};

export const SETTINGS_TABS = [GeneralTab, MCPTab, AboutTab].map((tab) => {
  // 直接使用 displayName，不再依赖 name 属性
  const displayName = tab.displayName ?? "";
  const baseLabel = displayName.replace(/Tab$/, "");
  return {
    ...tab,
    id: baseLabel.toLowerCase(),
    label: TAB_LABELS[baseLabel] ?? baseLabel,
    icon: (tab.icon ?? <Settings />) as LucideIcon,
    component: tab,
  };
});
