'use client'

import React, { useEffect, useState } from 'react'
import { Sun, Moon } from 'lucide-react'
import { useTheme } from 'next-themes'

export function ThemeToggle({ size = 'md' }) {
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) return <div />

  return (
    <button onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')} className='p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800'>
      {theme === 'dark' ? <Sun className='w-5 h-5' /> : <Moon className='w-5 h-5' />}
    </button>
  )
}