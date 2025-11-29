// 简化的Service Worker
self.addEventListener('install', function(event) {
    console.log('Service Worker 安装完成');
});

self.addEventListener('fetch', function(event) {
    // 简单的缓存策略
    event.respondWith(
        fetch(event.request).catch(function() {
            return new Response('离线模式 - 中国象棋');
        })
    );
});
