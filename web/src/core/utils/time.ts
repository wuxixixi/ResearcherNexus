// Copyright (c) 2025 SASS and/or its affiliates
// SPDX-License-Identifier: MIT

export function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
