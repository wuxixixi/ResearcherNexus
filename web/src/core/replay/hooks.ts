// Copyright (c) 2025 SASS and/or its affiliates
// SPDX-License-Identifier: MIT

import { useSearchParams } from "next/navigation";
import { useMemo } from "react";

import { env } from "~/env";

import { extractReplayIdFromSearchParams } from "./get-replay-id";

export function useReplay() {
  const searchParams = useSearchParams();
  const replayId = useMemo(
    () => extractReplayIdFromSearchParams(searchParams.toString()),
    [searchParams],
  );

  // Memoize the returned object to ensure stable reference if replayId doesn't change
  return useMemo(() => ({
    isReplay: replayId != null || env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY,
    replayId,
  }), [replayId]); // env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY is a build-time constant
}
