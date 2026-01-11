import { useEffect, useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { adminApi, AdminCourse, AdminCourseDetail, AdminLesson, Analytics } from '../api'
import { useTelegram } from '../context/TelegramContext'
import Loading from '../components/Loading'

interface Stats {
  users_count: number
  courses_count: number
  today_users: number
}

type Tab = 'dashboard' | 'courses' | 'course-detail'

export default function AdminPage() {
  const navigate = useNavigate()
  const { showBackButton, hideBackButton, showAlert, showConfirm } = useTelegram()
  
  const [stats, setStats] = useState<Stats | null>(null)
  const [analytics, setAnalytics] = useState<Analytics | null>(null)
  const [loading, setLoading] = useState(true)
  const [tab, setTab] = useState<Tab>('dashboard')
  
  // Courses
  const [courses, setCourses] = useState<AdminCourse[]>([])
  const [selectedCourse, setSelectedCourse] = useState<AdminCourseDetail | null>(null)
  
  // Modals
  const [showAddCourse, setShowAddCourse] = useState(false)
  const [showAddLesson, setShowAddLesson] = useState(false)
  const [showVideoModal, setShowVideoModal] = useState(false)
  const [selectedLesson, setSelectedLesson] = useState<AdminLesson | null>(null)
  
  // Forms
  const [courseForm, setCourseForm] = useState({
    title: '',
    description: '',
    price: '',
    stars_price: '',
    ton_price: '',
    category: 'Dasturlash'
  })
  
  const [lessonForm, setLessonForm] = useState({
    title: '',
    description: '',
    is_free: false
  })
  
  const [videoForm, setVideoForm] = useState({
    video_file_id: '',
    video_url: '',
    duration: ''
  })
  
  const thumbnailInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    loadStats()
    showBackButton(() => {
      if (tab === 'course-detail') {
        setTab('courses')
        setSelectedCourse(null)
      } else if (tab === 'courses') {
        setTab('dashboard')
      } else {
        navigate('/')
      }
    })
    
    return () => hideBackButton()
  }, [tab])

  const loadStats = async () => {
    try {
      const [statsRes, analyticsRes] = await Promise.all([
        adminApi.getStats(),
        adminApi.getAnalytics()
      ])
      setStats(statsRes.data)
      setAnalytics(analyticsRes.data)
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
  
  const loadCourses = async () => {
    try {
      const res = await adminApi.getCourses()
      setCourses(res.data.courses)
    } catch (error) {
      console.error('Error loading courses:', error)
    }
  }

  const loadCourseDetail = async (courseId: number) => {
    try {
      const res = await adminApi.getCourseDetail(courseId)
      setSelectedCourse(res.data)
      setTab('course-detail')
    } catch (error) {
      console.error('Error loading course:', error)
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
        ton_price: parseFloat(courseForm.ton_price) || 0,
        category: courseForm.category
      })
      
      showAlert('✅ Kurs muvaffaqiyatli qo\'shildi!')
      setShowAddCourse(false)
      setCourseForm({
        title: '',
        description: '',
        price: '',
        stars_price: '',
        ton_price: '',
        category: 'Dasturlash'
      })
      loadStats()
      loadCourses()
    } catch (error) {
      console.error('Error adding course:', error)
      showAlert('Xatolik yuz berdi!')
    }
  }

  const handleDeleteCourse = async (courseId: number) => {
    const confirmed = await showConfirm('Kursni o\'chirmoqchimisiz?')
    if (confirmed) {
      try {
        await adminApi.deleteCourse(courseId)
        showAlert('✅ Kurs o\'chirildi!')
        loadCourses()
      } catch (error) {
        showAlert('Xatolik!')
      }
    }
  }

  const handleAddLesson = async () => {
    if (!lessonForm.title || !selectedCourse) return

    try {
      await adminApi.createLesson(selectedCourse.id, {
        title: lessonForm.title,
        description: lessonForm.description || undefined,
        is_free: lessonForm.is_free
      })
      showAlert('✅ Dars qo\'shildi!')
      setShowAddLesson(false)
      setLessonForm({ title: '', description: '', is_free: false })
      loadCourseDetail(selectedCourse.id)
    } catch (error) {
      showAlert('Xatolik!')
    }
  }

  const handleDeleteLesson = async (lessonId: number) => {
    if (!selectedCourse) return
    try {
      await adminApi.deleteLesson(lessonId)
      showAlert('✅ Dars o\'chirildi!')
      loadCourseDetail(selectedCourse.id)
    } catch (error) {
      showAlert('Xatolik!')
    }
  }

  const handleSetVideo = async () => {
    if (!selectedLesson) return
    if (!videoForm.video_file_id && !videoForm.video_url) {
      showAlert('Video file ID yoki URL kiriting!')
      return
    }
    try {
      await adminApi.setLessonVideo(selectedLesson.id, {
        video_file_id: videoForm.video_file_id || undefined,
        video_url: videoForm.video_url || undefined,
        duration: parseInt(videoForm.duration) || 0
      })
      showAlert('✅ Video qo\'shildi!')
      setShowVideoModal(false)
      setVideoForm({ video_file_id: '', video_url: '', duration: '' })
      if (selectedCourse) loadCourseDetail(selectedCourse.id)
    } catch (error) {
      showAlert('Xatolik!')
    }
  }

  const handleThumbnailUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file || !selectedCourse) return
    try {
      await adminApi.uploadThumbnail(selectedCourse.id, file)
      showAlert('✅ Rasm yuklandi!')
      loadCourseDetail(selectedCourse.id)
    } catch (error) {
      showAlert('Rasm yuklashda xatolik!')
    }
  }

  const formatPrice = (price: number) => price.toLocaleString('uz-UZ')

  if (loading) {
    return <Loading text="Admin panel yuklanmoqda..." />
  }

  // Courses Tab
  if (tab === 'courses') {
    return (
      <div className="min-h-screen p-4">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-xl font-bold text-telegram-text">📚 Kurslar</h1>
          <button onClick={() => setShowAddCourse(true)} className="px-3 py-2 bg-telegram-button text-white rounded-xl text-sm">
            ➕ Yangi
          </button>
        </div>
        
        {courses.length === 0 ? (
          <div className="text-center py-10 text-telegram-hint">Kurslar yo'q</div>
        ) : (
          <div className="space-y-3">
            {courses.map(course => (
              <div key={course.id} className="bg-telegram-bg rounded-2xl p-4">
                <h3 className="font-medium text-telegram-text">{course.title}</h3>
                <p className="text-telegram-hint text-sm">{course.lessons_count} ta dars • {formatPrice(course.price)} so'm</p>
                <div className="flex gap-2 mt-3">
                  <button onClick={() => loadCourseDetail(course.id)} className="flex-1 py-2 bg-telegram-secondary rounded-xl text-sm">
                    ✏️ Tahrirlash
                  </button>
                  <button onClick={() => handleDeleteCourse(course.id)} className="py-2 px-4 bg-red-100 text-red-600 rounded-xl text-sm">
                    🗑️
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
        
        {showAddCourse && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-telegram-bg rounded-2xl p-6 w-full max-w-md max-h-[80vh] overflow-y-auto">
              <h2 className="text-xl font-bold text-telegram-text mb-4">➕ Yangi kurs</h2>
              <div className="space-y-4">
                <input type="text" value={courseForm.title} onChange={(e) => setCourseForm({ ...courseForm, title: e.target.value })}
                  className="w-full p-3 bg-telegram-secondary rounded-xl text-telegram-text outline-none" placeholder="Kurs nomi" />
                <textarea value={courseForm.description} onChange={(e) => setCourseForm({ ...courseForm, description: e.target.value })}
                  className="w-full p-3 bg-telegram-secondary rounded-xl text-telegram-text outline-none h-20 resize-none" placeholder="Tavsif" />
                <div className="grid grid-cols-2 gap-3">
                  <input type="number" value={courseForm.price} onChange={(e) => setCourseForm({ ...courseForm, price: e.target.value })}
                    className="w-full p-3 bg-telegram-secondary rounded-xl text-telegram-text outline-none" placeholder="Narx (so'm)" />
                  <input type="number" value={courseForm.stars_price} onChange={(e) => setCourseForm({ ...courseForm, stars_price: e.target.value })}
                    className="w-full p-3 bg-telegram-secondary rounded-xl text-telegram-text outline-none" placeholder="Stars" />
                </div>
                <input type="number" step="0.1" value={courseForm.ton_price} onChange={(e) => setCourseForm({ ...courseForm, ton_price: e.target.value })}
                  className="w-full p-3 bg-telegram-secondary rounded-xl text-telegram-text outline-none" placeholder="TON narxi" />
                <select value={courseForm.category} onChange={(e) => setCourseForm({ ...courseForm, category: e.target.value })}
                  className="w-full p-3 bg-telegram-secondary rounded-xl text-telegram-text outline-none">
                  <option value="Dasturlash">Dasturlash</option>
                  <option value="Dizayn">Dizayn</option>
                  <option value="Marketing">Marketing</option>
                  <option value="Biznes">Biznes</option>
                  <option value="Tillar">Tillar</option>
                  <option value="Boshqa">Boshqa</option>
                </select>
              </div>
              <div className="flex gap-3 mt-6">
                <button onClick={() => setShowAddCourse(false)} className="flex-1 p-3 bg-telegram-secondary rounded-xl">Bekor</button>
                <button onClick={handleAddCourse} className="flex-1 p-3 bg-telegram-button text-white rounded-xl">Qo'shish</button>
              </div>
            </div>
          </div>
        )}
      </div>
    )
  }

  // Course Detail Tab
  if (tab === 'course-detail' && selectedCourse) {
    return (
      <div className="min-h-screen p-4">
        <div className="bg-telegram-bg rounded-2xl p-4 mb-4">
          <h2 className="font-bold text-telegram-text mb-2">{selectedCourse.title}</h2>
          <p className="text-telegram-hint text-sm mb-3">{formatPrice(selectedCourse.price)} so'm • {selectedCourse.lessons.length} ta dars</p>
          <input type="file" ref={thumbnailInputRef} onChange={handleThumbnailUpload} accept="image/*" className="hidden" />
          <button onClick={() => thumbnailInputRef.current?.click()} className="w-full py-2 bg-telegram-secondary rounded-xl text-sm">
            🖼️ Rasm yuklash
          </button>
        </div>

        <div className="flex items-center justify-between mb-3">
          <h3 className="font-bold text-telegram-text">📖 Darslar</h3>
          <button onClick={() => setShowAddLesson(true)} className="px-3 py-1.5 bg-green-500 text-white rounded-lg text-sm">
            ➕ Dars
          </button>
        </div>

        {selectedCourse.lessons.length === 0 ? (
          <div className="text-center py-8 text-telegram-hint bg-telegram-bg rounded-2xl">Darslar yo'q</div>
        ) : (
          <div className="space-y-2">
            {selectedCourse.lessons.map((lesson, i) => (
              <div key={lesson.id} className="bg-telegram-bg rounded-xl p-3 flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-telegram-secondary flex items-center justify-center text-sm">{i + 1}</div>
                <div className="flex-1">
                  <span className="font-medium text-telegram-text text-sm">{lesson.title}</span>
                  <div className="text-xs text-telegram-hint">
                    {lesson.has_video ? <span className="text-green-500">✅ Video</span> : <span className="text-red-500">❌ Video yo'q</span>}
                  </div>
                </div>
                <button onClick={() => { setSelectedLesson(lesson); setShowVideoModal(true); }} className="p-2 bg-blue-100 text-blue-600 rounded-lg">🎥</button>
                <button onClick={() => handleDeleteLesson(lesson.id)} className="p-2 bg-red-100 text-red-600 rounded-lg">🗑️</button>
              </div>
            ))}
          </div>
        )}

        {showAddLesson && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-telegram-bg rounded-2xl p-6 w-full max-w-md">
              <h2 className="text-xl font-bold text-telegram-text mb-4">➕ Yangi dars</h2>
              <input type="text" value={lessonForm.title} onChange={(e) => setLessonForm({ ...lessonForm, title: e.target.value })}
                className="w-full p-3 bg-telegram-secondary rounded-xl text-telegram-text outline-none mb-3" placeholder="Dars nomi" />
              <label className="flex items-center gap-2 mb-4">
                <input type="checkbox" checked={lessonForm.is_free} onChange={(e) => setLessonForm({ ...lessonForm, is_free: e.target.checked })} />
                <span className="text-telegram-text text-sm">Bepul dars</span>
              </label>
              <div className="flex gap-3">
                <button onClick={() => setShowAddLesson(false)} className="flex-1 p-3 bg-telegram-secondary rounded-xl">Bekor</button>
                <button onClick={handleAddLesson} className="flex-1 p-3 bg-green-500 text-white rounded-xl">Qo'shish</button>
              </div>
            </div>
          </div>
        )}

        {showVideoModal && selectedLesson && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-telegram-bg rounded-2xl p-6 w-full max-w-md">
              <h2 className="text-xl font-bold text-telegram-text mb-4">🎥 Video qo'shish</h2>
              <p className="text-telegram-hint text-sm mb-4">{selectedLesson.title}</p>
              <input type="text" value={videoForm.video_file_id} onChange={(e) => setVideoForm({ ...videoForm, video_file_id: e.target.value })}
                className="w-full p-3 bg-telegram-secondary rounded-xl text-telegram-text outline-none mb-2 text-sm" placeholder="Telegram File ID" />
              <p className="text-telegram-hint text-xs mb-3">Botga video yuboring va file_id ni oling</p>
              <input type="text" value={videoForm.video_url} onChange={(e) => setVideoForm({ ...videoForm, video_url: e.target.value })}
                className="w-full p-3 bg-telegram-secondary rounded-xl text-telegram-text outline-none mb-3 text-sm" placeholder="yoki Video URL" />
              <input type="number" value={videoForm.duration} onChange={(e) => setVideoForm({ ...videoForm, duration: e.target.value })}
                className="w-full p-3 bg-telegram-secondary rounded-xl text-telegram-text outline-none mb-4" placeholder="Davomiyligi (soniya)" />
              <div className="flex gap-3">
                <button onClick={() => { setShowVideoModal(false); setSelectedLesson(null); }} className="flex-1 p-3 bg-telegram-secondary rounded-xl">Bekor</button>
                <button onClick={handleSetVideo} className="flex-1 p-3 bg-blue-500 text-white rounded-xl">Saqlash</button>
              </div>
            </div>
          </div>
        )}
      </div>
    )
  }

  // Dashboard Tab (default)
  const formatMoney = (amount: number) => {
    if (amount >= 1000000) return `${(amount / 1000000).toFixed(1)}M`
    if (amount >= 1000) return `${(amount / 1000).toFixed(0)}K`
    return amount.toString()
  }

  return (
    <div className="min-h-screen p-4">
      <h1 className="text-2xl font-bold text-telegram-text mb-6">🔐 Admin Panel</h1>

      {/* Main Stats */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl p-4 text-center text-white">
          <span className="text-2xl font-bold block">{stats?.users_count || 0}</span>
          <span className="text-xs opacity-90">Foydalanuvchilar</span>
        </div>
        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-2xl p-4 text-center text-white">
          <span className="text-2xl font-bold block">{stats?.courses_count || 0}</span>
          <span className="text-xs opacity-90">Kurslar</span>
        </div>
        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl p-4 text-center text-white">
          <span className="text-2xl font-bold block">{analytics?.total_lessons || 0}</span>
          <span className="text-xs opacity-90">Darslar</span>
        </div>
      </div>

      {/* Growth Stats */}
      {analytics && (
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="bg-telegram-bg rounded-2xl p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-telegram-hint text-xs">Foydalanuvchi o'sishi</span>
              <span className={`text-xs font-bold ${analytics.users_growth >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                {analytics.users_growth >= 0 ? '↑' : '↓'} {Math.abs(analytics.users_growth)}%
              </span>
            </div>
            <div className="text-lg font-bold text-telegram-text">+{analytics.weekly_users} haftalik</div>
          </div>
          <div className="bg-telegram-bg rounded-2xl p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-telegram-hint text-xs">Daromad o'sishi</span>
              <span className={`text-xs font-bold ${analytics.revenue_growth >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                {analytics.revenue_growth >= 0 ? '↑' : '↓'} {Math.abs(analytics.revenue_growth)}%
              </span>
            </div>
            <div className="text-lg font-bold text-telegram-text">{formatMoney(analytics.weekly_revenue)} so'm</div>
          </div>
        </div>
      )}

      {/* Period Stats */}
      {analytics && (
        <div className="bg-telegram-bg rounded-2xl p-4 mb-4">
          <h3 className="font-bold text-telegram-text mb-3">📊 Statistika</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center py-2 border-b border-telegram-secondary">
              <span className="text-telegram-hint text-sm">Bugun</span>
              <div className="text-right">
                <span className="text-telegram-text font-medium">{analytics.today_users} foydalanuvchi</span>
                <span className="text-green-500 text-sm ml-2">• {analytics.today_payments} to'lov</span>
              </div>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-telegram-secondary">
              <span className="text-telegram-hint text-sm">Haftalik</span>
              <div className="text-right">
                <span className="text-telegram-text font-medium">{analytics.weekly_users} foydalanuvchi</span>
                <span className="text-green-500 text-sm ml-2">• {formatMoney(analytics.weekly_revenue)}</span>
              </div>
            </div>
            <div className="flex justify-between items-center py-2">
              <span className="text-telegram-hint text-sm">Oylik</span>
              <div className="text-right">
                <span className="text-telegram-text font-medium">{analytics.monthly_users} foydalanuvchi</span>
                <span className="text-green-500 text-sm ml-2">• {formatMoney(analytics.monthly_revenue)}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Top Courses */}
      {analytics && analytics.top_courses.length > 0 && (
        <div className="bg-telegram-bg rounded-2xl p-4 mb-4">
          <h3 className="font-bold text-telegram-text mb-3">🏆 Top Kurslar</h3>
          <div className="space-y-2">
            {analytics.top_courses.map((course, index) => (
              <div key={course.id} className="flex items-center gap-3 py-2">
                <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                  index === 0 ? 'bg-yellow-500 text-white' : 
                  index === 1 ? 'bg-gray-400 text-white' : 
                  index === 2 ? 'bg-amber-600 text-white' : 'bg-telegram-secondary text-telegram-text'
                }`}>
                  {index + 1}
                </span>
                <span className="flex-1 text-telegram-text text-sm truncate">{course.title}</span>
                <span className="text-telegram-hint text-xs">{course.sales} sotuv</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="bg-telegram-bg rounded-2xl overflow-hidden mb-6">
        <button onClick={() => setShowAddCourse(true)} className="w-full flex items-center gap-4 p-4 hover:bg-telegram-secondary transition-colors border-b border-telegram-secondary">
          <span className="text-2xl">➕</span>
          <span className="font-medium text-telegram-text">Kurs qo'shish</span>
        </button>
        <button onClick={() => { loadCourses(); setTab('courses') }} className="w-full flex items-center gap-4 p-4 hover:bg-telegram-secondary transition-colors border-b border-telegram-secondary">
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

      {showAddCourse && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-telegram-bg rounded-2xl p-6 w-full max-w-md max-h-[80vh] overflow-y-auto">
            <h2 className="text-xl font-bold text-telegram-text mb-4">➕ Yangi kurs</h2>
            <div className="space-y-4">
              <input type="text" value={courseForm.title} onChange={(e) => setCourseForm({ ...courseForm, title: e.target.value })}
                className="w-full p-3 bg-telegram-secondary rounded-xl text-telegram-text outline-none" placeholder="Kurs nomi" />
              <textarea value={courseForm.description} onChange={(e) => setCourseForm({ ...courseForm, description: e.target.value })}
                className="w-full p-3 bg-telegram-secondary rounded-xl text-telegram-text outline-none h-20 resize-none" placeholder="Tavsif" />
              <div className="grid grid-cols-2 gap-3">
                <input type="number" value={courseForm.price} onChange={(e) => setCourseForm({ ...courseForm, price: e.target.value })}
                  className="w-full p-3 bg-telegram-secondary rounded-xl text-telegram-text outline-none" placeholder="Narx (so'm)" />
                <input type="number" value={courseForm.stars_price} onChange={(e) => setCourseForm({ ...courseForm, stars_price: e.target.value })}
                  className="w-full p-3 bg-telegram-secondary rounded-xl text-telegram-text outline-none" placeholder="Stars" />
              </div>
              <input type="number" step="0.1" value={courseForm.ton_price} onChange={(e) => setCourseForm({ ...courseForm, ton_price: e.target.value })}
                className="w-full p-3 bg-telegram-secondary rounded-xl text-telegram-text outline-none" placeholder="TON narxi" />
              <select value={courseForm.category} onChange={(e) => setCourseForm({ ...courseForm, category: e.target.value })}
                className="w-full p-3 bg-telegram-secondary rounded-xl text-telegram-text outline-none">
                <option value="Dasturlash">Dasturlash</option>
                <option value="Dizayn">Dizayn</option>
                <option value="Marketing">Marketing</option>
                <option value="Biznes">Biznes</option>
                <option value="Tillar">Tillar</option>
                <option value="Boshqa">Boshqa</option>
              </select>
            </div>
            <div className="flex gap-3 mt-6">
              <button onClick={() => setShowAddCourse(false)} className="flex-1 p-3 bg-telegram-secondary rounded-xl">Bekor</button>
              <button onClick={handleAddCourse} className="flex-1 p-3 bg-telegram-button text-white rounded-xl">Qo'shish</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
