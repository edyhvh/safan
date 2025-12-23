'use client';

import { useState, useRef } from 'react';
import Link from 'next/link';
import { Chapter } from '@/lib/types';
import { useClickOutside } from '@/hooks/useClickOutside';
import { ChevronDown } from '@/components/icons';

interface ChapterTitleSelectorProps {
  bookDisplayName: string;
  currentChapter: number;
  hebrewLetter?: string;
  chapters: { number: number; hebrew_letter: string }[];
  bookName: string;
  locale: string;
}

export default function ChapterTitleSelector({
  bookDisplayName,
  currentChapter,
  hebrewLetter,
  chapters,
  bookName,
  locale,
}: ChapterTitleSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useClickOutside(dropdownRef, () => setIsOpen(false), isOpen);

  return (
    <div className="text-center mb-8 pt-12">
      <h1 className="font-ui-latin text-lg text-black mb-1 inline-flex items-center gap-2">
        <span className="font-semibold">{bookDisplayName}</span>

        {/* Chapter selector with click dropdown */}
        <div className="relative inline-block" ref={dropdownRef}>
          <button
            onClick={() => setIsOpen(!isOpen)}
            className={`
              min-w-[36px] h-[36px] px-2
              flex items-center justify-center
              font-semibold text-base
              bg-black/5 hover:bg-black/10
              border border-black/10 hover:border-black/20
              rounded-lg
              cursor-pointer
              transition-all duration-200
              ${isOpen ? 'bg-black/10 border-black/20 shadow-sm' : ''}
            `}
            aria-expanded={isOpen}
            aria-haspopup="listbox"
          >
            {locale === 'he' && hebrewLetter ? (
              <span className="font-ui-hebrew">{hebrewLetter}</span>
            ) : (
              currentChapter
            )}
            <ChevronDown className={`ml-1 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
          </button>

          {/* Chapters dropdown */}
          {isOpen && chapters.length > 1 && (
            <div className="absolute left-1/2 -translate-x-1/2 top-full mt-2 dropdown-panel overflow-hidden z-50 min-w-[180px] max-h-[400px] overflow-y-auto">
              <div className="py-2">
                <div className="px-4 py-2 text-xs font-medium text-black/50 uppercase tracking-wide border-b border-black/5">
                  Chapters
                </div>
                <div className="grid grid-cols-4 gap-1 p-2">
                  {chapters.map((chapter) => (
                    <Link
                      key={chapter.number}
                      href={`/${locale}/book/${bookName}/chapter/${chapter.number}`}
                      onClick={() => setIsOpen(false)}
                      className={`flex items-center justify-center p-2 text-sm font-semibold rounded-lg transition-all duration-200 ${
                        chapter.number === currentChapter
                          ? 'bg-black text-white'
                          : 'text-black hover:bg-black/5'
                      }`}
                    >
                      {chapter.number}
                    </Link>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </h1>
    </div>
  );
}



