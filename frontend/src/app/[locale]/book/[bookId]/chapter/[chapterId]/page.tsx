import { notFound } from 'next/navigation';
import { BOOK_DISPLAY_NAMES, type BookName } from '@/lib/books';
import { loadBookServer } from '@/lib/books-server';
import Link from 'next/link';
import ChapterTitleSelector from '@/components/navigation/ChapterTitleSelector';
import ChapterNavigation from '@/components/navigation/ChapterNavigation';

interface PageProps {
  params: Promise<{
    locale: string;
    bookId: string;
    chapterId: string;
  }>;
}

export async function generateMetadata({ params }: PageProps) {
  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/6127684b-7698-4a86-909f-f0c87e0aa0d6',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'page.tsx:16',message:'generateMetadata entry',data:{paramsType:typeof params},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H3'})}).catch(()=>{});
  // #endregion

  const resolvedParams = await params;
  const { locale, bookId, chapterId } = resolvedParams;

  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/6127684b-7698-4a86-909f-f0c87e0aa0d6',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'page.tsx:23',message:'generateMetadata params resolved',data:{locale,bookId,chapterId},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H3'})}).catch(()=>{});
  // #endregion

  const bookName = bookId as BookName;
  const chapterNumber = parseInt(chapterId);

  if (isNaN(chapterNumber) || chapterNumber < 1) {
    return {
      title: 'Not Found - Shafan',
    };
  }

  const displayName = BOOK_DISPLAY_NAMES[bookName] || { en: bookName, he: bookName, es: bookName };

  return {
    title: `${displayName.en} ${chapterNumber} - Shafan`,
    description: `Read ${displayName.en} chapter ${chapterNumber} from Elias Hutter's Hebrew New Testament`,
  };
}

export default async function BookChapterPage({ params }: PageProps) {
  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/6127684b-7698-4a86-909f-f0c87e0aa0d6',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'page.tsx:48',message:'BookChapterPage entry',data:{paramsType:typeof params},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H3'})}).catch(()=>{});
  // #endregion

  const resolvedParams = await params;
  const { locale, bookId, chapterId } = resolvedParams;

  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/6127684b-7698-4a86-909f-f0c87e0aa0d6',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'page.tsx:55',message:'BookChapterPage params resolved',data:{locale,bookId,chapterId},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H3'})}).catch(()=>{});
  // #endregion

  const bookName = bookId as BookName;
  const chapterNumber = parseInt(chapterId);

  // Validate parameters
  if (isNaN(chapterNumber) || chapterNumber < 1) {
    notFound();
  }

  // Load book data (Server Component - use server method)
  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/6127684b-7698-4a86-909f-f0c87e0aa0d6',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'page.tsx:68',message:'Before loadBookServer',data:{bookName},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H4'})}).catch(()=>{});
  // #endregion

  const book = await loadBookServer(bookName);

  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/6127684b-7698-4a86-909f-f0c87e0aa0d6',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'page.tsx:74',message:'After loadBookServer',data:{bookLoaded:!!book,bookName:book?.book_name,chaptersCount:book?.chapters?.length},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H4'})}).catch(()=>{});
  // #endregion

  if (!book) {
    notFound();
  }

  // Check if chapter exists
  const chapter = book.chapters.find((ch) => ch.number === chapterNumber);
  if (!chapter) {
    notFound();
  }

  const displayName = BOOK_DISPLAY_NAMES[bookName] || { en: bookName, he: bookName, es: bookName };
  const bookDisplayName = displayName[locale as 'he' | 'es' | 'en'] || displayName.en;

  return (
    <div className="max-w-4xl mx-auto">
      {/* Title - Centered, with interactive chapter selector */}
      <ChapterTitleSelector
        bookDisplayName={bookDisplayName}
        currentChapter={chapterNumber}
        hebrewLetter={chapter.hebrew_letter}
        chapters={book.chapters.map((ch) => ({ number: ch.number, hebrew_letter: ch.hebrew_letter }))}
        bookName={bookName}
        locale={locale}
      />

      {/* Chapter Navigation */}
      <ChapterNavigation
        locale={locale}
        bookName={bookName}
        currentChapter={chapterNumber}
        totalChapters={book.chapters.length}
      />

      {/* Chapter Content */}
      <div className="mb-12">
        <h2 className="font-bible-hebrew text-[64px] text-center mb-8 text-black">
          {chapter.hebrew_letter}
        </h2>

        <div className="space-y-8" dir="rtl">
          {chapter.verses.map((verse) => (
            <div
              key={verse.number}
              id={`verse-${verse.number}`}
              className="font-bible-hebrew text-[32px] md:text-[36px] leading-[1.9] text-black scroll-mt-32 target:bg-amber-100/50 target:rounded-lg target:px-4 target:-mx-4 transition-colors duration-500"
            >
              {verse.number > 0 && (
                <span className="text-gray/60 font-ui-latin text-base ml-3">{verse.number}</span>
              )}
              <span className="font-bible-hebrew">{verse.text_nikud || 'No text available'}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Chapter Navigation Footer */}
      <ChapterNavigation
        locale={locale}
        bookName={bookName}
        currentChapter={chapterNumber}
        totalChapters={book.chapters.length}
        className="mt-8 flex gap-4 justify-center"
      />

      {/* Author info at the end */}
      <div className="mt-12 text-center">
        <p className="font-ui-latin text-sm text-gray">
          {book.author} ({book.publication_year})
        </p>
      </div>
    </div>
  );
}
