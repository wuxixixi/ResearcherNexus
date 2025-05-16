// Copyright (c) 2025 SASS and/or its affiliates
// SPDX-License-Identifier: MIT

import { Bird, Microscope, Podcast, Usb, User } from "lucide-react";

import { BentoCard, BentoGrid } from "~/components/magicui/bento-grid";

import { SectionHeader } from "../components/section-header";

const features = [
  {
    Icon: Microscope,
    name: "深度挖掘，广泛触达",
    description:
      "通过先进工具获取深度洞察。我们强大的搜索+爬虫和Python工具收集全面数据，提供深入报告以增强您的研究。",
    href: "https://github.com/wuxixixi/ResearcherNexus/blob/main/src/tools",
    cta: "了解更多",
    background: (
      <img alt="background" className="absolute -top-20 -right-20 opacity-60" />
    ),
    className: "lg:col-start-1 lg:col-end-2 lg:row-start-1 lg:row-end-3",
  },
  {
    Icon: User,
    name: "人机协作模式",
    description:
      "通过简单的自然语言，精细调整您的研究计划或调整研究重点。",
    href: "https://github.com/wuxixixi/ResearcherNexus/blob/main/src/graph/nodes.py",
    cta: "了解更多",
    background: (
      <img alt="background" className="absolute -top-20 -right-20 opacity-60" />
    ),
    className: "lg:col-start-1 lg:col-end-2 lg:row-start-3 lg:row-end-4",
  },
  {
    Icon: Bird,
    name: "语言技术栈",
    description:
      "基于LangChain和LangGraph框架构建，提供可靠性和灵活性。",
    href: "https://www.langchain.com/",
    cta: "了解更多",
    background: (
      <img alt="background" className="absolute -top-20 -right-20 opacity-60" />
    ),
    className: "lg:col-start-2 lg:col-end-3 lg:row-start-1 lg:row-end-2",
  },
  {
    Icon: Usb,
    name: "MCP集成",
    description:
      "通过无缝MCP集成增强您的研究工作流程并扩展您的工具箱。",
    href: "https://github.com/wuxixixi/ResearcherNexus/blob/main/src/graph/nodes.py",
    cta: "了解更多",
    background: (
      <img alt="background" className="absolute -top-20 -right-20 opacity-60" />
    ),
    className: "lg:col-start-2 lg:col-end-3 lg:row-start-2 lg:row-end-3",
  },
  {
    Icon: Podcast,
    name: "播客生成",
    description:
      "从报告中即时生成播客。完美适合移动学习或轻松分享研究成果。",
    href: "https://github.com/wuxixixi/ResearcherNexus/blob/main/src/podcast",
    cta: "了解更多",
    background: (
      <img alt="background" className="absolute -top-20 -right-20 opacity-60" />
    ),
    className: "lg:col-start-2 lg:col-end-3 lg:row-start-3 lg:row-end-4",
  },
];

export function CoreFeatureSection() {
  return (
    <section className="relative flex w-full flex-col content-around items-center justify-center">
      <SectionHeader
        anchor="core-features"
        title="核心功能"
        description="探索使ResearcherNexus高效的关键特性。"
      />
      <BentoGrid className="w-3/4 lg:grid-cols-2 lg:grid-rows-3">
        {features.map((feature) => (
          <BentoCard key={feature.name} {...feature} />
        ))}
      </BentoGrid>
    </section>
  );
}
