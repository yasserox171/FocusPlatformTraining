import LangBadge from "./LangBadge";
import type { Paragraph } from "@/lib/types";

function youtubeEmbedUrl(url: string): string {
  const match = url.match(
    /(?:youtube\.com\/(?:watch\?v=|embed\/)|youtu\.be\/)([\w-]{11})/
  );
  return match ? `https://www.youtube.com/embed/${match[1]}` : url;
}

export default function VideoBlock({ paragraph }: { paragraph: Paragraph }) {
  if (!paragraph.video_url) return null;
  return (
    <div className="relative rounded-xl bg-white p-4 shadow-sm">
      <LangBadge lang={paragraph.lang_hint} />
      <div className="aspect-video overflow-hidden rounded-lg bg-dark">
        {paragraph.video_type === "youtube" ? (
          <iframe
            className="h-full w-full"
            src={youtubeEmbedUrl(paragraph.video_url)}
            title="Video"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        ) : (
          <video className="h-full w-full" src={paragraph.video_url} controls />
        )}
      </div>
    </div>
  );
}
