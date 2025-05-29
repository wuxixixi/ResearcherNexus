// Copyright (c) 2025 SASS and/or its affiliates
// SPDX-License-Identifier: MIT

import { PythonOutlined } from "@ant-design/icons";
import { motion } from "framer-motion";
import { BookOpenText, PencilRuler, Search } from "lucide-react";
import { useTheme } from "next-themes";
import { useMemo } from "react";
import SyntaxHighlighter from "react-syntax-highlighter";
import { docco } from "react-syntax-highlighter/dist/esm/styles/hljs";
import { dark } from "react-syntax-highlighter/dist/esm/styles/prism";

import { FavIcon } from "~/components/researchernexus/fav-icon";
import Image from "~/components/researchernexus/image";
import { LoadingAnimation } from "~/components/researchernexus/loading-animation";
import { Markdown } from "~/components/researchernexus/markdown";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "~/components/ui/accordion";
import { findMCPTool } from "~/core/mcp";
import type { ToolCallRuntime } from "~/core/messages";
import { useStore, useMessage } from "~/core/store";
import { cn } from "~/lib/utils";

export function ResearchActivitiesBlock({
  className,
  researchId,
}: {
  className?: string;
  researchId: string;
}) {
  console.log("[ResearchActivitiesBlock] Rendering with researchId:", researchId);

  const activityIds = useStore((state) => {
    // console.log("[ResearchActivitiesBlock] useStore selector for activityIds running. researchId:", researchId);
    return state.researchActivityIds.get(researchId);
  });

  const ongoing = useStore((state) => {
    // console.log("[ResearchActivitiesBlock] useStore selector for ongoing running. researchId:", researchId, "state.ongoingResearchId:", state.ongoingResearchId);
    return state.ongoingResearchId === researchId;
  });

  // console.log("[ResearchActivitiesBlock] activityIds:", activityIds);
  // console.log("[ResearchActivitiesBlock] ongoing:", ongoing);

  if (!researchId) {
    console.warn("[ResearchActivitiesBlock] No researchId provided.");
    return <div className={cn("p-4 text-red-500", className)}>错误: 未提供研究ID。</div>;
  }

  if (!activityIds) {
    console.warn("[ResearchActivitiesBlock] No activityIds found for researchId:", researchId);
    // Still render the basic block structure but indicate no activities
    return (
      <div className={cn("p-4", className)}>
        <p>研究活动区 (Research Activities Block)</p>
        <p>当前研究 ID (Research ID): {researchId}</p>
        <p>活动 IDs (Activity IDs): 无活动 (No activities found)</p>
        <p>是否进行中 (Ongoing): {String(ongoing)}</p>
        <p>（内容仍为调试简化版，仅测试状态获取）</p>
        {/* {ongoing && <LoadingAnimation className="mx-4 my-12" />} */} 
      </div>
    );
  }
  
  // Restore list rendering structure, but with simple placeholders for items
  return (
    <>
      <ul className={cn("flex flex-col py-4", className)}>
        {activityIds.map(
          (activityId, _i) =>
            // We will re-introduce the i !== 0 condition later if needed
            // For now, let's render all items to see if mapping is the issue.
            <motion.li
              key={activityId}
              style={{ transition: "all 0.4s ease-out" }}
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{
                duration: 0.4,
                ease: "easeOut",
              }}
              className="my-2 p-2 border rounded"
            >
              {/* <p>活动项占位符 (Activity Item Placeholder)</p>
              <p>ID: {activityId}</p> */}
              <ActivityMessage messageId={activityId} />
              <ActivityListItem messageId={activityId} />
              {/* {i !== activityIds.length - 1 && <hr className="my-8" />} */}
            </motion.li>
        )}
      </ul>
      {/* {ongoing && <LoadingAnimation className="mx-4 my-12" />} */} 
    </>
  );

}

// ... (Rest of the original file content, like ActivityMessage, ActivityListItem, etc., 
// can remain commented out or be temporarily removed if they cause import errors 
// due to their own dependencies being commented out above)
// For now, I will assume they are effectively removed by commenting out their usage in the return.

function ActivityMessage({ messageId }: { messageId: string }) {
  const message = useMessage(messageId);
  if (message?.agent && message.content) {
    if (message.agent !== "reporter" && message.agent !== "planner") {
      return (
        <div className="px-4 py-2">
          <Markdown animated checkLinkCredibility>
            {message.content}
          </Markdown>
        </div>
      );
    }
  }
  return null;
}

// /*
function ActivityListItem({ messageId }: { messageId: string }) {
  const message = useMessage(messageId);
  if (message) {
    if (!message.isStreaming && message.toolCalls?.length) {
      for (const toolCall of message.toolCalls) {
        if (toolCall.name === "web_search") {
          return <WebSearchToolCall key={toolCall.id} toolCall={toolCall} message={message} />;
        } else if (toolCall.name === "crawl_tool") {
          return <CrawlToolCall key={toolCall.id} toolCall={toolCall} message={message} />;
        } else if (toolCall.name === "python_repl_tool") {
          return <PythonToolCall key={toolCall.id} toolCall={toolCall} message={message} />;
        } else {
          return <MCPToolCall key={toolCall.id} toolCall={toolCall} message={message} />;
        }
      }
    }
  }
  return null;
}

// ... other helper components like WebSearchToolCall, CrawlToolCall etc. would also be here ...
// Define these components here for now. They might need to be moved to separate files later.

// const previstoHostCache = new LRUCache<string, string>({ max: 100 });

