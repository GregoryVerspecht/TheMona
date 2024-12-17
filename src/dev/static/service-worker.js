self.addEventListener('install', function(event) {
  console.log('Service Worker installing.');
  event.waitUntil(
    caches.open('v1').then(function(cache) {
      return cache.addAll([
        '/',
        '/static/manifest.json',
        '/static/the_mona_concept_192.png',
        '/static/the_mona_concept_512.png'
      ]);
    })
  );
});

self.addEventListener('fetch', function(event) {
  console.log('Fetching:', event.request.url);
  event.respondWith(
    caches.match(event.request).then(function(response) {
      return response || fetch(event.request);
    })
  );
});
