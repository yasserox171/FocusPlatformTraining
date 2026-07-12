import LangBadge from "./LangBadge";
import type { Paragraph } from "@/lib/types";

export default function TextEditorBlock({ paragraph }: { paragraph: Paragraph }) {
  return (
    <div className="relative rounded-xl bg-white p-6 shadow-sm">
      <LangBadge lang={paragraph.lang_hint} />
      <div
        dir="auto"
        className="content-html leading-relaxed"
        dangerouslySetInnerHTML={{ __html: paragraph.content_html ?? "" }}
      />
    </div>
  );
}
