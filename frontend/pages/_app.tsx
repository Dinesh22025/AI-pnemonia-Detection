/**
 * PneumoVision AI - App Entry Point
 * Configures Redux, Theme, and Global Layout
 */

import type { AppProps } from 'next/app';
import { Provider } from 'react-redux';
import { Toaster } from 'react-hot-toast';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Cookies from 'js-cookie';

import { store, useAppDispatch, setUser, setAuthLoading, setDarkMode } from '@/services/store';
import { authAPI } from '@/services/api';
import Layout from '@/components/layout/Layout';
import '@/styles/globals.css';

function AppContent({ Component, pageProps }: AppProps) {
  const dispatch = useAppDispatch();
  const router = useRouter();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    
    // Initialize theme
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const isDark = savedTheme === 'dark' || (!savedTheme && prefersDark);
    
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    dispatch(setDarkMode(isDark));

    // Check authentication
    const token = Cookies.get('access_token');
    if (token) {
      authAPI
        .getProfile()
        .then((res) => {
          dispatch(setUser(res.data));
        })
        .catch(() => {
          Cookies.remove('access_token');
          Cookies.remove('refresh_token');
          dispatch(setUser(null));
        })
        .finally(() => {
          dispatch(setAuthLoading(false));
        });
    } else {
      dispatch(setAuthLoading(false));
    }
  }, [dispatch]);

  if (!mounted) return null;

  // Pages that don't need the main layout
  const authPages = ['/login', '/signup', '/forgot-password'];
  const isAuthPage = authPages.includes(router.pathname);
  const isLandingPage = router.pathname === '/';

  if (isLandingPage || isAuthPage) {
    return (
      <>
        <Component {...pageProps} />
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              borderRadius: '12px',
              background: '#333',
              color: '#fff',
            },
          }}
        />
      </>
    );
  }

  return (
    <Layout>
      <Component {...pageProps} />
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            borderRadius: '12px',
            background: '#333',
            color: '#fff',
          },
        }}
      />
    </Layout>
  );
}

export default function App(appProps: AppProps) {
  return (
    <Provider store={store}>
      <AppContent {...appProps} />
    </Provider>
  );
}

