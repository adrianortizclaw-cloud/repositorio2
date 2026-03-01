import { useEffect } from 'react';
import { apiClient } from '../utils/apiClient';

export function useAutoRefresh(token, onTokenUpdate) {
  useEffect(() => {
    if (!token) return;
    let interval = setInterval(async () => {
      const response = await apiClient(token)('/auth/refresh', { method: 'POST' });
      if (response.ok) {
        const payload = await response.json();
        onTokenUpdate(payload.access_token);
      }
    }, 1000 * 60 * 5);
    return () => clearInterval(interval);
  }, [token, onTokenUpdate]);
}
