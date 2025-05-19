// Copyright (c) 2025 SASS and/or its affiliates
// SPDX-License-Identifier: MIT

import { Bird, Microscope, Podcast, Usb, User } from "lucide-react";

import { BentoCard, BentoGrid } from "~/components/magicui/bento-grid";

import { SectionHeader } from "../components/section-header";

const features = [
  {
    Icon: Microscope,
    name: "深入探索与广泛触达",
    description:
      "利用先进工具解锁更深层次的见解。我们强大的搜索+抓取和Python工具可收集全面数据，提供深度报告以增强您的研究",
    href: "https://github.com/wuxixixi/ResearcherNexus/blob/main/src/tools",
    cta: "Learn more",
    background: (
      <img alt="background" className="absolute -top-20 -right-20 opacity-60" />
    ),
    className: "lg:col-start-1 lg:col-end-2 lg:row-start-1 lg:row-end-3",
  },
  {
    Icon: User,
    name: "人工参与",
    description:
      "通过简单的自然语言优化您的研究计划，或调整重点领域",
    href: "https://github.com/wuxixixi/ResearcherNexus/blob/main/src/graph/nodes.py",
    cta: "Learn more",
    background: (
      <img alt="background" className="absolute -top-20 -right-20 opacity-60" />
    ),
    className: "lg:col-start-1 lg:col-end-2 lg:row-start-3 lg:row-end-4",
  },
  {
    Icon: Bird,
    name: "Lang Stack",
    description:
      "使用 LangChain 和 LangGraph 框架自信地构建",
    href: "https://www.langchain.com/",
    cta: "Learn more",
    background: (
      <img alt="background" className="absolute -top-20 -right-20 opacity-60" />
    ),
    className: "lg:col-start-2 lg:col-end-3 lg:row-start-1 lg:row-end-2",
  },
  {
    Icon: Usb,
    name: "MCP 集成",
    description:
      "通过无缝的 MCP 集成，增强您的研究工作流程并扩展您的工具包",
    href: "https://github.com/wuxixixi/ResearcherNexus/blob/main/src/graph/nodes.py",
    cta: "Learn more",
    background: (
      <img alt="background" className="absolute -top-20 -right-20 opacity-60" />
    ),
    className: "lg:col-start-2 lg:col-end-3 lg:row-start-2 lg:row-end-3",
  },
  {
    Icon: Podcast,
    name: "播客生成",
    description:
      "即时从报告生成播客 非常适合随时随地学习或轻松分享研究成果",
    href: "https://github.com/wuxixixi/ResearcherNexus/blob/main/src/podcast",
    cta: "Learn more",
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
        description="让 ResearcherNexus 高效"
      />
      <BentoGrid className="w-3/4 lg:grid-cols-2 lg:grid-rows-3">
        {features.map((feature) => (
          <BentoCard key={feature.name} {...feature} />
        ))}
      </BentoGrid>
    </section>
  );
}
