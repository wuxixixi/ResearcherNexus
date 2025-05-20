// Copyright (c) 2025 SASS and/or its affiliates
// SPDX-License-Identifier: MIT

import { GithubFilled } from "@ant-design/icons";
import { ChevronRight } from "lucide-react";
import Link from "next/link";

import { AuroraText } from "~/components/magicui/aurora-text";
import { FlickeringGrid } from "~/components/magicui/flickering-grid";
import { Button } from "~/components/ui/button";
import { env } from "~/env";

export function Jumbotron() {
  return (
    <section className="flex h-[95vh] w-full flex-col items-center justify-center pb-15">
      <FlickeringGrid
        id="deer-hero-bg"
        className={`absolute inset-0 z-0 [mask-image:radial-gradient(800px_circle_at_center,white,transparent)]`}
        squareSize={4}
        gridGap={4}
        color="#60A5FA"
        maxOpacity={0.133}
        flickerChance={0.1}
      />
      <FlickeringGrid
        id="deer-hero"
        className="absolute inset-0 z-0 translate-y-[2vh] mask-[url(/images/deer-hero.svg)] mask-size-[100vw] mask-center mask-no-repeat md:mask-size-[72vh]"
        squareSize={3}
        gridGap={6}
        color="#60A5FA"
        maxOpacity={0.64}
        flickerChance={0.12}
      />
      <div className="relative z-10 flex flex-col items-center justify-center gap-12">
        <h1 className="text-center text-4xl font-bold md:text-6xl">
          <span className="bg-gradient-to-r from-white via-gray-200 to-gray-400 bg-clip-text text-transparent">
            动动手指{" "}
          </span>
          <AuroraText>，深度研究</AuroraText>
        </h1>
        <p className="max-w-4xl p-2 text-center text-sm opacity-85 md:text-2xl">
        认识ResearcherNexus，您的个人深度研究助手。
        它拥有强大的工具，如搜索引擎、网络爬虫、
        Python和MCP服务，能够提供即时洞察、全面报告，甚至引人入胜的播客内容。
        </p>
        <div className="flex gap-6">
          <Button className="hidden text-lg md:flex md:w-42" size="lg" asChild>
            <Link
              target={
                env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY ? "_blank" : undefined
              }
              href={
                env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY
                  ? "https://github.com/wuxixixi/ResearcherNexus"
                  : "/chat"
              }
            >
              开始研究 <ChevronRight />
            </Link>
          </Button>
          {!env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY && (
            <Button
              className="w-42 text-lg"
              size="lg"
              variant="outline"
              asChild
            >
              <Link
                href="https://cd"
                target="_blank"
              >
                <GithubFilled />
                了解更多
              </Link>
            </Button>
          )}
        </div>
      </div>
      <div className="absolute bottom-8 flex text-xs opacity-50">
        <p>* 觉测团队追求的是深度探索与高效研究</p>
      </div>
    </section>
  );
}
