import '../styles/globals.css';
import type { AppProps } from 'next/app';
import { useRouter } from 'next/router';
import { useEffect } from 'react';
import { authService } from '../services/auth';

// Pages that don't require authentication
const publicPages = ['/', '/login', '/landing'];

export default function App({ Component, pageProps }: AppProps) {
  const router = useRouter();

  useEffect(() => {
    // Skip auth check for public pages
    const isPublicPage = publicPages.includes(router.pathname);

    if (!isPublicPage && !authService.isAuthenticated()) {
      router.push('/login');
    }
  }, [router]);

  return <Component {...pageProps} />;
}
