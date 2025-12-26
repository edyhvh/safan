'use client'

import { useEffect } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { getLocaleFromPath } from '@/lib/locale'
import { logger } from '@/lib/logger'

/**
 * Error page for locale-specific routes
 * Automatically shown when an error occurs in locale routes
 */
export default function LocaleError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  const pathname = usePathname()
  const locale = getLocaleFromPath(pathname)

  useEffect(() => {
    // Log the error
    logger.error('Locale route error', error, {
      digest: error.digest,
      pathname,
      locale,
    })
  }, [error, pathname, locale])

  const translations = {
    he: {
      title: 'נראה שהייתה שגיאה',
      subtitle: 'שמור על קור רוח וישוע המשיח',
      tryAgain: 'נסה שוב',
      home: 'חזרה לדף הבית',
    },
    es: {
      title: 'Parece que hubo un error',
      subtitle: "Mantén la calma y Yeshua Ha'Mashiaj",
      tryAgain: 'Intentar de nuevo',
      home: 'Volver al inicio',
    },
    en: {
      title: 'It seems there was an error',
      subtitle: "Keep Calm and Yeshua Ha'Mashiaj",
      tryAgain: 'Try again',
      home: 'Back to home',
    },
  }

  const t = translations[locale as keyof typeof translations] || translations.en
  const isHebrew = locale === 'he'

  return (
    <div className="min-h-screen flex items-start justify-center bg-background px-4 pt-32">
      <div className="max-w-2xl w-full text-center">
        {/* Main error message - Large text */}
        <h1
          className={`text-5xl md:text-6xl font-bold text-black mb-8 ${isHebrew ? 'font-ui-hebrew' : ''}`}
          dir={isHebrew ? 'rtl' : 'ltr'}
        >
          {t.title}
        </h1>

        {/* Subtitle - Smaller text */}
        <p
          className={`text-2xl md:text-3xl text-gray mb-8 ${isHebrew ? 'font-ui-hebrew' : ''}`}
          dir={isHebrew ? 'rtl' : 'ltr'}
        >
          {t.subtitle}
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={reset}
            className="px-6 py-3 bg-black text-white rounded-lg hover:bg-gray transition-colors"
          >
            {t.tryAgain}
          </button>
          <Link
            href={`/${locale}`}
            className="px-6 py-3 bg-white text-black border border-black/20 rounded-lg hover:bg-black/5 transition-colors"
          >
            {t.home}
          </Link>
        </div>

        {process.env.NODE_ENV === 'development' && error.message && (
          <div className="mt-8 p-4 bg-red-50 border border-red-200 rounded-lg text-left">
            <p className="text-sm font-mono text-red-800 break-all">
              {error.message}
            </p>
            {error.digest && (
              <p className="text-xs text-red-600 mt-2">
                Digest: {error.digest}
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
