// Copyright (c) 2025 SASS and/or its affiliates
// SPDX-License-Identifier: MIT

import { BadgeInfo } from "lucide-react";

import { Markdown } from "~/components/deer-flow/markdown";

import about from "./about.md";
import type { Tab } from "./types";

export const AboutTab: Tab = () => {
  return <Markdown>{about}</Markdown>;
};
AboutTab.icon = BadgeInfo;
