/**
 * SakuraPetals – Falling cherry blossom animation
 * Nur aktiv wenn theme === 'sakura'.
 * Verwendet CSS-Animationen (kein Canvas), respektiert prefers-reduced-motion.
 * 20 Blütenblätter mit zufälligen Positionen, Größen, Geschwindigkeiten.
 */
import { useEffect, useState } from 'react'
import { useTheme } from '../context/ThemeContext'
import { useA11y } from '../context/AccessibilityContext'

interface Petal {
  id: number
  left: number    // vw
  size: number    // px
  delay: number   // s
  duration: number // s
  rotation: number // deg Startrotation
  drift: number   // px horizontaler Drift
  opacity: number
}

function randomBetween(min: number, max: number) {
  return Math.random() * (max - min) + min
}

function generatePetals(count: number): Petal[] {
  return Array.from({ length: count }, (_, i) => ({
    id: i,
    left: randomBetween(0, 100),
    size: randomBetween(10, 18),
    delay: randomBetween(0, 12),
    duration: randomBetween(8, 16),
    rotation: randomBetween(0, 360),
    drift: randomBetween(-60, 60),
    opacity: randomBetween(0.55, 0.9),
  }))
}

const PETALS = generatePetals(22)

// SVG Kirschblütenblatt (vereinfacht, 5-blättrig)
const PetalSVG = ({ size, rotation }: { size: number; rotation: number }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 40 40"
    aria-hidden="true"
    style={{ transform: `rotate(${rotation}deg)` }}
  >
    {/* 5 Blüttenblätter */}
    {[0, 72, 144, 216, 288].map(angle => (
      <ellipse
        key={angle}
        cx="20" cy="20"
        rx="5" ry="10"
        fill="#f4a7b9"
        opacity="0.85"
        transform={`rotate(${angle} 20 20) translate(0 -8)`}
      />
    ))}
    <circle cx="20" cy="20" r="3" fill="#f9d0dc" />
  </svg>
)

export default function SakuraPetals() {
  const { theme } = useTheme()
  const { reduceMotion } = useA11y()
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    setVisible(theme === 'sakura' && !reduceMotion)
  }, [theme, reduceMotion])

  if (!visible) return null

  return (
    <div
      aria-hidden="true"
      style={{
        position: 'fixed',
        inset: 0,
        pointerEvents: 'none',
        zIndex: 9998,
        overflow: 'hidden',
      }}
    >
      {PETALS.map(p => (
        <div
          key={p.id}
          style={{
            position: 'absolute',
            top: '-30px',
            left: `${p.left}vw`,
            opacity: p.opacity,
            animation: `sakura-fall ${p.duration}s ${p.delay}s linear infinite`,
            '--drift': `${p.drift}px`,
          } as React.CSSProperties}
        >
          <PetalSVG size={p.size} rotation={p.rotation} />
        </div>
      ))}
    </div>
  )
}
