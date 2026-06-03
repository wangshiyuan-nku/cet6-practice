var CACHE = 'cet6-v2.3';
var BASE = self.location.pathname.replace(/\/[^/]*$/, '');

self.addEventListener('install', function(e) {
  self.skipWaiting();
  e.waitUntil(
    caches.open(CACHE).then(function(c) {
      return c.addAll([
        BASE + '/',
        BASE + '/index.html',
        BASE + '/data.js',
        BASE + '/index_data.js',
        BASE + '/manifest.json',
        BASE + '/icon-192.png',
        BASE + '/icon-512.png'
      ]);
    })
  );
});

// Delete old caches when new service worker activates
self.addEventListener('activate', function(e) {
  e.waitUntil(
    caches.keys().then(function(keys) {
      return Promise.all(keys.filter(function(k) { return k !== CACHE; }).map(function(k) { return caches.delete(k); }));
    }).then(function() { return clients.claim(); })
  );
});

// Network-first: only cache same-origin app assets
self.addEventListener('fetch', function(e) {
  if (e.request.method !== 'GET') return;
  var url = new URL(e.request.url);
  if (url.origin !== self.location.origin) return;
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
