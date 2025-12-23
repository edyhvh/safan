'use client';

import { Chapter } from '@/lib/types';
import { useState } from 'react';
import VersesDropdown from './VersesDropdown';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { getLocaleFromPath } from '@/lib/locale';

interface ChaptersDropdownProps {
  chapters: Chapter[];
  bookName: string;
  isOpen: boolean;
  onClose: () => void;
  onCloseAll?: () => void;
}

export default function ChaptersDropdown({
  chapters,
  bookName,
  isOpen,
  onClose,
  onCloseAll,
}: ChaptersDropdownProps) {
  const [hoveredChapter, setHoveredChapter] = useState<number | null>(null);
  const pathname = usePathname();
  const locale = getLocaleFromPath(pathname);

  if (!isOpen) return null;

  const chapter = hoveredChapter ? chapters.find(c => c.number === hoveredChapter) : null;

  // If no chapters, show message
  if (!chapters || chapters.length === 0) {
    return (
      <div className="dropdown-panel z-[60] p-4">
        <span className="text-sm text-black/60">No chapters</span>
      </div>
    );
  }

  // Calculate grid columns based on number of chapters
  const gridCols = chapters.length === 1 ? 1 : chapters.length <= 4 ? 2 : chapters.length <= 9 ? 3 : chapters.length <= 16 ? 4 : 5;

  return (
    <div
      className="relative dropdown-panel z-[60] p-3"
    >
      {/* Grid of chapters */}
      <div
        className="grid gap-2"
        style={{ gridTemplateColumns: `repeat(${gridCols}, 1fr)` }}
      >
        {chapters.map((ch) => {
          const isHovered = hoveredChapter === ch.number;

          return (
            <Link
              key={ch.number}
              href={`/${locale}/book/${bookName}/chapter/${ch.number}`}
              className={`flex items-center justify-center w-10 h-10 text-sm font-semibold text-black transition-colors rounded-lg ${
                isHovered ? 'bg-black/15' : 'bg-black/5 hover:bg-black/10'
              } ${locale === 'he' ? 'font-ui-hebrew' : 'font-ui-latin'}`}
              onMouseEnter={() => setHoveredChapter(ch.number)}
              onClick={() => {
                onClose();
                onCloseAll?.();
              }}
            >
              {locale === 'he' ? ch.hebrew_letter : ch.number}
            </Link>
          );
        })}
      </div>

      {/* Verses dropdown - positioned outside the scrollable area */}
      {chapter && chapter.verses.length > 0 && (
        <div
          className="absolute left-full top-0 pl-2 z-[70]"
          onMouseEnter={() => setHoveredChapter(chapter.number)}
        >
          <VersesDropdown
            verses={chapter.verses}
            bookName={bookName}
            chapterNumber={chapter.number}
            isOpen={true}
            onClose={() => setHoveredChapter(null)}
            onCloseAll={() => {
              onClose();
              onCloseAll?.();
            }}
          />
        </div>
      )}
    </div>
  );
}
