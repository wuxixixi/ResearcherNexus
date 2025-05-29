// Copyright (c) 2025 SASS and/or its affiliates
// SPDX-License-Identifier: MIT

import { useEffect, useMemo, useRef, useState } from "react";

import { useReplay } from "../replay";

import { fetchReplayTitle } from "./chat";

export function useReplayMetadata() {
  const { isReplay } = useReplay();
  const [title, setTitle] = useState<string | null>(null);
  const isLoadingRef = useRef(false);
  const [error, setError] = useState<boolean>(false);
  
  useEffect(() => {
    if (!isReplay) {
      setTitle(null);
      setError(false);
      return;
    }
    if (!title && !isLoadingRef.current) {
      isLoadingRef.current = true;
      fetchReplayTitle()
        .then((fetchedTitle) => {
          setError(false);
          setTitle(fetchedTitle ?? null);
          if (fetchedTitle) {
            document.title = `${fetchedTitle} - ResearcherNexus`;
          }
        })
        .catch(() => {
          setError(true);
          setTitle("Error: the replay is not available.");
          document.title = "ResearcherNexus";
        })
        .finally(() => {
          isLoadingRef.current = false;
        });
    }
  }, [isReplay, title]);

  return useMemo(() => ({
    title,
    isLoading: isLoadingRef.current,
    hasError: error,
  }), [title, error]);
}
