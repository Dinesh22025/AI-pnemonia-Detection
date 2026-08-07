/**
 * Main Layout Component
 * Provides consistent layout with sidebar, header, and content area
 */

import React, { ReactNode, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { motion, AnimatePresence } from 'framer-motion';
import Cookies from 'js-cookie';
import toast from 'react-hot-toast';

import { useAppSelector, useAppDispatch, logout, toggleSidebar, setUser, toggleDarkMode } from '@/services/store';
import { authAPI } from '@/services/api';

interface LayoutProps {
  children: ReactNode;
}

const sidebarLinks = [
  { href: '/dashboard', label: 'Dashboard', icon: '📊' },
  { href: '/predict', label: 'New Prediction', icon: '🔬' },
  { href: '/history', label: 'History', icon: '📋' },
  { href: '/reports', label: 'Reports', icon: '📄' },
  { href: '/profile', label: 'Profile', icon: '👤' },
];

const adminLinks = [
  { href: '/admin', label: 'Admin Dashboard', icon: '⚙️' },
  { href: '/admin/users', label: 'User Management', icon: '👥' },
  { href: '/admin/analytics', label: 'Analytics', icon: '📈' },
];

export default function Layout({ children }: LayoutProps) {
  const router = useRouter();
  const dispatch = useAppDispatch();
  const { user, isAuthenticated } = useAppSelector((state: any) => state.auth);
  const { darkMode, sidebarOpen } = useAppSelector((state: any) => state.ui);
  const [profileOpen, setProfileOpen] = useState(false);

  const handleLogout = async () => {
    try {
      await authAPI.logout();
    } catch (e) {
      // Ignore errors
    }
    Cookies.remove('access_token');
    Cookies.remove('refresh_token');
    dispatch(logout());
    toast.success('Logged out successfully');
    router.push('/login');
  };

  const toggleTheme = () => {
    const newDark = !darkMode;
    dispatch(toggleDarkMode());
    localStorage.setItem('theme', newDark ? 'dark' : 'light');
    if (newDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  if (!isAuthenticated) {
    return <>{children}</>;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0, x: -300 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -300 }}
            className="fixed inset-0 z-50 lg:static lg:inset-auto"
          >
            {/* Backdrop */}
            <div
              className="absolute inset-0 bg-black/50 lg:hidden"
              onClick={() => dispatch(toggleSidebar())}
            />
            
            {/* Sidebar content */}
            <aside className="relative w-72 h-full bg-white dark:bg-gray-800 shadow-xl overflow-y-auto">
              <div className="p-6">
                <Link href="/dashboard" className="flex items-center gap-3 mb-8">
                  <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-accent-500 rounded-xl flex items-center justify-center text-white font-bold text-lg">
                    PV
                  </div>
                  <div>
                    <h2 className="text-lg font-bold text-gray-800 dark:text-white">PneumoVision</h2>
                    <p className="text-xs text-gray-500 dark:text-gray-400">AI Healthcare</p>
                  </div>
                </Link>

                <nav className="space-y-1">
                  {sidebarLinks.map((link) => {
                    const isActive = router.pathname === link.href;
                    return (
                      <Link
                        key={link.href}
                        href={link.href}
                        className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${
                          isActive
                            ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400 font-semibold'
                            : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700/50'
                        }`}
                        onClick={() => dispatch(toggleSidebar())}
                      >
                        <span className="text-xl">{link.icon}</span>
                        <span>{link.label}</span>
                      </Link>
                    );
                  })}

                  {user?.role === 'admin' && (
                    <>
                      <div className="my-4 px-4">
                        <div className="h-px bg-gray-200 dark:bg-gray-700" />
                      </div>
                      <p className="px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
                        Admin
                      </p>
                      {adminLinks.map((link) => {
                        const isActive = router.pathname === link.href;
                        return (
                          <Link
                            key={link.href}
                            href={link.href}
                            className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${
                              isActive
                                ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400 font-semibold'
                                : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700/50'
                            }`}
                            onClick={() => dispatch(toggleSidebar())}
                          >
                            <span className="text-xl">{link.icon}</span>
                            <span>{link.label}</span>
                          </Link>
                        );
                      })}
                    </>
                  )}
                </nav>
              </div>
            </aside>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main content */}
      <div className="lg:pl-72">
        {/* Header */}
        <header className="sticky top-0 z-40 glass border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between px-4 md:px-6 h-16">
            <button
              onClick={() => dispatch(toggleSidebar())}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              <svg className="w-6 h-6 text-gray-600 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>

            <div className="flex items-center gap-3">
              {/* Theme toggle */}
              <button
                onClick={toggleTheme}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              >
                {darkMode ? (
                  <svg className="w-5 h-5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5 text-gray-600" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
                  </svg>
                )}
              </button>

              {/* Profile dropdown */}
              <div className="relative">
                <button
                  onClick={() => setProfileOpen(!profileOpen)}
                  className="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                  <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-accent-500 rounded-full flex items-center justify-center text-white font-semibold text-sm">
                    {user?.name?.charAt(0) || 'U'}
                  </div>
                  <div className="hidden md:block text-left">
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-200">{user?.name}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 capitalize">{user?.role}</p>
                  </div>
                </button>

                {profileOpen && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="absolute right-0 mt-2 w-64 bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-100 dark:border-gray-700 overflow-hidden"
                  >
                    <div className="p-4 border-b border-gray-100 dark:border-gray-700">
                      <p className="font-semibold text-gray-800 dark:text-white">{user?.name}</p>
                      <p className="text-sm text-gray-500">{user?.email}</p>
                    </div>
                    <div className="p-2">
                      <Link
                        href="/profile"
                        className="flex items-center gap-3 px-4 py-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                        onClick={() => setProfileOpen(false)}
                      >
                        <span>👤</span>
                        <span className="text-sm text-gray-700 dark:text-gray-200">Profile</span>
                      </Link>
                      <button
                        onClick={handleLogout}
                        className="w-full flex items-center gap-3 px-4 py-2 rounded-xl hover:bg-red-50 dark:hover:bg-red-900/20 text-red-600 transition-colors"
                      >
                        <span>🚪</span>
                        <span className="text-sm">Logout</span>
                      </button>
                    </div>
                  </motion.div>
                )}
              </div>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="p-4 md:p-6 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  );
}

