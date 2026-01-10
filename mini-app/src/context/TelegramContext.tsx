import { createContext, useContext, useEffect, useState, ReactNode } from 'react'

interface TelegramUser {
  id: number
  first_name: string
  last_name?: string
  username?: string
  language_code?: string
  is_premium?: boolean
}

interface TelegramContextType {
  user: TelegramUser | null
  initData: string
  isReady: boolean
  showMainButton: (text: string, onClick: () => void) => void
  hideMainButton: () => void
  showBackButton: (onClick: () => void) => void
  hideBackButton: () => void
  showAlert: (message: string) => void
  showConfirm: (message: string) => Promise<boolean>
  openInvoice: (url: string) => Promise<string>
  hapticFeedback: (type: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft') => void
}

const TelegramContext = createContext<TelegramContextType | null>(null)

export function TelegramProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<TelegramUser | null>(null)
  const [initData, setInitData] = useState('')
  const [isReady, setIsReady] = useState(false)

  useEffect(() => {
    const tg = window.Telegram?.WebApp
    
    if (tg) {
      setUser(tg.initDataUnsafe.user || null)
      setInitData(tg.initData)
      setIsReady(true)
    } else {
      // Development mode - mock user
      setUser({
        id: 123456789,
        first_name: 'Test',
        last_name: 'User',
        username: 'testuser'
      })
      setInitData('user=%7B%22id%22%3A123456789%7D')
      setIsReady(true)
    }
  }, [])

  const showMainButton = (text: string, onClick: () => void) => {
    const tg = window.Telegram?.WebApp
    if (tg) {
      tg.MainButton.setText(text)
      tg.MainButton.onClick(onClick)
      tg.MainButton.show()
    }
  }

  const hideMainButton = () => {
    const tg = window.Telegram?.WebApp
    if (tg) {
      tg.MainButton.hide()
    }
  }

  const showBackButton = (onClick: () => void) => {
    const tg = window.Telegram?.WebApp
    if (tg) {
      tg.BackButton.onClick(onClick)
      tg.BackButton.show()
    }
  }

  const hideBackButton = () => {
    const tg = window.Telegram?.WebApp
    if (tg) {
      tg.BackButton.hide()
    }
  }

  const showAlert = (message: string) => {
    const tg = window.Telegram?.WebApp
    if (tg) {
      tg.showAlert(message)
    } else {
      alert(message)
    }
  }

  const showConfirm = (message: string): Promise<boolean> => {
    return new Promise((resolve) => {
      const tg = window.Telegram?.WebApp
      if (tg) {
        tg.showConfirm(message, resolve)
      } else {
        resolve(confirm(message))
      }
    })
  }

  const openInvoice = (url: string): Promise<string> => {
    return new Promise((resolve) => {
      const tg = window.Telegram?.WebApp
      if (tg) {
        tg.openInvoice(url, (status) => {
          resolve(status)
        })
      } else {
        window.open(url, '_blank')
        resolve('opened')
      }
    })
  }

  const hapticFeedback = (type: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft') => {
    const tg = window.Telegram?.WebApp as any
    if (tg?.HapticFeedback) {
      tg.HapticFeedback.impactOccurred(type)
    }
  }

  return (
    <TelegramContext.Provider value={{
      user,
      initData,
      isReady,
      showMainButton,
      hideMainButton,
      showBackButton,
      hideBackButton,
      showAlert,
      showConfirm,
      openInvoice,
      hapticFeedback
    }}>
      {children}
    </TelegramContext.Provider>
  )
}

export function useTelegram() {
  const context = useContext(TelegramContext)
  if (!context) {
    throw new Error('useTelegram must be used within TelegramProvider')
  }
  return context
}
