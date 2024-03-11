self.addEventListener('push', function(event) {
    var data = event.data.json();
    var options = {
        body: data.body,
        icon: 'icon.png',
        badge: 'badge.png'
    };
    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

self.addEventListener('message', function(event) {
    var data = event.data;
    var options = {
        body: data.body,
        icon: 'icon.png',
        badge: 'badge.png'
    };
    self.registration.showNotification(data.title, options);
});
