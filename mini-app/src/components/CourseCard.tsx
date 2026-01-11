import { Link } from 'react-router-dom'
import { Course } from '../api'

interface CourseCardProps {
  course: Course
}

export default function CourseCard({ course }: CourseCardProps) {
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('uz-UZ').format(price)
  }

  const formatDuration = (hours: number) => {
    if (hours < 1) return 'Tez kunda'
    return `${hours} soat`
  }

  const getCategoryIcon = (category: string) => {
    const icons: Record<string, string> = {
      'Dasturlash': '💻',
      'Dizayn': '🎨',
      'Marketing': '📈',
      'Biznes': '💼',
      'Tillar': '🌍',
      'Boshqa': '📚',
    }
    return icons[category] || '📚'
  }

  return (
    <Link 
      to={`/courses/${course.id}`}
      className="block bg-telegram-bg rounded-2xl overflow-hidden shadow-sm hover:shadow-md transition-shadow"
    >
      {/* Thumbnail */}
      <div className="relative h-40 bg-gradient-to-br from-telegram-button to-purple-600 flex items-center justify-center">
        {course.thumbnail && course.thumbnail.startsWith('http') ? (
          <img 
            src={course.thumbnail} 
            alt={course.title}
            className="w-full h-full object-cover"
          />
        ) : (
          <>
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 opacity-90" />
            <span className="relative text-6xl">{getCategoryIcon(course.category)}</span>
          </>
        )}
        
        {/* Category badge */}
        <span className="absolute top-3 left-3 px-3 py-1 bg-white/20 backdrop-blur-sm rounded-full text-white text-xs">
          {course.category}
        </span>
        
        {/* Lessons count */}
        <span className="absolute top-3 right-3 px-3 py-1 bg-black/30 backdrop-blur-sm rounded-full text-white text-xs">
          📹 {course.lessons_count} dars
        </span>
      </div>
      
      {/* Content */}
      <div className="p-4">
        <h3 className="font-semibold text-telegram-text line-clamp-2 mb-2">
          {course.title}
        </h3>
        
        <p className="text-telegram-hint text-sm line-clamp-2 mb-3">
          {course.description}
        </p>
        
        <div className="flex items-center justify-between">
          <div>
            <span className="text-telegram-button font-bold text-lg">
              {formatPrice(course.price)} so'm
            </span>
            <span className="block text-telegram-hint text-xs">
              ⭐ {course.stars_price} Stars
            </span>
          </div>
          
          <span className="text-telegram-hint text-sm">
            ⏱ {formatDuration(course.duration)}
          </span>
        </div>
      </div>
    </Link>
  )
}
