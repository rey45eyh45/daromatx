import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useTelegram } from '../context/TelegramContext'
import { coursesApi, Course, Category } from '../api'
import CourseCard from '../components/CourseCard'
import { SkeletonCard } from '../components/Loading'
import { 
  SearchIcon, 
  StarIcon, 
  UsersIcon, 
  VideoIcon, 
  AwardIcon,
  ChevronRightIcon,
  PlayIcon
} from '../components/Icons'

// Stats data
const stats = [
  { icon: UsersIcon, value: '1,200+', label: "O'quvchilar", color: 'from-blue-500 to-cyan-400' },
  { icon: VideoIcon, value: '50+', label: 'Video darslar', color: 'from-purple-500 to-pink-400' },
  { icon: AwardIcon, value: '15+', label: 'Sertifikatlar', color: 'from-amber-500 to-orange-400' },
]

// Features
const features = [
  { icon: '🎯', title: 'Amaliy loyihalar', desc: 'Real loyihalar bilan ishlash' },
  { icon: '💬', title: "24/7 Qo'llab-quvvatlash", desc: 'Har doim yordam beramiz' },
  { icon: '📱', title: 'Mobil qulay', desc: "Istalgan joyda o'qing" },
  { icon: '🏆', title: 'Sertifikat', desc: 'Kurs oxirida sertifikat' },
]

