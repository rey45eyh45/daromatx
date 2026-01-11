import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useTelegram } from '../context/TelegramContext'
import { usersApi, User } from '../api'
import Loading from '../components/Loading'
import { 
  VideoIcon, 
  CreditCardIcon, 
  AwardIcon, 
  SettingsIcon, 
  HelpIcon,
  ChevronRightIcon,
  BellIcon,
  StarIcon,
  CoursesIcon,
  BarChartIcon
} from '../components/Icons'

// Admin telegram IDs
const ADMIN_IDS = [5425876649, 123456789]

export default function ProfilePage() {
  const { user: tgUser } = useTelegram()
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadProfile()
  }, [])

  const loadProfile = async () => {
    try {
      const res = await usersApi.getMe()
      setUser(res.data)
    } catch (error) {
      console.error('Error loading profile:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatBalance = (balance: number) => {
    return new Intl.NumberFormat('uz-UZ').format(balance)
  }

  const displayUser = {
    full_name: user?.full_name || tgUser?.first_name || 'Foydalanuvchi',
    username: user?.username || tgUser?.username || 'username',
    balance: user?.balance || 150000,
    courses_count: user?.purchased_courses_count || 3,
    telegram_id: user?.telegram_id || tgUser?.id || 5425876649
  }

  if (loading) {
    return <Loading text="Profil yuklanmoqda..." />
  }

  return (
    <div className="min-h-screen bg-telegram-secondary/30 pb-24 overflow-x-hidden">
      {/* Profile header with gradient */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-telegram-button via-purple-600 to-indigo-700 h-48" />
        
        <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2" />
        <div className="absolute top-20 left-0 w-20 h-20 bg-white/5 rounded-full -translate-x-1/2" />
        
        <div className="relative z-10 px-5 pt-6 pb-4">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-white text-lg font-bold">Profil</h1>
            <button className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
              <BellIcon size={20} className="text-white" />
            </button>
          </div>

          {/* Profile card */}
          <div className="bg-telegram-bg rounded-3xl p-5 shadow-xl">
            <div className="flex items-center gap-4 mb-5">
              <div className="relative">
                <div className="w-20 h-20 bg-gradient-to-br from-telegram-button to-purple-600 rounded-2xl flex items-center justify-center text-3xl font-bold text-white shadow-lg">
                  {displayUser.full_name[0]?.toUpperCase()}
                </div>
                <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-green-500 rounded-lg flex items-center justify-center border-2 border-telegram-bg">
                  <span className="text-white text-xs">V</span>
                </div>
              </div>
              
              <div className="flex-1">
                <h2 className="text-xl font-bold text-telegram-text">
                  {displayUser.full_name}
                </h2>
                <p className="text-telegram-hint text-sm">
                  @{displayUser.username}
                </p>
                <div className="flex items-center gap-1 mt-1">
                  <StarIcon size={14} className="text-yellow-500" />
                  <span className="text-xs text-telegram-hint">Premium foydalanuvchi</span>
                </div>
              </div>
            </div>
            
            {/* Stats */}
            <div className="grid grid-cols-3 gap-3">
              <div className="bg-gradient-to-br from-blue-500/10 to-cyan-500/10 rounded-2xl p-3 text-center">
                <div className="w-10 h-10 mx-auto mb-2 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center">
                  <VideoIcon size={18} className="text-white" />
                </div>
                <span className="text-lg font-bold text-telegram-text block">{displayUser.courses_count}</span>
                <span className="text-[10px] text-telegram-hint">Kurslar</span>
              </div>
              
              <div className="bg-gradient-to-br from-green-500/10 to-emerald-500/10 rounded-2xl p-3 text-center">
                <div className="w-10 h-10 mx-auto mb-2 bg-gradient-to-br from-green-500 to-emerald-500 rounded-xl flex items-center justify-center">
                  <AwardIcon size={18} className="text-white" />
                </div>
                <span className="text-lg font-bold text-telegram-text block">2</span>
                <span className="text-[10px] text-telegram-hint">Sertifikat</span>
              </div>
              
              <div className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 rounded-2xl p-3 text-center">
                <div className="w-10 h-10 mx-auto mb-2 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
                  <CreditCardIcon size={18} className="text-white" />
                </div>
                <span className="text-lg font-bold text-telegram-text block">{formatBalance(displayUser.balance)}</span>
                <span className="text-[10px] text-telegram-hint">Balans</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="px-4 mt-4">
        <div className="grid grid-cols-2 gap-3">
          <Link
            to="/my-courses"
            className="bg-telegram-bg p-4 rounded-2xl flex items-center gap-3 shadow-sm hover:shadow-md transition-all active:scale-95"
          >
            <div className="w-12 h-12 bg-telegram-button/10 rounded-xl flex items-center justify-center">
              <CoursesIcon size={24} className="text-telegram-button" />
            </div>
            <div>
              <h3 className="font-semibold text-telegram-text text-sm">Kurslarim</h3>
              <p className="text-[10px] text-telegram-hint">{displayUser.courses_count} ta kurs</p>
            </div>
          </Link>
          
          <button
            className="bg-telegram-bg p-4 rounded-2xl flex items-center gap-3 shadow-sm hover:shadow-md transition-all active:scale-95"
          >
            <div className="w-12 h-12 bg-green-500/10 rounded-xl flex items-center justify-center">
              <CreditCardIcon size={24} className="text-green-500" />
            </div>
            <div className="text-left">
              <h3 className="font-semibold text-telegram-text text-sm">Balans</h3>
              <p className="text-[10px] text-telegram-hint">Hisob toldirish</p>
            </div>
          </button>
        </div>
      </div>

      {/* Admin Panel - faqat adminlar uchun */}
      {ADMIN_IDS.includes(displayUser.telegram_id) && (
        <div className="px-4 mt-6">
          <h3 className="text-sm font-semibold text-telegram-hint mb-3 px-1">🔐 Boshqaruv</h3>
          <div className="bg-telegram-bg rounded-2xl overflow-hidden shadow-sm">
            <Link to="/admin">
              <div className="flex items-center gap-4 p-4 hover:bg-telegram-secondary/50 transition-all active:bg-telegram-secondary bg-gradient-to-r from-red-500/5 to-orange-500/5">
                <div className="w-10 h-10 bg-gradient-to-br from-red-500 to-orange-500 rounded-xl flex items-center justify-center">
                  <BarChartIcon size={20} className="text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="font-medium text-telegram-text text-sm">Admin Panel</h3>
                  <p className="text-telegram-hint text-xs">Kurslar va foydalanuvchilarni boshqarish</p>
                </div>
                <ChevronRightIcon size={18} className="text-telegram-hint" />
              </div>
            </Link>
          </div>
        </div>
      )}

      {/* Menu items */}
      <div className="px-4 mt-6">
        <h3 className="text-sm font-semibold text-telegram-hint mb-3 px-1">Sozlamalar</h3>
        <div className="bg-telegram-bg rounded-2xl overflow-hidden shadow-sm">
          <MenuItem 
            icon={<CreditCardIcon size={20} className="text-orange-500" />}
            bgColor="bg-orange-500/10"
            title="Tolovlar tarixi" 
            subtitle="Barcha tolovlar" 
          />
          <MenuItem 
            icon={<AwardIcon size={20} className="text-purple-500" />}
            bgColor="bg-purple-500/10"
            title="Sertifikatlarim" 
            subtitle="Olingan sertifikatlar" 
          />
          <MenuItem 
            icon={<BellIcon size={20} className="text-blue-500" />}
            bgColor="bg-blue-500/10"
            title="Bildirishnomalar" 
            subtitle="Push xabarlar" 
          />
          <MenuItem 
            icon={<SettingsIcon size={20} className="text-gray-500" />}
            bgColor="bg-gray-500/10"
            title="Sozlamalar" 
            subtitle="Til va mavzu" 
            isLast
          />
        </div>
      </div>

      {/* Support */}
      <div className="px-4 mt-6">
        <h3 className="text-sm font-semibold text-telegram-hint mb-3 px-1">Yordam</h3>
        <div className="bg-telegram-bg rounded-2xl overflow-hidden shadow-sm">
          <MenuItem 
            icon={<HelpIcon size={20} className="text-teal-500" />}
            bgColor="bg-teal-500/10"
            title="Yordam markazi" 
            subtitle="FAQ va qollab-quvvatlash" 
          />
          <MenuItem 
            icon={<HelpIcon size={20} className="text-telegram-button" />}
            bgColor="bg-telegram-button/10"
            title="Telegram support" 
            subtitle="@daromatx_support" 
            isLast
          />
        </div>
      </div>

      {/* Footer info */}
      <div className="mt-8 text-center px-4">
        <div className="inline-flex items-center gap-2 bg-telegram-bg px-4 py-2 rounded-full shadow-sm">
          <span className="text-telegram-hint text-xs">ID: {displayUser.telegram_id}</span>
        </div>
        <p className="mt-4 text-telegram-hint text-xs">
          DAROMATX Academy v1.0
        </p>
        <p className="text-telegram-hint/50 text-[10px] mt-1">
          2026 Barcha huquqlar himoyalangan
        </p>
      </div>
    </div>
  )
}

interface MenuItemProps {
  icon: React.ReactNode
  bgColor: string
  title: string
  subtitle: string
  to?: string
  isLast?: boolean
}

function MenuItem({ icon, bgColor, title, subtitle, to, isLast }: MenuItemProps) {
  const content = (
    <div className={`flex items-center gap-4 p-4 hover:bg-telegram-secondary/50 transition-all active:bg-telegram-secondary ${!isLast ? 'border-b border-telegram-secondary/50' : ''}`}>
      <div className={`w-10 h-10 ${bgColor} rounded-xl flex items-center justify-center`}>
        {icon}
      </div>
      <div className="flex-1">
        <h3 className="font-medium text-telegram-text text-sm">{title}</h3>
        <p className="text-telegram-hint text-xs">{subtitle}</p>
      </div>
      <ChevronRightIcon size={18} className="text-telegram-hint" />
    </div>
  )

  if (to) {
    return <Link to={to}>{content}</Link>
  }

  return <button className="w-full text-left">{content}</button>
}
