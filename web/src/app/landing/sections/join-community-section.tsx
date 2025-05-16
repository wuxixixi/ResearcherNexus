// Copyright (c) 2025 SASS and/or its affiliates
// SPDX-License-Identifier: MIT

import { GithubFilled } from "@ant-design/icons";
import Link from "next/link";

import { AuroraText } from "~/components/magicui/aurora-text";
import { Button } from "~/components/ui/button";

import { SectionHeader } from "../components/section-header";

export function JoinCommunitySection() {
  return (
    <section className="flex w-full flex-col items-center justify-center pb-12">
      <SectionHeader
        anchor="join-community"
        title={
          <AuroraText colors={["#60A5FA", "#A5FA60", "#A560FA"]}>
            加入ResearcherNexus社区
          </AuroraText>
        }
        description="为塑造ResearcherNexus的未来贡献卓越的想法。合作、创新并产生影响。"
      />
      <Button className="text-xl" size="lg" asChild>
        <Link href="https://github.com/wuxixixi/ResearcherNexus" target="_blank">
          <GithubFilled />
          立即贡献
        </Link>
      </Button>
    </section>
  );
}
