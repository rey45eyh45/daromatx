import { Outlet, useLocation } from 'react-router-dom'
import BottomNav from './BottomNav'

export default function Layout() {
  const location = useLocation()
  
  // Bu sahifalarda navigation ko'rsatilmaydi
  const hideNavPages = [
    '/lesson/',
    '/courses/'  // Kurs detail sahifasi
  ]
  
  const shouldHideNav = hideNavPages.some(page => location.pathname.startsWith(page))

  return (
    <div className={`min-h-screen bg-telegram-secondary ${!shouldHideNav ? 'pb-20' : ''}`}>
      <main className="animate-fade-in">
        <Outlet />
      </main>
      {!shouldHideNav && <BottomNav />}
    </div>
  )
}
