/* =============================================
   QB7 Family Page — Service Worker
   Version: 1.0

   Purpose: Cache static assets for faster loading
   and offline shell display. Does NOT cache
   form submissions or dynamic data.
   ============================================= */

var CACHE_NAME = 'qb7-v123';

// Only cache files that never change (or change rarely).
// epa.js is NOT cached — it changes on every new post.
// msg_up.cgi and pic_up.php are NOT cached — they are server endpoints.
var STATIC_ASSETS = [
    'index.htm',
    'style.css',
    'radar.gif',
    'FacePics/Joe_M.JPG',
    'FacePics/Alys_FCC.JPG',
    'FacePics/J_FM.JPG',
    'FacePics/Viv.JPG',
    'FacePics/Colin.jpg',
    '../MBG.jpg'
];

// Install: pre-cache the static shell
self.addEventListener('install', function(event) {
    console.log('[SW] Installing v1');
    self.skipWaiting();
    event.waitUntil(
        caches.open(CACHE_NAME).then(function(cache) {
            console.log('[SW] Caching static assets');
            return cache.addAll(STATIC_ASSETS);
        })
    );
});

// Activate: clean up old caches when version changes
self.addEventListener('activate', function(event) {
    console.log('[SW] Activating v1');
    event.waitUntil(
        caches.keys().then(function(names) {
            return Promise.all(
                names.map(function(name) {
                    if (name !== CACHE_NAME) {
                        console.log('[SW] Deleting old cache:', name);
                        return caches.delete(name);
                    }
                })
            );
        }).then(function() { return self.clients.claim(); })
    );
});

// Fetch: network-first for everything, fall back to cache.
// This ensures fresh data (epa.js, posts) always comes from
// the server. Cache only kicks in when the network is unavailable.
//
// CRITICAL: POST requests (form submissions to msg_up.cgi and
// pic_up.php) are NEVER cached. Only GET requests are handled.
self.addEventListener('fetch', function(event) {

    // Never intercept POST requests — let them go straight to server
    if (event.request.method !== 'GET') {
        return;
    }

    // Never cache CGI or PHP endpoints even on GET
    var url = event.request.url;
    if (url.indexOf('msg_up.cgi') !== -1 || url.indexOf('pic_up.php') !== -1 || url.indexOf('del_posts.cgi') !== -1 || url.indexOf('save_profile_pic.php') !== -1 || url.indexOf('profiles.json') !== -1) {
        return;
    }

    // Network-first strategy:
    // Try the network. If it fails, serve from cache.
    event.respondWith(
        fetch(event.request).then(function(response) {
            // Got a good response — optionally update cache for static assets
            if (response.ok) {
                var responseClone = response.clone();
                caches.open(CACHE_NAME).then(function(cache) {
                    cache.put(event.request, responseClone);
                });
            }
            return response;
        }).catch(function() {
            // Network failed — try cache
            return caches.match(event.request);
        })
    );
});
