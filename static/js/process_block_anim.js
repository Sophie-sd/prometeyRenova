(function (global) {
    'use strict';

    var NUM_REVEAL_DURATION = 120;

    function setupWatermarkNum(el) {
        if (!el || el.dataset.pbWatermark === '1') {
            return;
        }

        var text = (el.textContent || '').trim();
        if (!text) {
            return;
        }

        el.dataset.pbWatermark = '1';
        el.dataset.pbNumValue = text;
        el.setAttribute('aria-label', text);
    }

    function resetWatermarkNum(el) {
        if (!el) {
            return;
        }

        el.classList.remove('is-num-reveal');
    }

    function showNumInstant(el) {
        if (!el) {
            return;
        }

        el.classList.add('is-num-reveal');
    }

    function playNumSequence(el, my, tokenRef, waitFn) {
        if (!el) {
            return Promise.resolve(true);
        }

        resetWatermarkNum(el);
        void el.offsetWidth;

        if (my !== tokenRef) {
            return Promise.resolve(false);
        }

        el.classList.add('is-num-reveal');

        return waitFn(NUM_REVEAL_DURATION).then(function () {
            return my === tokenRef;
        });
    }

    function setupTypewriterTitle(el) {
        if (!el || el.dataset.pbType === '1') {
            return;
        }

        var text = (el.textContent || '').trim();
        if (!text) {
            return;
        }

        el.dataset.pbType = '1';
        el.setAttribute('aria-label', text);
        el.textContent = '';

        var inFirstWord = true;

        for (var i = 0; i < text.length; i++) {
            var ch = text.charAt(i);
            var span = document.createElement('span');
            span.className = 'pb-type-letter';
            span.setAttribute('aria-hidden', 'true');

            if (ch === ' ') {
                span.classList.add('pb-type-letter--space');
                span.textContent = '\u00a0';
                inFirstWord = false;
            } else {
                span.textContent = ch;
                if (inFirstWord) {
                    span.classList.add('pb-type-letter--accent');
                }
            }

            el.appendChild(span);
        }

        var cursor = document.createElement('span');
        cursor.className = 'pb-type-cursor';
        cursor.setAttribute('aria-hidden', 'true');
        el.appendChild(cursor);
    }

    function resetTypewriterIn(root) {
        if (!root) {
            return;
        }

        root.querySelectorAll('.pb-step__title').forEach(function (title) {
            title.classList.remove('is-typing', 'is-typed');
        });

        root.querySelectorAll('.pb-type-letter.is-shown').forEach(function (letter) {
            letter.classList.remove('is-shown');
        });
    }

    function showTypewriterInstant(root) {
        if (!root) {
            return;
        }

        root.querySelectorAll('.pb-step__title').forEach(function (title) {
            title.classList.remove('is-typing');
            title.classList.add('is-typed');
        });

        root.querySelectorAll('.pb-type-letter').forEach(function (letter) {
            letter.classList.add('is-shown');
        });
    }

    function revealTypewriterEl(el, gap, my, tokenRef, waitFn) {
        if (!el) {
            return Promise.resolve(true);
        }

        el.classList.remove('is-typed');
        el.classList.add('is-typing');

        var letters = el.querySelectorAll('.pb-type-letter');
        var chain = Promise.resolve(true);

        for (var i = 0; i < letters.length; i++) {
            (function (letter, index) {
                chain = chain.then(function (ok) {
                    if (!ok || my !== tokenRef) {
                        return false;
                    }

                    letter.classList.add('is-shown');

                    if (index >= letters.length - 1) {
                        return true;
                    }

                    return waitFn(gap).then(function () {
                        return my === tokenRef;
                    });
                });
            })(letters[i], i);
        }

        return chain.then(function (ok) {
            if (!ok || my !== tokenRef) {
                return false;
            }

            el.classList.remove('is-typing');
            el.classList.add('is-typed');
            return true;
        });
    }

    function typewriterPhaseTail(el, gap, phaseDuration) {
        var letters = el ? el.querySelectorAll('.pb-type-letter') : [];
        var stagger = letters.length > 1 ? (letters.length - 1) * gap : 0;
        return Math.max(0, phaseDuration - stagger);
    }

    global.PbProcessAnim = {
        NUM_REVEAL_DURATION: NUM_REVEAL_DURATION,
        setupWatermarkNum: setupWatermarkNum,
        resetWatermarkNum: resetWatermarkNum,
        showNumInstant: showNumInstant,
        playNumSequence: playNumSequence,
        setupTypewriterTitle: setupTypewriterTitle,
        resetTypewriterIn: resetTypewriterIn,
        showTypewriterInstant: showTypewriterInstant,
        revealTypewriterEl: revealTypewriterEl,
        typewriterPhaseTail: typewriterPhaseTail
    };
})(typeof window !== 'undefined' ? window : this);
