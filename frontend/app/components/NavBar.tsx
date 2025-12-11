'use client'

import Link from 'next/link'
import Image from 'next/image'
import { useAuth } from './AuthProvider'

export default function NavBar() {
  const { user, loading, signOut } = useAuth()

  return (
    <nav className="fixed top-0 w-full bg-white border-b border-[#b48c5c] z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-2">
            <Link href="/" className="flex items-center space-x-2">
              <div className="relative w-50 h-50">
                <Image
                  src="/logo.png"
                  alt="Infinity8 Logo"
                  fill
                  className="object-contain"
                />
              </div>
            </Link>
          </div>
          <div className="hidden md:flex space-x-8">
            <a href="#spaces" className="text-gray-600 hover:text-[#b48c5c] transition">Spaces</a>
            <a href="#amenities" className="text-gray-600 hover:text-[#b48c5c] transition">Amenities</a>
            <a href="#pricing" className="text-gray-600 hover:text-[#b48c5c] transition">Pricing</a>
            <a href="#contact" className="text-gray-600 hover:text-[#b48c5c] transition">Contact</a>
          </div>
          <div className="flex items-center space-x-4">
            {loading ? (
              <div className="w-20 h-10 bg-gray-100 animate-pulse rounded-lg" />
            ) : user ? (
              <>
                <Link 
                  href="/dashboard" 
                  className="text-gray-600 hover:text-[#b48c5c] transition font-medium"
                >
                  Dashboard
                </Link>
                <button
                  onClick={signOut}
                  className="text-gray-600 hover:text-gray-900 transition"
                >
                  Sign out
                </button>
              </>
            ) : (
              <>
                <Link 
                  href="/auth/login" 
                  className="text-gray-600 hover:text-[#b48c5c] transition font-medium"
                >
                  Sign in
                </Link>
                <Link 
                  href="/auth/signup" 
                  className="bg-[#b48c5c] hover:bg-[#9a7450] text-white px-6 py-2 rounded-lg transition font-medium"
                >
                  Get Started
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}