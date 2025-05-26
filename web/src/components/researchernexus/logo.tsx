// Copyright (c) 2025 SASS and/or its affiliates
// SPDX-License-Identifier: MIT

import Link from "next/link";
import { cn } from "~/lib/utils";

interface LogoProps {
  className?: string;
}

export function Logo({ className }: LogoProps = {}) {
  return (
    <Link
      className={cn(
        "opacity-70 transition-opacity duration-300 hover:opacity-100",
        className
      )}
      href="/"
    >
      🔍 ResearcherNexus
    </Link>
  );
}
