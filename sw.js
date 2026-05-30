var CACHE = 'cet6-v2';
var BASE = self.location.pathname.replace(/\/[^/]*$/, '');

self.addEventListener('install', function(e) {
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

self.addEventListener('fetch', function(e) {
  e.respondWith(
    caches.match(e.request).then(function(r) {
      return r || fetch(e.request).then(function(resp) {
        if (resp.ok) {
          var clone = resp.clone();
          caches.open(CACHE).then(function(c) { c.put(e.request, clone); });
        }
        return resp;
      });
    })
  );
});