export default function HomePage() {
  const { user } = useTelegram()
  const [courses, setCourses] = useState<Course[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [activeSlide, setActiveSlide] = useState(0)

  useEffect(() => {
    loadData()
  }, [])

  // Auto slide for hero
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveSlide((prev) => (prev + 1) % 3)
    }, 4000)
    return () => clearInterval(interval)
  }, [])

  const loadData = async () => {
    try {
      const [coursesRes, categoriesRes] = await Promise.all([
        coursesApi.getAll(),
        coursesApi.getCategories()
      ])
      setCourses(coursesRes.data)
      setCategories(categoriesRes.data.categories)
    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      setLoading(false)
    }
  }

  const heroSlides = [
    {
      title: "Kelajak kasblarini o'rganing",
      subtitle: 'IT, Dizayn, Marketing va boshqalar',
      gradient: 'from-telegram-button via-purple-600 to-indigo-700',
      emoji: '🚀'
    },
    {
      title: "Professional bo'ling",
      subtitle: "Eng yaxshi mentorlar bilan o'qing",
      gradient: 'from-emerald-500 via-teal-500 to-cyan-600',
      emoji: '💼'
    },
    {
      title: "50+ video darslar",
      subtitle: "Amaliy loyihalar bilan o'rganing",
      gradient: 'from-orange-500 via-red-500 to-pink-600',
      emoji: '🎬'
    }
  ]

  return (
    <div className="min-h-screen bg-telegram-secondary/30">
      {/* Hero Section with Animated Gradient */}
      <div className={`relative bg-gradient-to-br ${heroSlides[activeSlide].gradient} text-white overflow-hidden transition-all duration-700`}>
        {/* Animated background shapes */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-20 -right-20 w-64 h-64 bg-white/10 rounded-full blur-3xl animate-pulse" />
          <div className="absolute -bottom-20 -left-20 w-64 h-64 bg-white/10 rounded-full blur-3xl animate-pulse delay-1000" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-white/5 rounded-full blur-3xl" />
        </div>

        <div className="relative z-10 px-5 pt-6 pb-10">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center shadow-lg">
                <span className="text-2xl">🎓</span>
              </div>
              <div>
                <p className="text-white/70 text-xs">Xush kelibsiz</p>
                <h1 className="text-lg font-bold">{user?.first_name || 'Mehmon'}</h1>
              </div>
            </div>
            <Link 
              to="/profile"
              className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center"
            >
              <span className="text-xl">👤</span>
            </Link>
          </div>

          {/* Hero Content */}
          <div className="text-center py-6">
            <div className="text-5xl mb-4 animate-bounce">
              {heroSlides[activeSlide].emoji}
            </div>
            <h2 className="text-2xl font-bold mb-2 transition-all duration-500">
              {heroSlides[activeSlide].title}
            </h2>
            <p className="text-white/80 text-sm mb-6">
              {heroSlides[activeSlide].subtitle}
            </p>

            {/* Slide indicators */}
            <div className="flex justify-center gap-2 mb-6">
              {heroSlides.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setActiveSlide(index)}
                  className={`h-1.5 rounded-full transition-all duration-300 ${
                    activeSlide === index 
                      ? 'w-8 bg-white' 
                      : 'w-1.5 bg-white/40'
                  }`}
                />
              ))}
            </div>

            {/* CTA Button */}
            <Link
              to="/courses"
              className="inline-flex items-center gap-2 bg-white text-telegram-button font-semibold px-6 py-3 rounded-2xl shadow-lg hover:shadow-xl transition-all hover:scale-105 active:scale-95"
            >
              <PlayIcon size={18} />
              Kurslarni ko'rish
            </Link>
          </div>

          {/* Search bar */}
          <Link 
            to="/courses"
            className="flex items-center gap-3 bg-white/15 backdrop-blur-md rounded-2xl p-4 mt-4 border border-white/20 hover:bg-white/20 transition-all"
          >
            <SearchIcon size={20} className="text-white/70" />
            <span className="text-white/70 text-sm">Kurs yoki mavzuni qidiring...</span>
          </Link>
        </div>

        {/* Wave decoration */}
        <div className="absolute bottom-0 left-0 right-0">
          <svg viewBox="0 0 1440 120" fill="none" className="w-full h-8">
            <path 
              d="M0,64 C480,120 960,0 1440,64 L1440,120 L0,120 Z" 
              className="fill-telegram-secondary/30"
            />
          </svg>
        </div>
      </div>

      {/* Stats Section */}
      <div className="px-4 -mt-2">
        <div className="bg-telegram-bg rounded-3xl shadow-lg p-4 grid grid-cols-3 gap-2">
          {stats.map((stat, index) => {
            const IconComponent = stat.icon
            return (
              <div key={index} className="text-center p-3">
                <div className={`w-12 h-12 mx-auto mb-2 rounded-2xl bg-gradient-to-br ${stat.color} flex items-center justify-center shadow-lg`}>
                  <IconComponent size={22} className="text-white" />
                </div>
                <div className="text-lg font-bold text-telegram-text">{stat.value}</div>
                <div className="text-[10px] text-telegram-hint">{stat.label}</div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Categories */}
      <div className="px-4 mt-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-telegram-text flex items-center gap-2">
            <span className="w-1 h-5 bg-telegram-button rounded-full"></span>
            Kategoriyalar
          </h2>
          <Link to="/courses" className="text-telegram-button text-sm flex items-center gap-1">
            Barchasi <ChevronRightIcon size={16} />
          </Link>
        </div>
        
        <div className="grid grid-cols-4 gap-3">
          {(categories.length > 0 ? categories.slice(0, 8) : [
            { id: 1, name: 'Dasturlash', icon: '💻' },
            { id: 2, name: 'Dizayn', icon: '🎨' },
            { id: 3, name: 'Marketing', icon: '📈' },
            { id: 4, name: 'Biznes', icon: '💼' },
            { id: 5, name: 'Tillar', icon: '🌍' },
            { id: 6, name: 'Foto/Video', icon: '📸' },
            { id: 7, name: 'Musiqa', icon: '🎵' },
            { id: 8, name: 'Boshqa', icon: '✨' },
          ]).map((cat) => (
            <Link
              key={cat.id}
              to={`/courses?category=${cat.id}`}
              className="flex flex-col items-center p-3 bg-telegram-bg rounded-2xl shadow-sm hover:shadow-md transition-all hover:scale-105 active:scale-95"
            >
              <span className="text-2xl mb-1">{cat.icon}</span>
              <span className="text-[10px] text-telegram-text text-center font-medium">{cat.name}</span>
            </Link>
          ))}
        </div>
      </div>

      {/* Features */}
      <div className="px-4 mt-6">
        <h2 className="text-lg font-bold text-telegram-text flex items-center gap-2 mb-4">
          <span className="w-1 h-5 bg-purple-500 rounded-full"></span>
          Nega bizni tanlashadi?
        </h2>
        
        <div className="grid grid-cols-2 gap-3">
          {features.map((feature, index) => (
            <div 
              key={index}
              className="bg-telegram-bg p-4 rounded-2xl shadow-sm"
            >
              <span className="text-2xl">{feature.icon}</span>
              <h3 className="font-semibold text-telegram-text text-sm mt-2">{feature.title}</h3>
              <p className="text-[11px] text-telegram-hint mt-1">{feature.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Popular Courses */}
      <div className="px-4 mt-6 pb-24">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-telegram-text flex items-center gap-2">
            <span className="w-1 h-5 bg-orange-500 rounded-full"></span>
            🔥 Mashhur kurslar
          </h2>
          <Link to="/courses" className="text-telegram-button text-sm flex items-center gap-1">
            Barchasi <ChevronRightIcon size={16} />
          </Link>
        </div>
        
        {loading ? (
          <div className="grid gap-4">
            {[1, 2, 3].map((i) => (
              <SkeletonCard key={i} />
            ))}
          </div>
        ) : courses.length > 0 ? (
          <div className="grid gap-4">
            {courses.slice(0, 5).map((course) => (
              <CourseCard key={course.id} course={course} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12 bg-telegram-bg rounded-3xl shadow-sm">
            <div className="w-20 h-20 mx-auto mb-4 bg-gradient-to-br from-telegram-button/20 to-purple-500/20 rounded-3xl flex items-center justify-center">
              <span className="text-4xl">📚</span>
            </div>
            <h3 className="font-semibold text-telegram-text mb-2">Kurslar tez orada!</h3>
            <p className="text-telegram-hint text-sm px-8">
              Biz sizlar uchun eng yaxshi kurslarni tayyorlamoqdamiz
            </p>
            <div className="flex items-center justify-center gap-2 mt-4">
              <span className="w-2 h-2 bg-telegram-button rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
              <span className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
              <span className="w-2 h-2 bg-pink-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
            </div>
          </div>
        )}
      </div>

      {/* Floating CTA */}
      <div className="fixed bottom-20 left-4 right-4 z-30">
        <Link
          to="/courses"
          className="flex items-center justify-between bg-gradient-to-r from-telegram-button to-purple-600 text-white p-4 rounded-2xl shadow-lg hover:shadow-xl transition-all"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
              <StarIcon size={20} className="text-yellow-300" />
            </div>
            <div>
              <p className="font-semibold text-sm">Birinchi kursni boshlang!</p>
              <p className="text-white/70 text-xs">50% chegirma 🎉</p>
            </div>
          </div>
          <ChevronRightIcon size={24} />
        </Link>
      </div>
    </div>
  )
}
