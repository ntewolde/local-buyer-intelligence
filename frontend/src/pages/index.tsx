/**
 * Home Page - Landing for unauthenticated, redirect to dashboard for authenticated
 */
import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { authService } from '../services/auth';
import LandingPage from './landing';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // If authenticated, redirect to dashboard
    if (authService.isAuthenticated()) {
      router.replace('/dashboard');
    }
  }, [router]);

  // Show landing page for unauthenticated users
  return <LandingPage />;
}
