import Link from 'next/link';

interface ChapterNavigationProps {
  locale: string;
  bookName: string;
  currentChapter: number;
  totalChapters: number;
  className?: string;
}

export default function ChapterNavigation({
  locale,
  bookName,
  currentChapter,
  totalChapters,
  className = "mb-8 flex gap-4 justify-center"
}: ChapterNavigationProps) {
  return (
    <div className={className}>
      {currentChapter > 1 && (
        <Link
          href={`/${locale}/book/${bookName}/chapter/${currentChapter - 1}`}
          className="px-4 py-2 text-sm font-ui-latin border border-gray/20 rounded hover:bg-background transition-colors"
        >
          ← Previous Chapter
        </Link>
      )}
      {currentChapter < totalChapters && (
        <Link
          href={`/${locale}/book/${bookName}/chapter/${currentChapter + 1}`}
          className="px-4 py-2 text-sm font-ui-latin border border-gray/20 rounded hover:bg-background transition-colors"
        >
          Next Chapter →
        </Link>
      )}
    </div>
  );
}
