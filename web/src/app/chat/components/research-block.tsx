// Copyright (c) 2025 SASS and/or its affiliates
// SPDX-License-Identifier: MIT

import { Check, Copy, Headphones, Pencil, Undo2, X, DownloadCloud } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import { ScrollContainer } from "~/components/researchernexus/scroll-container";
import { Tooltip } from "~/components/researchernexus/tooltip";
import { Button } from "~/components/ui/button";
import { Card } from "~/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "~/components/ui/tabs";
import { useReplay } from "~/core/replay";
import { closeResearch, listenToPodcast, useStore } from "~/core/store";
import { cn } from "~/lib/utils";
import { downloadContentAsMarkdown, downloadMessagesAsMarkdown } from "~/lib/download";
import type { Message } from "~/core/messages";

import { ResearchActivitiesBlock } from "./research-activities-block";
import { ResearchReportBlock } from "./research-report-block";

export function ResearchBlock({
  className,
  researchId = null,
}: {
  className?: string;
  researchId: string | null;
}) {
  const reportId = useStore((state) =>
    researchId ? state.researchReportIds.get(researchId) : undefined,
  );
  const [activeTab, setActiveTab] = useState("activities");
  const hasReport = useStore((state) =>
    researchId ? state.researchReportIds.has(researchId) : false,
  );
  const reportStreaming = useStore((state) =>
    reportId ? (state.messages.get(reportId)?.isStreaming ?? false) : false,
  );
  const { isReplay } = useReplay();
  useEffect(() => {
    if (hasReport) {
      setActiveTab("report");
    }
  }, [hasReport]);

  // Restore original getResearchTopic logic
  const getResearchTopic = useCallback(() => {
    if (!researchId) return undefined;
    const researchInitialMessage = useStore.getState().messages.get(researchId);
    // Use the first ~100 chars of content, or a default if not available
    return researchInitialMessage?.content?.substring(0, 100) || "Research";
  }, [researchId]);

  const handleGeneratePodcast = useCallback(async () => {
    if (!researchId) {
      return;
    }
    await listenToPodcast(researchId);
  }, [researchId]);

  const [editing, setEditing] = useState(false);
  const [copied, setCopied] = useState(false);
  const handleCopy = useCallback(() => {
    if (!reportId) {
      return;
    }
    const report = useStore.getState().messages.get(reportId);
    if (!report) {
      return;
    }
    void navigator.clipboard.writeText(report.content);
    setCopied(true);
    setTimeout(() => {
      setCopied(false);
    }, 1000);
  }, [reportId]);

  const handleDownloadReport = useCallback(() => {
    if (!reportId) {
      return;
    }
    const reportMessage = useStore.getState().messages.get(reportId);
    if (!reportMessage || !reportMessage.content) {
      console.warn("No report content to download.");
      return;
    }
    const topic = getResearchTopic();
    downloadContentAsMarkdown(reportMessage.content, "报告区导出", topic);
  }, [reportId, getResearchTopic]);

  const handleDownloadActivities = useCallback(() => {
    if (!researchId) return;

    const state = useStore.getState();
    const activityIds = state.researchActivityIds.get(researchId);

    if (!activityIds || activityIds.length === 0) {
      console.warn("No activities to download for this research.");
      return;
    }

    const activityMessages = activityIds
      .map(id => state.messages.get(id))
      .filter((msg): msg is Message => !!msg);

    if (activityMessages.length > 0) {
      const topic = getResearchTopic();
      downloadMessagesAsMarkdown(activityMessages, "研究活动区导出", topic);
    } else {
      console.warn("No message content found for activities to download.");
    }
  }, [researchId, getResearchTopic]);

  const handleEdit = useCallback(() => {
    setEditing((editing) => !editing);
  }, []);

  // When the research id changes, set the active tab to activities
  useEffect(() => {
    if (!hasReport) {
      setActiveTab("activities");
    }
  }, [hasReport, researchId]);

  return (
    <div className={cn("h-full w-full", className)}>
      <Card className={cn("relative h-full w-full pt-4", className)}>
        <div className="absolute right-4 flex h-9 items-center justify-center">
          {hasReport && !reportStreaming && (
            <>
              <Tooltip title="生成播客">
                <Button
                  className="text-gray-400"
                  size="icon"
                  variant="ghost"
                  disabled={isReplay}
                  onClick={handleGeneratePodcast}
                >
                  <Headphones />
                </Button>
              </Tooltip>
              <Tooltip title="下载报告 (Markdown)">
                <Button
                  className="text-gray-400"
                  size="icon"
                  variant="ghost"
                  onClick={handleDownloadReport}
                >
                  <DownloadCloud />
                </Button>
              </Tooltip>
              <Tooltip title="编辑">
                <Button
                  className="text-gray-400"
                  size="icon"
                  variant="ghost"
                  disabled={isReplay}
                  onClick={handleEdit}
                >
                  {editing ? <Undo2 /> : <Pencil />}
                </Button>
              </Tooltip>
              <Tooltip title="复制">
                <Button
                  className="text-gray-400"
                  size="icon"
                  variant="ghost"
                  onClick={handleCopy}
                >
                  {copied ? <Check /> : <Copy />}
                </Button>
              </Tooltip>
            </>
          )}
          <Tooltip title="关闭">
            <Button
              className="text-gray-400"
              size="sm"
              variant="ghost"
              onClick={() => {
                closeResearch();
              }}
            >
              <X />
            </Button>
          </Tooltip>
        </div>
        <Tabs
          className="flex h-full w-full flex-col"
          value={activeTab}
          onValueChange={(value) => setActiveTab(value)}
        >
          <div className="flex w-full justify-center">
            <TabsList className="">
              <TabsTrigger
                className="px-8"
                value="report"
                disabled={!hasReport}
              >
                报告区（可编辑）
              </TabsTrigger>
              <TabsTrigger className="px-8" value="activities">
                研究活动区
              </TabsTrigger>
            </TabsList>
          </div>
          <TabsContent
            className="h-full min-h-0 flex-grow px-8"
            value="report"
            forceMount
            hidden={activeTab !== "report"}
          >
            <ScrollContainer
              className="px-5pb-20 h-full"
              scrollShadowColor="var(--card)"
              autoScrollToBottom={!hasReport || reportStreaming}
            >
              {reportId && researchId && (
                <ResearchReportBlock
                  className="mt-4"
                  researchId={researchId}
                  messageId={reportId}
                  editing={editing}
                />
              )}
            </ScrollContainer>
          </TabsContent>
          <TabsContent
            className="h-full min-h-0 flex-grow px-8"
            value="activities"
            forceMount
            hidden={activeTab !== "activities"}
          >
            {researchId && (
              <div className="flex items-center justify-between p-2 border-b sticky top-0 bg-card z-10">
                <h3 className="text-md font-semibold">研究活动记录</h3>
                <Tooltip title="Download Activities Log (Markdown)">
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={handleDownloadActivities}
                  >
                    <DownloadCloud size={16} />
                  </Button>
                </Tooltip>
              </div>
            )}
            <ScrollContainer
              className="h-full"
              scrollShadowColor="var(--card)"
              autoScrollToBottom={!hasReport || reportStreaming}
            >
              {researchId && (
                <ResearchActivitiesBlock
                  className="mt-4"
                  researchId={researchId}
                />
              )}
            </ScrollContainer>
          </TabsContent>
        </Tabs>
      </Card>
    </div>
  );
}
