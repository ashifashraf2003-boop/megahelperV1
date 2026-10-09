const CACHE_NAME = 'phone-check-v1';

self.addEventListener('install', (e) => {
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(clients.claim());
});

self.addEventListener('fetch', (e) => {
  // Let network requests pass through
  e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
});
