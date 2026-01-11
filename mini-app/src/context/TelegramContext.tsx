import { createContext, useContext, useEffect, useState, ReactNode, useRef } from 'react'

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
  const mainButtonCallbackRef = useRef<(() => void) | null>(null)
  const backButtonCallbackRef = useRef<(() => void) | null>(null)

  useEffect(() => {
    const initTelegram = () => {
      const tg = window.Telegram?.WebApp
      
      if (tg && tg.initDataUnsafe?.user) {
        console.log('Telegram WebApp initialized:', tg.initDataUnsafe.user)
        setUser(tg.initDataUnsafe.user)
        setInitData(tg.initData)
        setIsReady(true)
        return true
      }
      return false
    }
    
    // Darhol sinab ko'rish
    if (initTelegram()) return
    
    // Agar Telegram hali yuklanmagan bo'lsa, qayta sinash
    const retryCount = 5
    let attempts = 0
    
    const retryInterval = setInterval(() => {
      attempts++
      console.log(`Telegram init attempt ${attempts}/${retryCount}`)
      
      if (initTelegram() || attempts >= retryCount) {
        clearInterval(retryInterval)
        
        // Agar hali ham topilmasa, development mode
        if (!window.Telegram?.WebApp?.initDataUnsafe?.user) {
          console.log('Using development mode user')
          setUser({
            id: 123456789,
            first_name: 'Mehmon',
            last_name: '',
            username: 'guest'
          })
          setInitData('user=%7B%22id%22%3A123456789%7D')
          setIsReady(true)
        }
      }
    }, 200)
    
    return () => clearInterval(retryInterval)
  }, [])

  const showMainButton = (text: string, onClick: () => void) => {
    const tg = window.Telegram?.WebApp
    if (tg) {
      // Eski callback ni olib tashlash
      if (mainButtonCallbackRef.current) {
        tg.MainButton.offClick(mainButtonCallbackRef.current)
      }
      // Yangi callback ni saqlash va qo'shish
      mainButtonCallbackRef.current = onClick
      tg.MainButton.setText(text)
      tg.MainButton.onClick(onClick)
      tg.MainButton.show()
    }
  }

  const hideMainButton = () => {
    const tg = window.Telegram?.WebApp
    if (tg) {
      // Callback ni olib tashlash
      if (mainButtonCallbackRef.current) {
        tg.MainButton.offClick(mainButtonCallbackRef.current)
        mainButtonCallbackRef.current = null
      }
      tg.MainButton.hide()
    }
  }

  const showBackButton = (onClick: () => void) => {
    const tg = window.Telegram?.WebApp
    if (tg) {
      // Eski callback ni olib tashlash
      if (backButtonCallbackRef.current) {
        tg.BackButton.offClick(backButtonCallbackRef.current)
      }
      // Yangi callback ni saqlash va qo'shish
      backButtonCallbackRef.current = onClick
      tg.BackButton.onClick(onClick)
      tg.BackButton.show()
    }
  }

  const hideBackButton = () => {
    const tg = window.Telegram?.WebApp
    if (tg) {
      // Callback ni olib tashlash
      if (backButtonCallbackRef.current) {
        tg.BackButton.offClick(backButtonCallbackRef.current)
        backButtonCallbackRef.current = null
      }
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
