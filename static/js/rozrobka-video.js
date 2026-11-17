(function () {
    var dialog = document.querySelector('[data-rs-video-dialog]');
    if (!dialog) return;
    var slot = dialog.querySelector('[data-rs-video-slot]');
    var closer = dialog.querySelector('[data-rs-video-close]');
    var last = null;

    function clearFrame() {
        if (slot) slot.replaceChildren();
    }

    function closeDialog() {
        clearFrame();
        if (dialog.open && typeof dialog.close === 'function') dialog.close();
        else dialog.removeAttribute('open');
        if (last && typeof last.focus === 'function') last.focus();
    }

    function openDialog(button) {
        var id = button.getAttribute('data-rs-video');
        if (!id || !slot) return;
        last = button;
        clearFrame();
        var frame = document.createElement('iframe');
        frame.referrerPolicy = 'strict-origin-when-cross-origin';
        frame.src = 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(id) + '?autoplay=1&playsinline=1&fs=0';
        frame.title = button.getAttribute('data-rs-video-title') || 'Відео';
        frame.setAttribute('allow', 'autoplay; encrypted-media; picture-in-picture');
        frame.width = '320';
        frame.height = '568';
        slot.appendChild(frame);
        if (typeof dialog.showModal === 'function') dialog.showModal();
        else dialog.setAttribute('open', '');
        if (closer) closer.focus();
    }

    document.addEventListener('click', function (event) {
        var button = event.target.closest('[data-rs-video]');
        if (button) {
            event.preventDefault();
            openDialog(button);
            return;
        }
        if (event.target.closest('[data-rs-video-close]')) closeDialog();
    });

    dialog.addEventListener('click', function (event) {
        if (event.target === dialog) closeDialog();
    });
    dialog.addEventListener('close', clearFrame);
    dialog.addEventListener('cancel', clearFrame);
}());