function WebSearchToolCall({ toolCall, message }: { toolCall: ToolCallRuntime, message: { isStreaming?: boolean } }) {
  const args = toolCall.args as { query: string };
  const result = toolCall.result as unknown as
    | { query: string; results: { title: string; url: string }[] }
    | undefined;
  const { resolvedTheme } = useTheme();
  const borderColor = resolvedTheme === "dark" ? "#444" : "#ddd";

  return (
    <div className="group/tool-call relative my-4 flex flex-col gap-2 rounded-lg border p-4" style={{ borderColor }}>
      <div className="flex items-center gap-2">
        <Search size={18} />
        <span className="font-semibold">Web Search:</span>
        <span>{args.query}</span>
      </div>
      {message.isStreaming && !result && (
        <div className="flex items-center gap-2">
          <LoadingAnimation />
          <span>Searching...</span>
        </div>
      )}
      {result && Array.isArray(result.results) && (
        <ul className="ml-6 flex flex-col gap-2">
          {result.results.map((item, index) => (
            <li key={index} className="flex items-center gap-2">
              <FavIcon url={item.url} title={item.title} />
              <a href={item.url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                {item.title}
              </a>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function CrawlToolCall({ toolCall, message }: { toolCall: ToolCallRuntime, message: { isStreaming?: boolean } }) {
  const args = toolCall.args;
  const result = toolCall.result;
  const { resolvedTheme } = useTheme();
  const borderColor = resolvedTheme === "dark" ? "#444" : "#ddd";

  return (
    <div className="group/tool-call relative my-4 flex flex-col gap-2 rounded-lg border p-4" style={{ borderColor }}>
      <div className="flex items-center gap-2">
        <BookOpenText size={18} />
        <span className="font-semibold">Crawling URL:</span>
        <a href={args.url as string} target="_blank" rel="noopener noreferrer" className="hover:underline">
          {args.url as string}
        </a>
      </div>
      {message.isStreaming && !result && (
        <div className="flex items-center gap-2">
          <LoadingAnimation />
          <span>Crawling...</span>
        </div>
      )}
      {result && (
        <Accordion type="single" collapsible className="w-full">
          <AccordionItem value="item-1">
            <AccordionTrigger>View Content (first 500 chars)</AccordionTrigger>
            <AccordionContent>
              <pre className="whitespace-pre-wrap text-sm">{result.substring(0, 500)}...</pre>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      )}
    </div>
  );
}

function PythonToolCall({ toolCall, message }: { toolCall: ToolCallRuntime, message: { isStreaming?: boolean } }) {
  const args = toolCall.args;
  const result = toolCall.result as { result?: string; image?: string; error?: string } | undefined;
  const { resolvedTheme } = useTheme();
  const syntaxTheme = resolvedTheme === "dark" ? dark : docco;
  const borderColor = resolvedTheme === "dark" ? "#444" : "#ddd";

  return (
    <div className="group/tool-call relative my-4 flex flex-col gap-2 rounded-lg border p-4" style={{ borderColor }}>
      <div className="flex items-center gap-2">
        <PythonOutlined style={{ fontSize: "18px" }} />
        <span className="font-semibold">Python REPL</span>
      </div>
      <SyntaxHighlighter language="python" style={syntaxTheme} customStyle={{ borderRadius: "6px" }}>
        {args.code as string}
      </SyntaxHighlighter>
      {message.isStreaming && !result && (
        <div className="flex items-center gap-2">
          <LoadingAnimation />
          <span>Executing...</span>
        </div>
      )}
      {result?.result && (
        <Accordion type="single" collapsible className="w-full">
          <AccordionItem value="item-1">
            <AccordionTrigger>View Output</AccordionTrigger>
            <AccordionContent>
              <pre className="whitespace-pre-wrap text-sm">{result.result}</pre>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      )}
      {result?.image && (
        <div>
          <Image src={`data:image/png;base64,${result.image}`} alt="Python REPL generated image" />
        </div>
      )}
      {result?.error && (
        <div className="text-red-500">
          <span className="font-semibold">Error:</span> {result.error}
        </div>
      )}
    </div>
  );
}

function MCPToolCall({ toolCall, message }: { toolCall: ToolCallRuntime, message: { isStreaming?: boolean } }) {
  const { args, result, name: toolName } = toolCall;
  const { resolvedTheme } = useTheme();
  const borderColor = resolvedTheme === "dark" ? "#444" : "#ddd";
  const mcpTool = useMemo(() => findMCPTool(toolName), [toolName]);

  return (
    <div className="group/tool-call relative my-4 flex flex-col gap-2 rounded-lg border p-4" style={{ borderColor }}>
      <div className="flex items-center gap-2">
        <PencilRuler size={18} />
        <span className="font-semibold">
          {mcpTool?.name ?? toolName}
        </span>
      </div>
      {args && Object.keys(args).length > 0 && (
        <Accordion type="single" collapsible className="w-full">
          <AccordionItem value="item-args">
            <AccordionTrigger>View Arguments</AccordionTrigger>
            <AccordionContent>
              <pre className="whitespace-pre-wrap text-sm">
                {JSON.stringify(args, null, 2)}
              </pre>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      )}
      {message.isStreaming && !result && (
        <div className="flex items-center gap-2">
          <LoadingAnimation />
          <span>Processing...</span>
        </div>
      )}
      {result && (
        <Accordion type="single" collapsible className="w-full">
          <AccordionItem value="item-result">
            <AccordionTrigger>View Result</AccordionTrigger>
            <AccordionContent>
              <pre className="whitespace-pre-wrap text-sm">
                {typeof result === "string" ? result : JSON.stringify(result, null, 2)}
              </pre>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      )}
    </div>
  );
}
// */
