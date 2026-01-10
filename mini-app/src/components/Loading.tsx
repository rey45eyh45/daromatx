interface LoadingProps {
  text?: string
}

export default function Loading({ text = 'Yuklanmoqda...' }: LoadingProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <div className="animate-spin rounded-full h-10 w-10 border-4 border-telegram-button border-t-transparent mb-4"></div>
      <p className="text-telegram-hint text-sm">{text}</p>
    </div>
  )
}

export function SkeletonCard() {
  return (
    <div className="bg-telegram-bg rounded-2xl overflow-hidden">
      <div className="h-40 skeleton"></div>
      <div className="p-4 space-y-3">
        <div className="h-5 skeleton rounded w-3/4"></div>
        <div className="h-4 skeleton rounded w-full"></div>
        <div className="h-4 skeleton rounded w-2/3"></div>
        <div className="flex justify-between">
          <div className="h-6 skeleton rounded w-24"></div>
          <div className="h-4 skeleton rounded w-16"></div>
        </div>
      </div>
    </div>
  )
}
