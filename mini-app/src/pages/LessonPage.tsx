import { useEffect, useState, useRef, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { lessonsApi, Lesson } from '../api'
import { useTelegram } from '../context/TelegramContext'
import Loading from '../components/Loading'

export default function LessonPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { showBackButton, hideBackButton, showAlert, user } = useTelegram()
  
  const [lesson, setLesson] = useState<Lesson | null>(null)
  const [loading, setLoading] = useState(true)
  const [videoUrl, setVideoUrl] = useState<string | null>(null)
  const [videoLoading, setVideoLoading] = useState(false)
  const [videoError, setVideoError] = useState<string | null>(null)
  
  // Video player state
  const videoRef = useRef<HTMLVideoElement>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [showControls, setShowControls] = useState(true)
  const controlsTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const lastProgressUpdate = useRef<number>(0)

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
      
      // If lesson has video_file_id, load video URL
      if (res.data.video_file_id) {
        loadVideoUrl(lessonId)
      }
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

  const loadVideoUrl = async (lessonId: number) => {
    setVideoLoading(true)
    setVideoError(null)
    try {
      const res = await lessonsApi.getVideoUrl(lessonId)
      setVideoUrl(res.data.video_url)
    } catch (error: any) {
      console.error('Error loading video:', error)
      setVideoError(error.response?.data?.detail || 'Video yuklanmadi')
    } finally {
      setVideoLoading(false)
    }
  }

  // Hide controls after 3 seconds of inactivity
  const resetControlsTimeout = useCallback(() => {
    if (controlsTimeoutRef.current) {
      clearTimeout(controlsTimeoutRef.current)
    }
    setShowControls(true)
    if (isPlaying) {
      controlsTimeoutRef.current = setTimeout(() => {
        setShowControls(false)
      }, 3000)
    }
  }, [isPlaying])

  const handlePlayPause = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause()
      } else {
        videoRef.current.play()
      }
    }
  }

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime)
      
      // Update progress every 10 seconds
      const now = Date.now()
      if (now - lastProgressUpdate.current > 10000 && lesson) {
        lastProgressUpdate.current = now
        lessonsApi.updateProgress(lesson.id, Math.floor(videoRef.current.currentTime), false)
      }
    }
  }

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = parseFloat(e.target.value)
    if (videoRef.current) {
      videoRef.current.currentTime = time
      setCurrentTime(time)
    }
  }

  const handleVideoEnd = () => {
    if (lesson) {
      lessonsApi.updateProgress(lesson.id, lesson.duration, true)
      showAlert('🎉 Dars tugadi!')
    }
  }

  const toggleFullscreen = () => {
    if (videoRef.current) {
      if (document.fullscreenElement) {
        document.exitFullscreen()
      } else {
        videoRef.current.requestFullscreen()
      }
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  if (loading) {
    return <Loading text="Dars yuklanmoqda..." />
  }

  if (!lesson) {
    return null
  }

  return (
    <div className="min-h-screen bg-black">
      {/* Video player container */}
      <div 
        className="relative aspect-video bg-gray-900"
        onClick={resetControlsTimeout}
        onMouseMove={resetControlsTimeout}
      >
        {videoLoading ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center text-white">
              <div className="animate-spin w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
              <p>Video yuklanmoqda...</p>
            </div>
          </div>
        ) : videoError ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center text-white p-4">
              <span className="text-5xl block mb-4">⚠️</span>
              <p className="text-red-400 mb-4">{videoError}</p>
              <button
                onClick={() => lesson && loadVideoUrl(lesson.id)}
                className="px-4 py-2 bg-blue-500 rounded-lg"
              >
                Qayta urinish
              </button>
            </div>
          </div>
        ) : videoUrl ? (
          <>
            {/* Video element */}
            <video
              ref={videoRef}
              src={videoUrl}
              className="w-full h-full"
              playsInline
              onPlay={() => setIsPlaying(true)}
              onPause={() => setIsPlaying(false)}
              onTimeUpdate={handleTimeUpdate}
              onLoadedMetadata={() => {
                if (videoRef.current) {
                  setDuration(videoRef.current.duration)
                }
              }}
              onEnded={handleVideoEnd}
              onClick={handlePlayPause}
            />

            {/* Watermark */}
            <div className="absolute top-4 right-4 text-white/30 text-sm pointer-events-none select-none">
              ID: {user?.id || 'USER'}
            </div>

            {/* Custom controls overlay */}
            <div 
              className={`absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4 transition-opacity duration-300 ${showControls ? 'opacity-100' : 'opacity-0'}`}
            >
              {/* Progress bar */}
              <input
                type="range"
                min={0}
                max={duration || 100}
                value={currentTime}
                onChange={handleSeek}
                className="w-full h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer mb-3"
                style={{
                  background: `linear-gradient(to right, #3b82f6 ${(currentTime / duration) * 100}%, #4b5563 ${(currentTime / duration) * 100}%)`
                }}
              />

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  {/* Play/Pause */}
                  <button
                    onClick={handlePlayPause}
                    className="text-white text-2xl"
                  >
                    {isPlaying ? '⏸️' : '▶️'}
                  </button>

                  {/* Time */}
                  <span className="text-white text-sm">
                    {formatTime(currentTime)} / {formatTime(duration)}
                  </span>
                </div>

                {/* Fullscreen */}
                <button
                  onClick={toggleFullscreen}
                  className="text-white text-xl"
                >
                  ⛶
                </button>
              </div>
            </div>

            {/* Center play button */}
            {!isPlaying && showControls && (
              <div 
                className="absolute inset-0 flex items-center justify-center cursor-pointer"
                onClick={handlePlayPause}
              >
                <div className="w-20 h-20 bg-blue-500/80 rounded-full flex items-center justify-center">
                  <span className="text-4xl text-white ml-1">▶</span>
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="absolute inset-0 flex items-center justify-center text-center text-white">
            <div>
              <span className="text-6xl block mb-4">🎥</span>
              <p>Video mavjud emas</p>
            </div>
          </div>
        )}
      </div>

      {/* Lesson info */}
      <div className="bg-telegram-bg p-4">
        <h1 className="text-xl font-bold text-telegram-text mb-2">
          {lesson.title}
        </h1>
        
        <div className="flex items-center gap-4 text-telegram-hint text-sm mb-4">
          <span>⏱ {formatTime(lesson.duration)}</span>
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
