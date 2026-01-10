import { Outlet, useLocation } from 'react-router-dom'
import BottomNav from './BottomNav'

export default function Layout() {
  const location = useLocation()
  const isLessonPage = location.pathname.startsWith('/lesson/')

  return (
    <div className="min-h-screen bg-telegram-secondary pb-20">
      <main className="animate-fade-in">
        <Outlet />
      </main>
      {!isLessonPage && <BottomNav />}
    </div>
  )
}
