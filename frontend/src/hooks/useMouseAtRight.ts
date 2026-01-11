import { useState, useEffect, useCallback } from 'react'

/**
 * Hook to detect if mouse is near the right edge of the screen
 * Used to show/hide reading controls similar to navbar behavior
 */
export function useMouseAtRight(threshold: number = 80): boolean {
  const [isMouseAtRight, setIsMouseAtRight] = useState(false)

  const handleMouseMove = useCallback(
    (event: MouseEvent) => {
      // Detect if mouse is near the right edge
      const windowWidth = window.innerWidth
      const mouseX = event.clientX
      const isAtRight = windowWidth - mouseX < threshold

      setIsMouseAtRight(isAtRight)
    },
    [threshold]
  )

  useEffect(() => {
    // Add event listener
    window.addEventListener('mousemove', handleMouseMove, { passive: true })

    // Cleanup
    return () => {
      window.removeEventListener('mousemove', handleMouseMove)
    }
  }, [handleMouseMove])

  return isMouseAtRight
}
