var CACHE = 'cet6-v2.3';
var BASE = self.location.pathname.replace(/\/[^/]*$/, '');

self.addEventListener('install', function(e) {
  self.skipWaiting();
  e.waitUntil(
    caches.open(CACHE).then(function(c) {
      // Don't pre-cache index.html — it must always be fresh.
      // Pre-cache large static data files that rarely change.
      return c.addAll([
        BASE + '/data.js',
        BASE + '/index_data.js',
        BASE + '/manifest.json',
        BASE + '/icon-192.png',
        BASE + '/icon-512.png'
      ]);
    })
  );
});

// Delete all old caches when new service worker activates
self.addEventListener('activate', function(e) {
  e.waitUntil(
    caches.keys().then(function(keys) {
      return Promise.all(keys.map(function(k) { return caches.delete(k); }));
    }).then(function() { return clients.claim(); })
  );
});

self.addEventListener('message', function(e) {
  if (e.data === 'skipWaiting') self.skipWaiting();
});

self.addEventListener('fetch', function(e) {
  if (e.request.method !== 'GET') return;
  var url = new URL(e.request.url);
  if (url.origin !== self.location.origin) return;

  // HTML: network-first, never cache — always get the latest version
  if (e.request.mode === 'navigate' || e.request.destination === 'document') {
    e.respondWith(
      fetch(e.request).catch(function() {
        return caches.match(e.request);
      })
    );
    return;
  }

  // Other assets: network-first with cache fallback
  e.respondWith(
    fetch(e.request).then(function(resp) {
      if (resp.ok) {
        var clone = resp.clone();
        caches.open(CACHE).then(function(c) { c.put(e.request, clone); });
      }
      return resp;
    }).catch(function() {
      return caches.match(e.request);
    })
  );
});
