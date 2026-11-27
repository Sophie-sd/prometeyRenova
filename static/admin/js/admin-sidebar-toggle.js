// Unfold (0.105+) тримає sidebarOpen як метод, а sidebarToggle робить
// `this.sidebarOpen = !this.sidebarOpen`. Заперечення функції дає false,
// тож перший клік на закритому меню нічого не змінює. На ширині <=1280
// метод завжди повертає false, і x-show лишає панель закритою.
// Обгортка підміняє метод булевим значенням до того, як Alpine читає x-data.
(function () {
    'use strict';

    document.addEventListener('alpine:init', function () {
        var original = window.theme;
        if (typeof original !== 'function' || original.__plSidebar) {
            return;
        }

        function readStoredOpen() {
            try {
                return localStorage.getItem('sidebarOpen') !== '0';
            } catch (err) {
                return true;
            }
        }

        function theme(defaultTheme) {
            var data = original(defaultTheme);
            if (!data || typeof data.sidebarToggle !== 'function') {
                return data;
            }

            var compute = data.sidebarOpen;
            var open = false;
            if (typeof compute === 'function') {
                open = !!compute.call(data);
            } else {
                open = !!compute;
            }
            data.sidebarOpen = open;

            data.sidebarToggle = function () {
                var current = this.sidebarOpen;
                if (typeof current === 'function') {
                    current = !!current.call(this);
                }
                this.sidebarOpen = !current;
                if (window.innerWidth > 1280) {
                    try {
                        localStorage.setItem('sidebarOpen', this.sidebarOpen ? '1' : '0');
                    } catch (err) {}
                }
            };

            var bindings = data.themeBindings;
            if (bindings) {
                bindings['x-resize.window'] = function () {
                    if (window.innerWidth <= 1280) {
                        return;
                    }
                    this.sidebarOpen = readStoredOpen();
                };
            }

            return data;
        }

        theme.__plSidebar = true;
        window.theme = theme;
    });
})();
