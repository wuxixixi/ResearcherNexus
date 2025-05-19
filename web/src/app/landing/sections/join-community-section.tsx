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
        description="贡献卓越的想法，塑造研究员联结（ResearcherNexus）的未来。携手合作、创新并创造影响力。"
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
