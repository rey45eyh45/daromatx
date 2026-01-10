import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { adminApi } from '../api'
import { useTelegram } from '../context/TelegramContext'
import Loading from '../components/Loading'

interface Stats {
  users_count: number
  courses_count: number
  today_users: number
}

export default function AdminPage() {
  const navigate = useNavigate()
  const { showBackButton, hideBackButton, showAlert } = useTelegram()
  
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  const [showAddCourse, setShowAddCourse] = useState(false)
  const [courseForm, setCourseForm] = useState({
    title: '',
    description: '',
    price: '',
    stars_price: '',
    category: 'Dasturlash'
  })

  useEffect(() => {
    loadStats()
    showBackButton(() => navigate('/'))
    
    return () => hideBackButton()
  }, [])

  const loadStats = async () => {
    try {
      const res = await adminApi.getStats()
      setStats(res.data)
    } catch (error: any) {
      console.error('Error loading stats:', error)
      if (error.response?.status === 403) {
        showAlert('Sizda admin huquqlari yo\'q!')
        navigate('/')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleAddCourse = async () => {
    if (!courseForm.title || !courseForm.description || !courseForm.price) {
      showAlert('Barcha maydonlarni to\'ldiring!')
      return
    }

    try {
      await adminApi.createCourse({
        title: courseForm.title,
        description: courseForm.description,
        price: parseFloat(courseForm.price),
        stars_price: parseInt(courseForm.stars_price) || 100,
        category: courseForm.category
      })
      
      showAlert('✅ Kurs muvaffaqiyatli qo\'shildi!')
      setShowAddCourse(false)
      setCourseForm({
        title: '',
        description: '',
        price: '',
        stars_price: '',
        category: 'Dasturlash'
      })
      loadStats()
    } catch (error) {
      console.error('Error adding course:', error)
      showAlert('Xatolik yuz berdi!')
    }
  }

  if (loading) {
    return <Loading text="Admin panel yuklanmoqda..." />
  }

  return (
    <div className="min-h-screen p-4">
      <h1 className="text-2xl font-bold text-telegram-text mb-6">🔐 Admin Panel</h1>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-3 mb-6">
        <div className="bg-blue-100 rounded-2xl p-4 text-center">
          <span className="text-2xl font-bold text-blue-600 block">
            {stats?.users_count || 0}
          </span>
          <span className="text-blue-600 text-sm">Foydalanuvchilar</span>
        </div>
        <div className="bg-green-100 rounded-2xl p-4 text-center">
          <span className="text-2xl font-bold text-green-600 block">
            {stats?.courses_count || 0}
          </span>
          <span className="text-green-600 text-sm">Kurslar</span>
        </div>
        <div className="bg-purple-100 rounded-2xl p-4 text-center">
          <span className="text-2xl font-bold text-purple-600 block">
            {stats?.today_users || 0}
          </span>
          <span className="text-purple-600 text-sm">Bugun</span>
        </div>
      </div>

      {/* Actions */}
      <div className="bg-telegram-bg rounded-2xl overflow-hidden mb-6">
        <button
          onClick={() => setShowAddCourse(true)}
          className="w-full flex items-center gap-4 p-4 hover:bg-telegram-secondary transition-colors border-b border-telegram-secondary"
        >
          <span className="text-2xl">➕</span>
          <span className="font-medium text-telegram-text">Kurs qo'shish</span>
        </button>
        <button className="w-full flex items-center gap-4 p-4 hover:bg-telegram-secondary transition-colors border-b border-telegram-secondary">
          <span className="text-2xl">📚</span>
          <span className="font-medium text-telegram-text">Kurslarni boshqarish</span>
        </button>
        <button className="w-full flex items-center gap-4 p-4 hover:bg-telegram-secondary transition-colors border-b border-telegram-secondary">
          <span className="text-2xl">👥</span>
          <span className="font-medium text-telegram-text">Foydalanuvchilar</span>
        </button>
        <button className="w-full flex items-center gap-4 p-4 hover:bg-telegram-secondary transition-colors">
          <span className="text-2xl">📢</span>
          <span className="font-medium text-telegram-text">Xabar yuborish</span>
        </button>
      </div>

      {/* Add Course Modal */}
      {showAddCourse && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-telegram-bg rounded-2xl p-6 w-full max-w-md max-h-[80vh] overflow-y-auto">
            <h2 className="text-xl font-bold text-telegram-text mb-4">➕ Yangi kurs</h2>
            
            <div className="space-y-4">
              <div>
                <label className="text-telegram-hint text-sm">Kurs nomi</label>
                <input
                  type="text"
                  value={courseForm.title}
                  onChange={(e) => setCourseForm({ ...courseForm, title: e.target.value })}
                  className="w-full p-3 bg-telegram-secondary rounded-xl text-telegram-text outline-none"
                  placeholder="Python kursi"
                />
              </div>
              
              <div>
                <label className="text-telegram-hint text-sm">Tavsif</label>
                <textarea
                  value={courseForm.description}
                  onChange={(e) => setCourseForm({ ...courseForm, description: e.target.value })}
                  className="w-full p-3 bg-telegram-secondary rounded-xl text-telegram-text outline-none h-24 resize-none"
                  placeholder="Kurs haqida..."
                />
              </div>
              
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-telegram-hint text-sm">Narx (so'm)</label>
                  <input
                    type="number"
                    value={courseForm.price}
                    onChange={(e) => setCourseForm({ ...courseForm, price: e.target.value })}
                    className="w-full p-3 bg-telegram-secondary rounded-xl text-telegram-text outline-none"
                    placeholder="100000"
                  />
                </div>
                <div>
                  <label className="text-telegram-hint text-sm">Stars narxi</label>
                  <input
                    type="number"
                    value={courseForm.stars_price}
                    onChange={(e) => setCourseForm({ ...courseForm, stars_price: e.target.value })}
                    className="w-full p-3 bg-telegram-secondary rounded-xl text-telegram-text outline-none"
                    placeholder="100"
                  />
                </div>
              </div>
              
              <div>
                <label className="text-telegram-hint text-sm">Kategoriya</label>
                <select
                  value={courseForm.category}
                  onChange={(e) => setCourseForm({ ...courseForm, category: e.target.value })}
                  className="w-full p-3 bg-telegram-secondary rounded-xl text-telegram-text outline-none"
                >
                  <option value="Dasturlash">Dasturlash</option>
                  <option value="Dizayn">Dizayn</option>
                  <option value="Marketing">Marketing</option>
                  <option value="Biznes">Biznes</option>
                  <option value="Tillar">Tillar</option>
                  <option value="Boshqa">Boshqa</option>
                </select>
              </div>
            </div>
            
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowAddCourse(false)}
                className="flex-1 p-3 bg-telegram-secondary text-telegram-hint rounded-xl"
              >
                Bekor qilish
              </button>
              <button
                onClick={handleAddCourse}
                className="flex-1 p-3 bg-telegram-button text-telegram-buttonText rounded-xl font-medium"
              >
                Qo'shish
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
