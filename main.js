if ('serviceWorker' in navigator && 'PushManager' in window && 'Notification' in window) {
    console.log('Push notifications are supported');
  
    navigator.serviceWorker.register('/service-worker.js')
      .then(registration => {
        console.log('Service Worker registered');
  
        return registration.pushManager.getSubscription()
          .then(subscription => {
            if (subscription) {
              return subscription;  // Already subscribed
            }
  
            return registration.pushManager.subscribe({ userVisibleOnly: true });
          });
      })
      .then(subscription => {
        console.log('Subscribed to push notifications:', subscription);
        // Send the subscription object to your server to save it
      })
      .catch(error => {
        console.error('Error registering service worker or subscribing to push notifications:', error);
      });
  
    Notification.requestPermission().then(permission => {
      if (permission === 'granted') {
        console.log('Notification permission granted');
      } else {
        console.log('Notification permission denied');
      }
    });
  } else {
    console.log('Push notifications are not supported');
  }
  