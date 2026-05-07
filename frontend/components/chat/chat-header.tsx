"use client";

import { BookOpenIcon, PanelLeftIcon } from "lucide-react";
import { memo } from "react";
import { Button } from "@/components/ui/button";
import { useSidebar } from "@/components/ui/sidebar";
import type { VisibilityType } from "./visibility-selector";

function PureChatHeader({
  isReadonly,
}: {
  chatId: string;
  selectedVisibilityType: VisibilityType;
  isReadonly: boolean;
}) {
  const { state, toggleSidebar, isMobile } = useSidebar();

  if (state === "collapsed" && !isMobile) {
    return null;
  }

  return (
    <header className="sticky top-0 flex h-14 items-center gap-2 bg-sidebar px-3">
      <Button
        className="md:hidden"
        onClick={toggleSidebar}
        size="icon-sm"
        variant="ghost"
      >
        <PanelLeftIcon className="size-4" />
      </Button>

      <div className="flex items-center gap-2 text-sm">
        <div className="flex size-7 items-center justify-center rounded-lg border border-border/40 bg-card/40">
          <BookOpenIcon className="size-4 text-foreground/80" />
        </div>
        <div className="flex flex-col leading-none">
          <span className="font-medium text-foreground">Course Assistant</span>
          <span className="text-[11px] text-muted-foreground">
            CMSC389A course chat
          </span>
        </div>
      </div>

      {isReadonly && (
        <div className="ml-auto text-[11px] text-muted-foreground">
          Read-only
        </div>
      )}
    </header>
  );
}

export const ChatHeader = memo(PureChatHeader, (prevProps, nextProps) => {
  return (
    prevProps.chatId === nextProps.chatId &&
    prevProps.selectedVisibilityType === nextProps.selectedVisibilityType &&
    prevProps.isReadonly === nextProps.isReadonly
  );
});
