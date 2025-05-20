// Copyright (c) 2025 SASS and/or its affiliates
// SPDX-License-Identifier: MIT

import {
  ArrowDownWideNarrow,
  CheckCheck,
  RefreshCcwDot,
  StepForward,
  WrapText,
} from "lucide-react";
import { getPrevText, useEditor } from "novel";
import { CommandGroup, CommandItem, CommandSeparator } from "../../ui/command";

const options = [
  {
    value: "improve",
    label: "润色",
    icon: RefreshCcwDot,
  },
  // TODO: add this back in
  // {
  //   value: "fix",
  //   label: "Fix grammar",
  //   icon: CheckCheck,
  // },
  {
    value: "shorter",
    label: "缩短一些",
    icon: ArrowDownWideNarrow,
  },
  {
    value: "longer",
    label: "变长一些",
    icon: WrapText,
  },
];

interface AISelectorCommandsProps {
  onSelect: (value: string, option: string) => void;
}

const AISelectorCommands = ({ onSelect }: AISelectorCommandsProps) => {
  const { editor } = useEditor();
  if (!editor) return null;
  return (
    <>
      <CommandGroup heading="编辑或审查选中的内容">
        {options.map((option) => (
          <CommandItem
            onSelect={(value) => {
              const slice = editor.state.selection.content();
              const text = editor.storage.markdown.serializer.serialize(
                slice.content,
              );
              onSelect(text, value);
            }}
            className="flex gap-2 px-4"
            key={option.value}
            value={option.value}
          >
            <option.icon className="h-4 w-4 text-purple-500" />
            {option.label}
          </CommandItem>
        ))}
      </CommandGroup>
      <CommandSeparator />
      <CommandGroup heading="利用AI做更多">
        <CommandItem
          onSelect={() => {
            const pos = editor.state.selection.from;
            const text = getPrevText(editor, pos);
            onSelect(text, "continue");
          }}
          value="continue"
          className="gap-2 px-4"
        >
          <StepForward className="h-4 w-4 text-purple-500" />
          继续写下去
        </CommandItem>
      </CommandGroup>
    </>
  );
};

export default AISelectorCommands;
