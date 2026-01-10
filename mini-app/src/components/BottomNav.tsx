import { NavLink } from 'react-router-dom'
import { HomeIcon, CoursesIcon, MyCoursesIcon, ProfileIcon } from './Icons'

type NavItem = {
  to: string
  icon: typeof HomeIcon
  label: string
}

const navItems: NavItem[] = [
  { to: '/', icon: HomeIcon, label: 'Bosh sahifa' },
  { to: '/courses', icon: CoursesIcon, label: 'Kurslar' },
  { to: '/my-courses', icon: MyCoursesIcon, label: 'Mening' },
  { to: '/profile', icon: ProfileIcon, label: 'Profil' },
]

export default function BottomNav() {
  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-telegram-bg border-t border-telegram-secondary/30 backdrop-blur-lg bg-opacity-95 safe-area-bottom">
      <div className="flex justify-around items-center h-16 max-w-lg mx-auto px-2">
        {navItems.map((item) => {
          const IconComponent = item.icon
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex flex-col items-center justify-center w-full h-full transition-all duration-200 ${
                  isActive
                    ? 'text-telegram-button'
                    : 'text-telegram-hint hover:text-telegram-text'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <div className={`p-1.5 rounded-xl transition-all duration-200 ${isActive ? 'bg-telegram-button/15' : ''}`}>
                    <IconComponent 
                      size={22} 
                      className={`transition-transform duration-200 ${isActive ? 'scale-110' : ''}`}
                    />
                  </div>
                  <span className={`text-[10px] mt-0.5 font-medium ${isActive ? 'text-telegram-button' : ''}`}>
                    {item.label}
                  </span>
                </>
              )}
            </NavLink>
          )
        })}
      </div>
    </nav>
  )
}
