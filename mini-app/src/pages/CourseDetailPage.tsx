import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { coursesApi, CourseDetail, paymentsApi } from '../api'
import { useTelegram } from '../context/TelegramContext'
import Loading from '../components/Loading'

export default function CourseDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { showBackButton, hideBackButton, showMainButton, hideMainButton, showAlert, hapticFeedback } = useTelegram()
  
  const [course, setCourse] = useState<CourseDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [purchasing, setPurchasing] = useState(false)
  const [showPaymentModal, setShowPaymentModal] = useState(false)

  useEffect(() => {
    if (id) {
      loadCourse(parseInt(id))
    }

    // Back button
    showBackButton(() => navigate(-1))
    
    return () => {
      hideBackButton()
      hideMainButton()
    }
  }, [id])

  useEffect(() => {
    if (course) {
      showMainButton(`Sotib olish - ${formatPrice(course.price)} so'm`, () => {
        setShowPaymentModal(true)
      })
    }
  }, [course])

  const loadCourse = async (courseId: number) => {
    try {
      const res = await coursesApi.getById(courseId)
      setCourse(res.data)
    } catch (error) {
      console.error('Error loading course:', error)
      showAlert('Kurs topilmadi')
      navigate('/courses')
    } finally {
      setLoading(false)
    }
  }

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('uz-UZ').format(price)
  }

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60)
    return `${minutes} daqiqa`
  }

  const handlePayment = async (paymentType: string) => {
    if (!course) return
    
    setPurchasing(true)
    hapticFeedback('medium')
    
    try {
      const res = await paymentsApi.create(course.id, paymentType)
      
      if (res.data.payment_url) {
        // Open payment URL
        const tg = window.Telegram?.WebApp
        if (paymentType === 'stars' && tg) {
          tg.openInvoice(res.data.payment_url, (status) => {
            if (status === 'paid') {
              showAlert('🎉 Tabriklaymiz! Kurs muvaffaqiyatli sotib olindi!')
              navigate('/my-courses')
            }
          })
        } else {
          window.open(res.data.payment_url, '_blank')
        }
      }
      
      setShowPaymentModal(false)
    } catch (error) {
      console.error('Payment error:', error)
      showAlert('Xatolik yuz berdi. Qayta urinib ko\'ring.')
    } finally {
      setPurchasing(false)
    }
  }

  if (loading) {
    return <Loading text="Kurs yuklanmoqda..." />
  }

  if (!course) {
    return null
  }

  return (
    <div className="min-h-screen">
      {/* Header image */}
      <div className="relative h-56 bg-gradient-to-br from-telegram-button to-purple-600 flex items-center justify-center">
        {course.thumbnail ? (
          <img 
            src={course.thumbnail} 
            alt={course.title}
            className="w-full h-full object-cover"
          />
        ) : (
          <span className="text-8xl">📚</span>
        )}
        
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
        
        <div className="absolute bottom-4 left-4 right-4 text-white">
          <span className="px-3 py-1 bg-white/20 backdrop-blur-sm rounded-full text-sm">
            {course.category}
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="p-4 -mt-4 relative">
        <div className="bg-telegram-bg rounded-2xl p-4 shadow-lg">
          <h1 className="text-xl font-bold text-telegram-text mb-2">
            {course.title}
          </h1>
          
          <div className="flex items-center gap-4 text-telegram-hint text-sm mb-4">
            <span>📹 {course.lessons_count} dars</span>
            <span>⏱ {course.duration} soat</span>
          </div>
          
          <p className="text-telegram-text mb-4">
            {course.description}
          </p>
          
          {/* Price */}
          <div className="flex items-center justify-between p-4 bg-telegram-secondary rounded-xl mb-4">
            <div>
              <span className="text-2xl font-bold text-telegram-button">
                {formatPrice(course.price)} so'm
              </span>
              <span className="block text-telegram-hint text-sm">
                ⭐ {course.stars_price} Telegram Stars
              </span>
            </div>
          </div>
        </div>

        {/* Lessons */}
        <div className="mt-4">
          <h2 className="text-lg font-semibold text-telegram-text mb-3">
            📖 Darslar ro'yxati
          </h2>
          
          <div className="space-y-2">
            {course.lessons.map((lesson, index) => (
              <div
                key={lesson.id}
                className={`p-4 bg-telegram-bg rounded-xl flex items-center gap-3 ${
                  lesson.is_free ? 'cursor-pointer hover:bg-telegram-secondary' : 'opacity-70'
                }`}
                onClick={() => lesson.is_free && navigate(`/lesson/${lesson.id}`)}
              >
                <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium ${
                  lesson.is_free ? 'bg-green-100 text-green-600' : 'bg-telegram-secondary text-telegram-hint'
                }`}>
                  {index + 1}
                </div>
                <div className="flex-1">
                  <h3 className="font-medium text-telegram-text">{lesson.title}</h3>
                  <span className="text-telegram-hint text-sm">
                    {formatDuration(lesson.duration)}
                  </span>
                </div>
                <span className="text-xl">
                  {lesson.is_free ? '▶️' : '🔒'}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Payment Modal */}
      {showPaymentModal && (
        <div className="fixed inset-0 bg-black/50 flex items-end z-50" onClick={() => setShowPaymentModal(false)}>
          <div 
            className="w-full bg-telegram-bg rounded-t-3xl p-6 animate-slide-up"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="w-12 h-1 bg-telegram-hint/30 rounded-full mx-auto mb-4"></div>
            
            <h3 className="text-xl font-bold text-telegram-text mb-4">
              💳 To'lov usulini tanlang
            </h3>
            
            <div className="space-y-3 mb-4">
              <button
                onClick={() => handlePayment('stars')}
                disabled={purchasing}
                className="w-full p-4 bg-yellow-100 text-yellow-700 rounded-xl font-medium flex items-center justify-between"
              >
                <span>⭐ Telegram Stars</span>
                <span>{course.stars_price} Stars</span>
              </button>
              
              <button
                onClick={() => handlePayment('click')}
                disabled={purchasing}
                className="w-full p-4 bg-blue-100 text-blue-700 rounded-xl font-medium flex items-center justify-between"
              >
                <span>💳 Click</span>
                <span>{formatPrice(course.price)} so'm</span>
              </button>
              
              <button
                onClick={() => handlePayment('payme')}
                disabled={purchasing}
                className="w-full p-4 bg-cyan-100 text-cyan-700 rounded-xl font-medium flex items-center justify-between"
              >
                <span>💳 Payme</span>
                <span>{formatPrice(course.price)} so'm</span>
              </button>
              
              <button
                onClick={() => handlePayment('ton')}
                disabled={purchasing}
                className="w-full p-4 bg-purple-100 text-purple-700 rounded-xl font-medium flex items-center justify-between"
              >
                <span>💎 TON Crypto</span>
                <span>≈ {(course.price / 50000).toFixed(2)} TON</span>
              </button>
            </div>
            
            <button
              onClick={() => setShowPaymentModal(false)}
              className="w-full p-4 bg-telegram-secondary text-telegram-hint rounded-xl"
            >
              Bekor qilish
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
