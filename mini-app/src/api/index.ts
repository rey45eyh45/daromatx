import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Telegram init data ni har bir so'rovga qo'shish
api.interceptors.request.use((config) => {
  const tg = window.Telegram?.WebApp
  if (tg?.initData) {
    config.headers['X-Telegram-Init-Data'] = tg.initData
  } else {
    // Development mode
    config.headers['X-Telegram-Init-Data'] = 'user=%7B%22id%22%3A123456789%7D'
  }
  return config
})

// Types
export interface Course {
  id: number
  title: string
  description: string
  price: number
  stars_price: number
  ton_price: number
  thumbnail: string | null
  category: string
  duration: number
  is_active: boolean
  lessons_count: number
  is_purchased?: boolean
}

export interface CourseDetail extends Course {
  lessons: Lesson[]
  is_purchased: boolean
}

export interface Lesson {
  id: number
  course_id?: number
  title: string
  description: string | null
  video_file_id?: string | null
  video_url?: string | null
  duration: number
  order: number
  is_free: boolean
}

export interface User {
  id: number
  telegram_id: number
  username: string | null
  full_name: string
  balance: number
  purchased_courses_count: number
}

export interface PurchasedCourse {
  id: number
  course_id: number
  course_title: string
  progress: number
  total_lessons?: number
  completed_lessons?: number
  thumbnail?: string
  purchased_at?: string
}

export interface Category {
  id: string
  name: string
  icon: string
}

export interface Payment {
  id: number
  course_id: number
  amount: number
  currency: string
  payment_type: string
  status: string
  payment_url?: string
}

// API functions
export const coursesApi = {
  getAll: (category?: string, search?: string) => 
    api.get<Course[]>('/courses', { params: { category, search } }),
  
  getById: (id: number) => 
    api.get<CourseDetail>(`/courses/${id}`),
  
  getCategories: () => 
    api.get<{ categories: Category[] }>('/courses/categories'),
}

export const usersApi = {
  getMe: () => 
    api.get<User>('/users/me'),
  
  getMyCourses: () => 
    api.get<PurchasedCourse[]>('/users/me/courses'),
}

export const lessonsApi = {
  getByCourse: (courseId: number) => 
    api.get<Lesson[]>(`/lessons/course/${courseId}`),
  
  getById: (id: number) => 
    api.get<Lesson>(`/lessons/${id}`),
  
  getVideoUrl: (id: number) =>
    api.get<{ video_url: string; type: string; expires?: number; token?: string; watermark?: string }>(`/lessons/${id}/video-url`),
  
  updateProgress: (id: number, watchedSeconds: number, isCompleted: boolean) =>
    api.post(`/lessons/${id}/progress`, { watched_seconds: watchedSeconds, is_completed: isCompleted }),
}

export const paymentsApi = {
  create: (courseId: number, paymentType: string) =>
    api.post<Payment>('/payments/create', { course_id: courseId, payment_type: paymentType }),
  
  checkStatus: (paymentId: number) =>
    api.get(`/payments/${paymentId}/status`),
  
  verifyTon: (courseId: number) =>
    api.post<{ success: boolean; message: string; course_id?: number; expected_amount?: number; wallet?: string; already_purchased?: boolean }>('/payments/ton/verify', { course_id: courseId }),
  
  getTonInfo: () =>
    api.get<{ wallet: string; rate: number; currency: string }>('/payments/ton/info'),
}

export const adminApi = {
  getStats: () => 
    api.get('/admin/stats'),
  
  createCourse: (data: { title: string; description: string; price: number; stars_price: number; ton_price: number; category: string }) =>
    api.post('/admin/courses', data),
  
  getCourses: () =>
    api.get<{ courses: AdminCourse[] }>('/admin/courses'),
  
  getCourseDetail: (id: number) =>
    api.get<AdminCourseDetail>(`/admin/courses/${id}`),
  
  deleteCourse: (id: number) =>
    api.delete(`/admin/courses/${id}`),
  
  createLesson: (courseId: number, data: { title: string; description?: string; order?: number; duration?: number; is_free?: boolean }) =>
    api.post(`/admin/courses/${courseId}/lessons`, data),
  
  deleteLesson: (id: number) =>
    api.delete(`/admin/lessons/${id}`),
  
  setLessonVideo: (lessonId: number, data: { video_file_id?: string; video_url?: string; duration?: number }) =>
    api.post(`/admin/lessons/${lessonId}/video`, data),
  
  uploadThumbnail: (courseId: number, file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/admin/courses/${courseId}/thumbnail`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  
  getUsers: (limit?: number, offset?: number) =>
    api.get('/admin/users', { params: { limit, offset } }),
}

// Admin types
export interface AdminCourse {
  id: number
  title: string
  description: string
  price: number
  stars_price: number
  ton_price: number
  thumbnail: string | null
  category: string
  is_active: boolean
  lessons_count: number
  created_at: string
}

export interface AdminLesson {
  id: number
  title: string
  description: string | null
  order: number
  duration: number
  is_free: boolean
  video_file_id: string | null
  has_video: boolean
}

export interface AdminCourseDetail extends AdminCourse {
  lessons: AdminLesson[]
}

export default api
