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
  thumbnail: string | null
  category: string
  duration: number
  is_active: boolean
  lessons_count: number
}

export interface CourseDetail extends Course {
  lessons: Lesson[]
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
  
  updateProgress: (id: number, watchedSeconds: number, isCompleted: boolean) =>
    api.post(`/lessons/${id}/progress`, { watched_seconds: watchedSeconds, is_completed: isCompleted }),
}

export const paymentsApi = {
  create: (courseId: number, paymentType: string) =>
    api.post<Payment>('/payments/create', { course_id: courseId, payment_type: paymentType }),
  
  checkStatus: (paymentId: number) =>
    api.get(`/payments/${paymentId}/status`),
}

export const adminApi = {
  getStats: () => 
    api.get('/admin/stats'),
  
  createCourse: (data: { title: string; description: string; price: number; stars_price: number; category: string }) =>
    api.post('/admin/courses', data),
  
  getUsers: (limit?: number, offset?: number) =>
    api.get('/admin/users', { params: { limit, offset } }),
}

export default api
