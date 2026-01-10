import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { coursesApi, Course, Category } from '../api'
import CourseCard from '../components/CourseCard'
import { SkeletonCard } from '../components/Loading'
import { SearchIcon } from '../components/Icons'

// Default categories when API is not available
const defaultCategories: Category[] = [
  { id: '1', name: 'Dasturlash', icon: '💻' },
  { id: '2', name: 'Dizayn', icon: '🎨' },
  { id: '3', name: 'Marketing', icon: '📈' },
  { id: '4', name: 'Biznes', icon: '💼' },
  { id: '5', name: 'Tillar', icon: '🌍' },
  { id: '6', name: 'Foto/Video', icon: '📸' },
  { id: '7', name: 'Musiqa', icon: '🎵' },
  { id: '8', name: 'Boshqa', icon: '✨' },
]

export default function CoursesPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [courses, setCourses] = useState<Course[]>([])
  const [categories, setCategories] = useState<Category[]>(defaultCategories)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  
  const activeCategory = searchParams.get('category') || ''

  useEffect(() => {
    loadCategories()
  }, [])

  useEffect(() => {
    loadCourses()
  }, [activeCategory, search])

  const loadCategories = async () => {
    try {
      const res = await coursesApi.getCategories()
      if (res.data.categories.length > 0) {
        setCategories(res.data.categories)
      }
    } catch (error) {
      console.error('Error loading categories:', error)
      // Keep default categories
    }
  }

  const loadCourses = async () => {
    setLoading(true)
    try {
      const res = await coursesApi.getAll(activeCategory || undefined, search || undefined)
      setCourses(res.data)
    } catch (error) {
      console.error('Error loading courses:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCategoryClick = (categoryId: string) => {
    if (categoryId === activeCategory) {
      searchParams.delete('category')
    } else {
      searchParams.set('category', categoryId)
    }
    setSearchParams(searchParams)
  }

  return (
    <div className="min-h-screen bg-telegram-secondary/30">
      {/* Header */}
      <div className="bg-telegram-bg p-4 pb-6 rounded-b-3xl shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-xl font-bold text-telegram-text flex items-center gap-2">
            <span className="w-1 h-6 bg-telegram-button rounded-full"></span>
            Kurslar
          </h1>
          <span className="text-sm text-telegram-hint">{courses.length} ta kurs</span>
        </div>
        
        {/* Search */}
        <div className="relative mb-4">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Kurs yoki mavzuni qidiring..."
            className="w-full px-4 py-3.5 pl-12 bg-telegram-secondary/50 rounded-2xl text-telegram-text placeholder-telegram-hint outline-none focus:ring-2 focus:ring-telegram-button/50 transition-all"
          />
          <div className="absolute left-4 top-1/2 -translate-y-1/2 text-telegram-hint">
            <SearchIcon size={20} />
          </div>
          {search && (
            <button 
              onClick={() => setSearch('')}
              className="absolute right-4 top-1/2 -translate-y-1/2 text-telegram-hint hover:text-telegram-text"
            >
              ✕
            </button>
          )}
        </div>
        
        {/* Categories Grid */}
        <div className="grid grid-cols-4 gap-2">
          {/* All button */}
          <button
            onClick={() => handleCategoryClick('')}
            className={`flex flex-col items-center justify-center p-3 rounded-2xl transition-all ${
              !activeCategory
                ? 'bg-gradient-to-br from-telegram-button to-purple-600 text-white shadow-lg scale-[1.02]'
                : 'bg-telegram-secondary/50 text-telegram-text hover:bg-telegram-secondary active:scale-95'
            }`}
          >
            <span className="text-xl mb-1">🔥</span>
            <span className="text-[10px] font-medium">Barchasi</span>
          </button>
          
          {categories.slice(0, 7).map((cat) => (
            <button
              key={cat.id}
              onClick={() => handleCategoryClick(cat.id)}
              className={`flex flex-col items-center justify-center p-3 rounded-2xl transition-all ${
                activeCategory === cat.id
                  ? 'bg-gradient-to-br from-telegram-button to-purple-600 text-white shadow-lg scale-[1.02]'
                  : 'bg-telegram-secondary/50 text-telegram-text hover:bg-telegram-secondary active:scale-95'
              }`}
            >
              <span className="text-xl mb-1">{cat.icon}</span>
              <span className="text-[10px] font-medium text-center leading-tight">{cat.name}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Active filter info */}
      {(activeCategory || search) && (
        <div className="px-4 py-3 flex items-center justify-between">
          <p className="text-sm text-telegram-hint">
            {search && `"${search}" `}
            {activeCategory && categories.find(c => c.id === activeCategory)?.name}
            {' '}bo'yicha qidirildi
          </p>
          <button 
            onClick={() => {
              setSearch('')
              searchParams.delete('category')
              setSearchParams(searchParams)
            }}
            className="text-telegram-button text-sm flex items-center gap-1"
          >
            Tozalash
          </button>
        </div>
      )}

      {/* Courses list */}
      <div className="p-4 pb-24">
        {loading ? (
          <div className="grid gap-4">
            {[1, 2, 3, 4].map((i) => (
              <SkeletonCard key={i} />
            ))}
          </div>
        ) : courses.length > 0 ? (
          <div className="grid gap-4">
            {courses.map((course) => (
              <CourseCard key={course.id} course={course} />
            ))}
          </div>
        ) : (
          <div className="text-center py-16 bg-telegram-bg rounded-3xl shadow-sm">
            <div className="w-20 h-20 mx-auto mb-4 bg-gradient-to-br from-telegram-button/20 to-purple-500/20 rounded-3xl flex items-center justify-center">
              <span className="text-4xl">🔍</span>
            </div>
            <h3 className="font-semibold text-telegram-text mb-2">Kurslar topilmadi</h3>
            <p className="text-telegram-hint text-sm px-8 mb-4">
              Boshqa kategoriya yoki so'zni sinab ko'ring
            </p>
            <button
              onClick={() => {
                setSearch('')
                searchParams.delete('category')
                setSearchParams(searchParams)
              }}
              className="px-6 py-2.5 bg-telegram-button text-white rounded-xl text-sm font-medium"
            >
              Barcha kurslarni ko'rish
            </button>
          </div>
        )}
      </div>
    </div>
  )
}