// Copyright (c) 2025 SASS and/or its affiliates
// SPDX-License-Identifier: MIT

import { motion } from "framer-motion";
import { FastForward, Play, AlertCircle } from "lucide-react";
import { useCallback, useRef, useState, useEffect } from "react";
import { useRouter } from "next/navigation";

import { RainbowText } from "~/components/ResearcherNexus/rainbow-text";
import { Button } from "~/components/ui/button";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "~/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "~/components/ui/dialog";
import { fastForwardReplay } from "~/core/api";
import { useReplayMetadata } from "~/core/api/hooks";
import type { Option } from "~/core/messages";
import { useReplay } from "~/core/replay";
import { sendMessage, useStore } from "~/core/store";
import { env } from "~/env";
import { cn } from "~/lib/utils";
import { useAuth } from "~/lib/auth-context";

import { ConversationStarter } from "./conversation-starter";
import { InputBox } from "./input-box";
import { MessageListView } from "./message-list-view";
import { Welcome } from "./welcome";

export function MessagesBlock({ className }: { className?: string }) {
  const { isAuthenticated, incrementUsage, getRemainingUsage, user } = useAuth();
  const router = useRouter();
  const messageCount = useStore((state) => state.messageIds.length);
  const responding = useStore((state) => state.responding);
  const { isReplay } = useReplay();
  const { title: replayTitle, hasError: replayHasError } = useReplayMetadata();
  const [replayStarted, setReplayStarted] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);
  const [feedback, setFeedback] = useState<{ option: Option } | null>(null);
  const [usageLimitReached, setUsageLimitReached] = useState(false);
  const [usageData, setUsageData] = useState({ used: 0, limit: 0, remaining: 0 });
  
  // 当用户未登录时，将其重定向到登录页
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);
  
  // 获取用户使用情况
  useEffect(() => {
    if (isAuthenticated && user) {
      const fetchUsageData = async () => {
        const data = await getRemainingUsage();
        setUsageData(data);
      };
      fetchUsageData();
    }
  }, [isAuthenticated, user, getRemainingUsage]);

  // 发送消息前检查用户使用限制
  const checkUsageLimitBeforeSend = useCallback(async () => {
    if (!isAuthenticated) {
      router.push('/login');
      return false;
    }
    
    const result = await incrementUsage();
    if (!result.success) {
      setUsageLimitReached(true);
      return false;
    }
    
    // 更新用户使用情况
    const data = await getRemainingUsage();
    setUsageData(data);
    return true;
  }, [isAuthenticated, incrementUsage, getRemainingUsage, router]);
  
  const handleSend = useCallback(
    async (message: string, options?: { interruptFeedback?: string }) => {
      // 在发送消息前检查用户使用限制
      if (!isReplay && !await checkUsageLimitBeforeSend()) {
        return;
      }
      
      const abortController = new AbortController();
      abortControllerRef.current = abortController;
      try {
        await sendMessage(
          message,
          {
            interruptFeedback:
              options?.interruptFeedback ?? feedback?.option.value,
          },
          {
            abortSignal: abortController.signal,
          },
        );
      } catch {}
    },
    [feedback, checkUsageLimitBeforeSend, isReplay],
  );
  const handleCancel = useCallback(() => {
    abortControllerRef.current?.abort();
    abortControllerRef.current = null;
  }, []);
  const handleFeedback = useCallback(
    (feedback: { option: Option }) => {
      setFeedback(feedback);
    },
    [setFeedback],
  );
  const handleRemoveFeedback = useCallback(() => {
    setFeedback(null);
  }, [setFeedback]);
  const handleStartReplay = useCallback(() => {
    setReplayStarted(true);
    void sendMessage();
  }, [setReplayStarted]);
  const [fastForwarding, setFastForwarding] = useState(false);
  const handleFastForwardReplay = useCallback(() => {
    setFastForwarding(!fastForwarding);
    fastForwardReplay(!fastForwarding);
  }, [fastForwarding]);
  
  // 关闭使用限制提示对话框
  const closeUsageLimitDialog = useCallback(() => {
    setUsageLimitReached(false);
  }, []);

  // 如果未登录，应该返回空内容或加载中状态
  if (!isAuthenticated) {
    return <div className="flex h-full items-center justify-center">正在检查认证状态...</div>;
  }
  
  return (
    <div className={cn("flex h-full flex-col", className)}>
      <MessageListView
        className="flex flex-grow"
        onFeedback={handleFeedback}
        onSendMessage={handleSend}
      />
      {!isReplay ? (
        <div className="relative flex h-42 shrink-0 pb-4">
          {!responding && messageCount === 0 && (
            <ConversationStarter
              className="absolute top-[-218px] left-0"
              onSend={handleSend}
            />
          )}
          <InputBox
            className="h-full w-full"
            responding={responding}
            feedback={feedback}
            onSend={handleSend}
            onCancel={handleCancel}
            onRemoveFeedback={handleRemoveFeedback}
          />
          {/* 显示用户使用情况 */}
          {isAuthenticated && user && !user.role.includes('admin') && (
            <div className="absolute right-2 top-[-30px] text-xs text-muted-foreground">
              今日使用次数: {usageData.used}/{usageData.limit}
            </div>
          )}
        </div>
      ) : (
        <>
          <div
            className={cn(
              "fixed bottom-[calc(50vh+80px)] left-0 transition-all duration-500 ease-out",
              replayStarted && "pointer-events-none scale-150 opacity-0",
            )}
          >
            <Welcome />
          </div>
          <motion.div
            className="mb-4 h-fit w-full items-center justify-center"
            initial={{ opacity: 0, y: "20vh" }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Card
              className={cn(
                "w-full transition-all duration-300",
                !replayStarted && "translate-y-[-40vh]",
              )}
            >
              <div className="flex items-center justify-between">
                <div className="flex-grow">
                  <CardHeader>
                    <CardTitle>
                      <RainbowText animated={responding}>
                        {responding ? "Replaying" : `${replayTitle}`}
                      </RainbowText>
                    </CardTitle>
                    <CardDescription>
                      <RainbowText animated={responding}>
                        {responding
                          ? "ResearcherNexus is now replaying the conversation..."
                          : replayStarted
                            ? "The replay has been stopped."
                            : `You're now in ResearcherNexus's replay mode. Click the "Play" button on the right to start.`}
                      </RainbowText>
                    </CardDescription>
                  </CardHeader>
                </div>
                {!replayHasError && (
                  <div className="pr-4">
                    {responding && (
                      <Button
                        className={cn(fastForwarding && "animate-pulse")}
                        variant={fastForwarding ? "default" : "outline"}
                        onClick={handleFastForwardReplay}
                      >
                        <FastForward size={16} />
                        Fast Forward
                      </Button>
                    )}
                    {!replayStarted && (
                      <Button className="w-24" onClick={handleStartReplay}>
                        <Play size={16} />
                        Play
                      </Button>
                    )}
                  </div>
                )}
              </div>
            </Card>
            {!replayStarted && env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY && (
              <div className="text-muted-foreground w-full text-center text-xs">
                * This site is for demo purposes only. If you want to try your
                own question, please{" "}
                <a
                  className="underline"
                  href="https://github.com/wuxixixi/ResearcherNexus"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  click here
                </a>{" "}
                to clone it locally and run it.
              </div>
            )}
          </motion.div>
        </>
      )}
      
      {/* 使用限制对话框 */}
      <Dialog open={usageLimitReached} onOpenChange={setUsageLimitReached}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-yellow-500" />
              使用次数已达上限
            </DialogTitle>
            <DialogDescription>
              您今天的使用次数已达到{usageData.limit}次限制。请明天再试或联系管理员（wuxi@sass.org.cn）增加配额。
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={closeUsageLimitDialog}>
              知道了
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
