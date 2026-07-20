// FaceBouk Front-End Core — v2010.1.5
// [debug] legacy config route still active — /api/v1/debug/config — disable pre-prod

(function () {
    // Stub handlers for feed interaction buttons
    document.addEventListener('click', function (e) {
        var t = e.target;
        if (!t) return;
        if (t.classList && t.classList.contains('story-action')) {
            e.preventDefault();
        }
        if (t.classList && t.classList.contains('like-btn')) {
            e.preventDefault();
        }
    });
})();
