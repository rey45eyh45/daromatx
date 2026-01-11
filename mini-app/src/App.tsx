import { Routes, Route } from 'react-router-dom'
import { useEffect, useState } from 'react'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import CoursesPage from './pages/CoursesPage'
import CourseDetailPage from './pages/CourseDetailPage'
import MyCoursesPage from './pages/MyCoursesPage'
import LessonPage from './pages/LessonPage'
import ProfilePage from './pages/ProfilePage'
import AdminPage from './pages/AdminPage'
import { TelegramProvider } from './context/TelegramContext'

function App() {
  const [isReady, setIsReady] = useState(false)

  useEffect(() => {
    // Telegram WebApp initialization
    const tg = window.Telegram?.WebApp
    if (tg) {
      tg.ready()
      tg.expand()
      tg.enableClosingConfirmation()
      
      // Set header color
      tg.setHeaderColor('secondary_bg_color')
      tg.setBackgroundColor('secondary_bg_color')
    }
    setIsReady(true)
  }, [])

  if (!isReady) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-telegram-button border-t-transparent"></div>
      </div>
    )
  }

  return (
    <TelegramProvider>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="courses" element={<CoursesPage />} />
          <Route path="courses/:id" element={<CourseDetailPage />} />
          <Route path="my-courses" element={<MyCoursesPage />} />
          <Route path="lesson/:id" element={<LessonPage />} />
          <Route path="profile" element={<ProfilePage />} />
        </Route>
        {/* Admin sahifa - Layout'siz (BottomNav yo'q) */}
        <Route path="admin" element={<AdminPage />} />
      </Routes>
    </TelegramProvider>
  )
}

export default App
