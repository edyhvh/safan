'use client'

import { useState, useRef, useEffect } from 'react'
import Link from 'next/link'
import { useClickOutside } from '@/hooks/useClickOutside'
import { ChevronDown } from '@/components/icons'
import {
  AVAILABLE_BOOKS,
  BOOK_DISPLAY_NAMES,
  BOOK_HEBREW_INFO,
  searchBooks,
  type BookName,
} from '@/lib/books'

interface ChapterTitleSelectorProps {
  bookDisplayName: string
  currentChapter: number
  hebrewLetter?: string
  chapters: { number: number; hebrew_letter: string }[]
  bookName: string
  locale: string
}

export default function ChapterTitleSelector({
  bookDisplayName,
  currentChapter,
  hebrewLetter,
  chapters,
  bookName,
  locale,
}: ChapterTitleSelectorProps) {
  const [isChapterOpen, setIsChapterOpen] = useState(false)
  const [isBookOpen, setIsBookOpen] = useState(false)
  const [bookSearchQuery, setBookSearchQuery] = useState('')
  const [chapterSearchQuery, setChapterSearchQuery] = useState('')
  const [filteredBooks, setFilteredBooks] = useState<BookName[]>([...AVAILABLE_BOOKS])
  const [filteredChapters, setFilteredChapters] = useState(chapters)
  const chapterDropdownRef = useRef<HTMLDivElement>(null)
  const bookDropdownRef = useRef<HTMLDivElement>(null)
  const bookSearchInputRef = useRef<HTMLInputElement>(null)
  const chapterSearchInputRef = useRef<HTMLInputElement>(null)

  // Filter books based on search query
  useEffect(() => {
    if (bookSearchQuery.trim()) {
      const results = searchBooks(bookSearchQuery)
      setFilteredBooks(results)
    } else {
      setFilteredBooks([...AVAILABLE_BOOKS])
    }
  }, [bookSearchQuery])

  // Filter chapters based on search query
  useEffect(() => {
    if (chapterSearchQuery.trim()) {
      const query = chapterSearchQuery.toLowerCase()
      const filtered = chapters.filter((chapter) =>
        chapter.number.toString().includes(query) ||
        chapter.hebrew_letter.includes(chapterSearchQuery)
      )
      setFilteredChapters(filtered)
    } else {
      setFilteredChapters(chapters)
    }
  }, [chapterSearchQuery, chapters])

  // Focus search inputs when dropdowns open
  useEffect(() => {
    if (isBookOpen && bookSearchInputRef.current) {
      setTimeout(() => bookSearchInputRef.current?.focus(), 100)
    } else {
      setBookSearchQuery('')
    }
  }, [isBookOpen])

  useEffect(() => {
    if (isChapterOpen && chapterSearchInputRef.current) {
      setTimeout(() => chapterSearchInputRef.current?.focus(), 100)
    } else {
      setChapterSearchQuery('')
    }
  }, [isChapterOpen])

  // Close dropdowns when clicking outside
  useClickOutside(
    chapterDropdownRef,
    () => setIsChapterOpen(false),
    isChapterOpen
  )
  useClickOutside(bookDropdownRef, () => setIsBookOpen(false), isBookOpen)

  // Get Hebrew info for the current book (for en/es locales)
  const hebrewInfo = BOOK_HEBREW_INFO[bookName as BookName]
  const transliteration =
    locale === 'es'
      ? hebrewInfo?.transliteration.es
      : hebrewInfo?.transliteration.en

  return (
    <div className="text-center mb-8 pt-12">
      {/* Hebrew name and transliteration (only for en/es locales) */}
      {locale !== 'he' && hebrewInfo && (
        <div className="mb-3 text-center">
          <div className="font-bible-hebrew text-xl text-black/70 leading-tight">
            {hebrewInfo.hebrew}
          </div>
          <div className="text-[11px] text-black/35 font-light tracking-wide">
            {transliteration}
          </div>
        </div>
      )}
      <h1 className="font-ui-latin text-lg text-black mb-1 inline-flex items-center gap-2">
        {/* Book selector with click dropdown */}
        <div className="relative inline-block" ref={bookDropdownRef}>
          <button
            onClick={() => {
              setIsBookOpen(!isBookOpen)
              setIsChapterOpen(false)
            }}
            className={`
              h-[36px] px-3
              flex items-center justify-center
              font-semibold text-base
              cursor-pointer
              transition-all duration-200
              neumorphism
              ${isBookOpen ? 'active' : ''}
            `}
            aria-expanded={isBookOpen}
            aria-haspopup="listbox"
          >
            <span className={locale === 'he' ? 'font-ui-hebrew' : ''}>
              {bookDisplayName}
            </span>
            <ChevronDown
              className={`ml-1 transition-transform duration-200 ${isBookOpen ? 'rotate-180' : ''}`}
            />
          </button>

          {/* Books dropdown */}
          {isBookOpen && (
            <div className="absolute left-1/2 -translate-x-1/2 top-full mt-2 dropdown-panel overflow-hidden z-50 min-w-[200px] max-h-[400px] overflow-y-auto">
              {/* Book search */}
              <div className="p-2 border-b border-black/5">
                <div className="relative">
                  <svg
                    className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-black/40"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                    />
                  </svg>
                  <input
                    ref={bookSearchInputRef}
                    type="text"
                    value={bookSearchQuery}
                    onChange={(e) => setBookSearchQuery(e.target.value)}
                    placeholder="Search for..."
                    className="w-full pl-10 pr-4 py-2 text-sm font-ui-latin text-black neumorphism-inset outline-none placeholder:text-black/40 rounded-lg"
                    onClick={(e) => e.stopPropagation()}
                  />
                </div>
              </div>
              <div className="py-1 max-h-[300px] overflow-y-auto">
                {filteredBooks.length > 0 ? (
                  filteredBooks.map((book) => {
                  const displayName = BOOK_DISPLAY_NAMES[book]
                  const isCurrentBook = book === bookName
                  return (
                    <Link
                      key={book}
                      href={`/${locale}/book/${book}/chapter/1`}
                      onClick={() => setIsBookOpen(false)}
                      className={`block px-4 py-2 text-sm font-semibold transition-all duration-200 ${
                        isCurrentBook
                          ? 'bg-black text-white'
                          : 'text-black hover:bg-black/5'
                      } ${locale === 'he' ? 'font-ui-hebrew text-right' : ''}`}
                    >
                      {displayName[locale as 'he' | 'es' | 'en'] ||
                        displayName.en}
                    </Link>
                  )
                  })
                ) : (
                  <div className="px-4 py-3 text-sm text-black/60 text-center">
                    No books found
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Chapter selector with click dropdown */}
        <div className="relative inline-block" ref={chapterDropdownRef}>
          <button
            onClick={() => {
              setIsChapterOpen(!isChapterOpen)
              setIsBookOpen(false)
            }}
            className={`
              min-w-[36px] h-[36px] px-2
              flex items-center justify-center
              font-semibold text-base
              cursor-pointer
              transition-all duration-200
              neumorphism
              ${isChapterOpen ? 'active' : ''}
            `}
            aria-expanded={isChapterOpen}
            aria-haspopup="listbox"
          >
            {locale === 'he' && hebrewLetter ? (
              <span className="font-ui-hebrew">{hebrewLetter}</span>
            ) : (
              currentChapter
            )}
            <ChevronDown
              className={`ml-1 transition-transform duration-200 ${isChapterOpen ? 'rotate-180' : ''}`}
            />
          </button>

          {/* Chapters dropdown */}
          {isChapterOpen && chapters.length > 1 && (
            <div className="absolute left-1/2 -translate-x-1/2 top-full mt-2 dropdown-panel overflow-hidden z-50 min-w-[180px] max-h-[400px] overflow-y-auto">
              <div className="py-2">
                <div className="px-4 py-2 text-xs font-medium text-black/50 uppercase tracking-wide border-b border-black/5">
                  Chapters
                </div>
                {/* Chapter search */}
                <div className="p-2 border-b border-black/5">
                  <div className="relative">
                    <svg
                      className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-black/40"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                      />
                    </svg>
                    <input
                      ref={chapterSearchInputRef}
                      type="text"
                      value={chapterSearchQuery}
                      onChange={(e) => setChapterSearchQuery(e.target.value)}
                      placeholder="Search for..."
                      className="w-full pl-10 pr-4 py-2 text-sm font-ui-latin text-black neumorphism-inset outline-none placeholder:text-black/40 rounded-lg"
                      onClick={(e) => e.stopPropagation()}
                    />
                  </div>
                </div>
                <div className="grid grid-cols-4 gap-1 p-2">
                  {filteredChapters.length > 0 ? (
                    filteredChapters.map((chapter) => (
                    <Link
                      key={chapter.number}
                      href={`/${locale}/book/${bookName}/chapter/${chapter.number}`}
                      onClick={() => setIsChapterOpen(false)}
                      className={`flex items-center justify-center p-2 text-sm font-semibold rounded-lg transition-all duration-200 ${
                        chapter.number === currentChapter
                          ? 'bg-black text-white'
                          : 'text-black hover:bg-black/5'
                      }`}
                    >
                      {chapter.number}
                    </Link>
                    ))
                  ) : (
                    <div className="col-span-4 px-4 py-3 text-sm text-black/60 text-center">
                      No chapters found
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </h1>
    </div>
  )
}
