// Copyright (c) 2025 SASS and/or its affiliates
// SPDX-License-Identifier: MIT

// Import the actual Message and MessageRole types from the store
import type { Message, MessageRole } from "../core/messages/types";

// The Message interface here is now for reference or if we need to extend/adapt
// but downloadMessagesAsMarkdown will use the imported Message type directly.

function sanitizeFilename(name: string): string {
  // Remove characters that are not allowed in filenames on most OSes
  // and replace spaces with underscores, limit length.
  const sanitized = name.replace(/[<>:"\/\\|?*\s]+/g, '_').replace(/_+/g, '_');
  return sanitized.substring(0, 50); // Limit length to avoid overly long filenames
}

export function downloadMessagesAsMarkdown(messages: Message[], exportTypeDescriptor: string, topic?: string) {
  const safeTopic = topic ? sanitizeFilename(topic) : "";
  const filenameBase = safeTopic ? `${safeTopic} - ${exportTypeDescriptor}` : exportTypeDescriptor;
  const fileName = `${filenameBase}.md`;
  
  const titleInContent = topic ? `${topic} - ${exportTypeDescriptor}` : exportTypeDescriptor;
  let markdownContent = `# ${titleInContent}\n\n`;

  messages.forEach(message => {
    markdownContent += `## ${message.role.toUpperCase()}\n`;
    markdownContent += `${message.content}\n\n`;
  });

  const blob = new Blob([markdownContent], { type: 'text/markdown;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = fileName;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

// We might need a similar function for the report block if its data structure is different.
// For now, assuming the report block also provides an array of message-like objects.
// If not, we will create a separate function e.g., downloadReportAsMarkdown 

export function downloadContentAsMarkdown(content: string, exportTypeDescriptor: string, topic?: string) {
  const safeTopic = topic ? sanitizeFilename(topic) : "";
  const filenameBase = safeTopic ? `${safeTopic} - ${exportTypeDescriptor}` : exportTypeDescriptor;
  const fileName = `${filenameBase}.md`;

  const titleInContent = topic ? `${topic} - ${exportTypeDescriptor}` : exportTypeDescriptor;
  let markdownContent = `# ${titleInContent}\n\n`;
  markdownContent += content;

  const blob = new Blob([markdownContent], { type: 'text/markdown;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = fileName;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
} 