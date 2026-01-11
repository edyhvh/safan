import { useState, useEffect, useCallback } from 'react'

export interface ScrollState {
  isAtTop: boolean
  isMouseAtTop: boolean
  scrollDirection: 'up' | 'down' | null
  shouldHideForContent: boolean
}

export function useScrollState(): ScrollState {
  const [scrollState, setScrollState] = useState<ScrollState>({
    isAtTop: true,
    isMouseAtTop: false,
    scrollDirection: null,
    shouldHideForContent: false,
  })

  const [lastScrollY, setLastScrollY] = useState(0)

  const handleScroll = useCallback(() => {
    const currentScrollY = window.scrollY
    const isAtTop = currentScrollY < 10

    // Check if we should hide navbar due to content collision
    // The navbar is approximately 90px tall (top-6 = 24px + navbar height ~66px)
    // We want to hide when content would be at the navbar's position
    // A good threshold is around 70-80px of scroll
    const shouldHideForContent = currentScrollY > 70

    setScrollState(prev => ({
      ...prev,
      isAtTop,
      shouldHideForContent,
      scrollDirection: currentScrollY > lastScrollY ? 'down' : 'up',
    }))

    setLastScrollY(currentScrollY)
  }, [lastScrollY])

  const handleMouseMove = useCallback((event: MouseEvent) => {
    // Detect if mouse is at the very top to show navbar
    // This is kept for potential future use, but currently navbar visibility
    // is controlled by hover state on the navbar itself
    const isMouseAtTop = event.clientY < 15
    setScrollState(prev => ({
      ...prev,
      isMouseAtTop,
    }))
  }, [])

  useEffect(() => {
    // Set initial state
    handleScroll()

    // Add event listeners
    window.addEventListener('scroll', handleScroll, { passive: true })
    window.addEventListener('mousemove', handleMouseMove, { passive: true })

    // Cleanup
    return () => {
      window.removeEventListener('scroll', handleScroll)
      window.removeEventListener('mousemove', handleMouseMove)
    }
  }, [handleScroll, handleMouseMove])

  return scrollState
}