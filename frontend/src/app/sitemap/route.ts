import { AVAILABLE_BOOKS } from '@/lib/books'
import { locales } from '@/lib/locale'
import { loadBookServer } from '@/lib/books-server'

export const runtime = 'nodejs'
export const revalidate = 604800

const BASE_URL = 'https://shafan.xyz'

function buildUrlEntry(
  loc: string,
  lastmod: string,
  changefreq: string,
  priority: string
) {
  return [
    '  <url>',
    `    <loc>${loc}</loc>`,
    `    <lastmod>${lastmod}</lastmod>`,
    `    <changefreq>${changefreq}</changefreq>`,
    `    <priority>${priority}</priority>`,
    '  </url>',
  ].join('\n')
}

export async function GET() {
  const lastmod = new Date().toISOString()
  const changefreq = 'weekly'
  const urls: string[] = []

  urls.push(buildUrlEntry(BASE_URL, lastmod, changefreq, '1.0'))

  locales.forEach((locale) => {
    urls.push(
      buildUrlEntry(`${BASE_URL}/${locale}`, lastmod, changefreq, '0.9')
    )
    urls.push(
      buildUrlEntry(`${BASE_URL}/${locale}/info`, lastmod, changefreq, '0.8')
    )
    urls.push(
      buildUrlEntry(`${BASE_URL}/${locale}/donate`, lastmod, changefreq, '0.8')
    )
  })

  const books = await Promise.all(
    AVAILABLE_BOOKS.map(async (bookId) => {
      const book = await loadBookServer(bookId)
      return { bookId, chapterCount: book?.chapters.length ?? 0 }
    })
  )

  books.forEach(({ bookId, chapterCount }) => {
    if (chapterCount < 1) return

    locales.forEach((locale) => {
      for (let chapter = 1; chapter <= chapterCount; chapter += 1) {
        urls.push(
          buildUrlEntry(
            `${BASE_URL}/${locale}/book/${bookId}/chapter/${chapter}`,
            lastmod,
            changefreq,
            '0.85'
          )
        )
      }
    })
  })

  const xml = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    urls.join('\n'),
    '</urlset>',
  ].join('\n')

  return new Response(xml, {
    status: 200,
    headers: {
      'Content-Type': 'application/xml; charset=utf-8',
      'Cache-Control': 'public, s-maxage=604800, stale-while-revalidate=86400',
    },
  })
}
