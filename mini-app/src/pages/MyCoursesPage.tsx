import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { usersApi, PurchasedCourse } from '../api'
import Loading from '../components/Loading'
import { PlayIcon, CheckIcon, ClockIcon, VideoIcon } from '../components/Icons'

// Demo data for testing when API is not available
const demoCourses: PurchasedCourse[] = [
  {
    id: 1,
    course_id: 1,
    course_title: 'Python dasturlash asoslari',
    progress: 65,
    total_lessons: 24,
    completed_lessons: 16,
    thumbnail: '',
    purchased_at: '2026-01-05'
  },
  {
    id: 2,
    course_id: 2,
    course_title: 'Web dizayn kursi',
    progress: 30,
    total_lessons: 18,
    completed_lessons: 5,
    thumbnail: '',
    purchased_at: '2026-01-08'
  },
  {
    id: 3,
    course_id: 3,
    course_title: 'SMM marketing',
    progress: 100,
    total_lessons: 12,
    completed_lessons: 12,
    thumbnail: '',
    purchased_at: '2025-12-20'
  }
]

export default function MyCoursesPage() {
  const [courses, setCourses] = useState<PurchasedCourse[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'in-progress' | 'completed'>('all')

  useEffect(() => {
    loadMyCourses()
  }, [])

  const loadMyCourses = async () => {
    try {
      const res = await usersApi.getMyCourses()
      setCourses(res.data.length > 0 ? res.data : demoCourses)
    } catch (error) {
      console.error('Error loading my courses:', error)
      // Use demo data for testing
      setCourses(demoCourses)
    } finally {
      setLoading(false)
    }
  }

  const filteredCourses = courses.filter(course => {
    if (filter === 'completed') return course.progress === 100
    if (filter === 'in-progress') return course.progress < 100
    return true
  })

  const stats = {
    total: courses.length,
    inProgress: courses.filter(c => c.progress < 100).length,
    completed: courses.filter(c => c.progress === 100).length
  }

  if (loading) {
    return <Loading text="Kurslaringiz yuklanmoqda..." />
  }

  return (
    <div className="min-h-screen bg-telegram-secondary/30 pb-24">
      {/* Header */}
      <div className="bg-gradient-to-br from-telegram-button via-purple-600 to-indigo-700 text-white p-5 pb-8 rounded-b-3xl">
        <h1 className="text-xl font-bold mb-4 flex items-center gap-2">
          <span className="w-1 h-6 bg-white/50 rounded-full"></span>
          Mening kurslarim
        </h1>
        
        {/* Stats */}
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-white/15 backdrop-blur-sm rounded-2xl p-3 text-center">
            <div className="text-2xl font-bold">{stats.total}</div>
            <div className="text-[10px] text-white/70">Jami kurs</div>
          </div>
          <div className="bg-white/15 backdrop-blur-sm rounded-2xl p-3 text-center">
            <div className="text-2xl font-bold text-yellow-300">{stats.inProgress}</div>
            <div className="text-[10px] text-white/70">Davom etmoqda</div>
          </div>
          <div className="bg-white/15 backdrop-blur-sm rounded-2xl p-3 text-center">
            <div className="text-2xl font-bold text-green-300">{stats.completed}</div>
            <div className="text-[10px] text-white/70">Tugallangan</div>
          </div>
        </div>
      </div>

      {/* Filter tabs */}
      <div className="px-4 -mt-4">
        <div className="bg-telegram-bg rounded-2xl p-1.5 flex gap-1 shadow-lg">
          {[
            { key: 'all', label: 'Barchasi', count: stats.total },
            { key: 'in-progress', label: 'Davom etmoqda', count: stats.inProgress },
            { key: 'completed', label: 'Tugallangan', count: stats.completed }
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setFilter(tab.key as typeof filter)}
              className={`flex-1 py-2.5 px-2 rounded-xl text-xs font-medium transition-all ${
                filter === tab.key
                  ? 'bg-telegram-button text-white shadow-md'
                  : 'text-telegram-hint hover:text-telegram-text'
              }`}
            >
              {tab.label} ({tab.count})
            </button>
          ))}
        </div>
      </div>

      {/* Courses list */}
      <div className="p-4">
        {filteredCourses.length > 0 ? (
          <div className="space-y-3">
            {filteredCourses.map((course) => (
              <Link
                key={course.id}
                to={`/courses/${course.course_id}`}
                className="block bg-telegram-bg rounded-2xl p-4 shadow-sm hover:shadow-md transition-all active:scale-[0.98]"
              >
                <div className="flex items-start gap-4">
                  {/* Thumbnail */}
                  <div className={`w-16 h-16 rounded-xl flex items-center justify-center text-2xl ${
                    course.progress === 100 
                      ? 'bg-gradient-to-br from-green-500 to-emerald-600' 
                      : 'bg-gradient-to-br from-telegram-button to-purple-600'
                  }`}>
                    {course.progress === 100 ? '✅' : '📚'}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-telegram-text mb-1 truncate">
                      {course.course_title}
                    </h3>
                    
                    {/* Lessons info */}
                    <div className="flex items-center gap-3 text-xs text-telegram-hint mb-2">
                      <span className="flex items-center gap-1">
                        <VideoIcon size={12} />
                        {course.completed_lessons || 0}/{course.total_lessons || 0} dars
                      </span>
                      {course.progress === 100 ? (
                        <span className="flex items-center gap-1 text-green-500">
                          <CheckIcon size={12} />
                          Tugallangan
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 text-yellow-600">
                          <ClockIcon size={12} />
                          Davom etmoqda
                        </span>
                      )}
                    </div>
                    
                    {/* Progress bar */}
                    <div className="w-full h-2 bg-telegram-secondary rounded-full overflow-hidden">
                      <div 
                        className={`h-full transition-all rounded-full ${
                          course.progress === 100 
                            ? 'bg-gradient-to-r from-green-500 to-emerald-500' 
                            : 'bg-gradient-to-r from-telegram-button to-purple-500'
                        }`}
                        style={{ width: `${course.progress}%` }}
                      ></div>
                    </div>
                    <div className="flex justify-between items-center mt-1">
                      <span className="text-[10px] text-telegram-hint">
                        {course.progress}% tugallangan
                      </span>
                    </div>
                  </div>
                  
                  {/* Play button */}
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                    course.progress === 100 
                      ? 'bg-green-500/20 text-green-600' 
                      : 'bg-telegram-button/20 text-telegram-button'
                  }`}>
                    {course.progress === 100 ? (
                      <CheckIcon size={20} />
                    ) : (
                      <PlayIcon size={18} />
                    )}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        ) : courses.length > 0 ? (
          <div className="text-center py-12 bg-telegram-bg rounded-3xl">
            <span className="text-5xl mb-4 block">📋</span>
            <p className="text-telegram-hint">Bu kategoriyada kurs yo'q</p>
          </div>
        ) : (
          <div className="text-center py-12 bg-telegram-bg rounded-3xl shadow-sm">
            <div className="w-24 h-24 mx-auto mb-4 bg-gradient-to-br from-telegram-button/20 to-purple-500/20 rounded-3xl flex items-center justify-center">
              <span className="text-5xl">📚</span>
            </div>
            <h2 className="text-lg font-semibold text-telegram-text mb-2">
              Hali kurs sotib olmadingiz
            </h2>
            <p className="text-telegram-hint text-sm mb-6 px-8">
              Bilimingizni oshirish uchun kurslarimizni ko'ring va o'rganishni boshlang!
            </p>
            <Link 
              to="/courses"
              className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-telegram-button to-purple-600 text-white rounded-2xl font-medium shadow-lg hover:shadow-xl transition-all"
            >
              <PlayIcon size={18} />
              Kurslarni ko'rish
            </Link>
          </div>
        )}
      </div>
    </div>
  )
}
