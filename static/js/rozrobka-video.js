(function () {
    'use strict';

    var dialog = document.getElementById('pl-rs-video-dialog');
    if (!dialog || typeof dialog.showModal !== 'function') {
        return;
    }

    var frame = dialog.querySelector('[data-pl-rs-video-frame]');
    var title = document.getElementById('pl-rs-video-dialog-title');
    var closeBtn = dialog.querySelector('[data-pl-rs-video-close]');
    var idPattern = /^[A-Za-z0-9_-]{6,}$/;

    function stopVideo() {
        if (frame) {
            frame.replaceChildren();
        }
    }

    document.addEventListener('click', function (event) {
        var button = event.target.closest('[data-pl-rs-video]');
        if (!button || !frame) {
            return;
        }
        var videoId = button.getAttribute('data-pl-rs-video') || '';
        if (!idPattern.test(videoId)) {
            return;
        }
        var label = button.getAttribute('aria-label') || '';
        if (title) {
            title.textContent = label;
        }
        stopVideo();
        var iframe = document.createElement('iframe');
        iframe.src = 'https://www.youtube-nocookie.com/embed/' + videoId + '?autoplay=1&playsinline=1&rel=0';
        iframe.title = label;
        iframe.setAttribute('allow', 'autoplay; encrypted-media; picture-in-picture');
        iframe.setAttribute('allowfullscreen', '');
        iframe.setAttribute('referrerpolicy', 'strict-origin-when-cross-origin');
        frame.appendChild(iframe);
        dialog.showModal();
    });

    if (closeBtn) {
        closeBtn.addEventListener('click', function () {
            dialog.close();
        });
    }

    dialog.addEventListener('close', stopVideo);
})();
