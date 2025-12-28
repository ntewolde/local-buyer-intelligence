import '../styles/globals.css';
import type { AppProps } from 'next/app';
import { useRouter } from 'next/router';
import { useEffect } from 'react';
import { authService } from '../services/auth';

export default function App({ Component, pageProps }: AppProps) {
  const router = useRouter();

  useEffect(() => {
    // Redirect to login if not authenticated (except on login page)
    if (router.pathname !== '/login' && !authService.isAuthenticated()) {
      router.push('/login');
    }
  }, [router]);

  return <Component {...pageProps} />;
}
