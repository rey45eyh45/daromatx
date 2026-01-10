import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { lessonsApi, Lesson } from '../api'
import { useTelegram } from '../context/TelegramContext'
import Loading from '../components/Loading'

export default function LessonPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { showBackButton, hideBackButton, showAlert } = useTelegram()
  
  const [lesson, setLesson] = useState<Lesson | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (id) {
      loadLesson(parseInt(id))
    }

    showBackButton(() => navigate(-1))
    
    return () => {
      hideBackButton()
    }
  }, [id])

  const loadLesson = async (lessonId: number) => {
    try {
      const res = await lessonsApi.getById(lessonId)
      setLesson(res.data)
    } catch (error: any) {
      console.error('Error loading lesson:', error)
      if (error.response?.status === 403) {
        showAlert('Bu darsga kirishingiz yo\'q. Kursni sotib oling.')
      } else {
        showAlert('Dars topilmadi')
      }
      navigate(-1)
    } finally {
      setLoading(false)
    }
  }

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${minutes}:${secs.toString().padStart(2, '0')}`
  }

  if (loading) {
    return <Loading text="Dars yuklanmoqda..." />
  }

  if (!lesson) {
    return null
  }

  return (
    <div className="min-h-screen bg-black">
      {/* Video player */}
      <div className="relative aspect-video bg-gray-900 flex items-center justify-center">
        {lesson.video_url ? (
          <video
            src={lesson.video_url}
            controls
            autoPlay
            className="w-full h-full"
            onTimeUpdate={(e) => {
              const video = e.currentTarget
              // Update progress
              lessonsApi.updateProgress(lesson.id, Math.floor(video.currentTime), false)
            }}
            onEnded={() => {
              lessonsApi.updateProgress(lesson.id, lesson.duration, true)
              showAlert('🎉 Dars tugadi!')
            }}
          />
        ) : (
          <div className="text-center text-white">
            <span className="text-6xl block mb-4">🎥</span>
            <p>Video Telegram orqali yuboriladi</p>
            <p className="text-gray-400 text-sm mt-2">
              File ID: {lesson.video_file_id}
            </p>
          </div>
        )}
      </div>

      {/* Lesson info */}
      <div className="bg-telegram-bg p-4">
        <h1 className="text-xl font-bold text-telegram-text mb-2">
          {lesson.title}
        </h1>
        
        <div className="flex items-center gap-4 text-telegram-hint text-sm mb-4">
          <span>⏱ {formatDuration(lesson.duration)}</span>
          <span>📖 Dars #{lesson.order}</span>
        </div>
        
        {lesson.description && (
          <div className="p-4 bg-telegram-secondary rounded-xl">
            <h3 className="font-medium text-telegram-text mb-2">📝 Tavsif</h3>
            <p className="text-telegram-hint">{lesson.description}</p>
          </div>
        )}
      </div>
    </div>
  )
}
