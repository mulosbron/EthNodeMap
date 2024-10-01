const app = (() => {
    const API_URL = 'http://127.0.0.1:5001';
    const darkMode = (() => {
        let themeState = {
            isDarkMode: false
        };
        const getStoredTheme = () => {
            try {
                return localStorage.getItem('dark-mode');
            } catch (error) {
                console.error('Error accessing localStorage:', error);
                return null;
            }
        };
        const saveThemeToLocalStorage = (theme) => {
            try {
                localStorage.setItem('dark-mode', theme ? 'enabled' : 'disabled');
            } catch (error) {
                console.error('Error saving to localStorage:', error);
            }
        };
        const addDarkModeClass = () => {
            try {
                document.documentElement.classList.add('dark-mode');
            } catch (error) {
                console.error('Error adding dark-mode class:', error);
            }
        };
        const removeDarkModeClass = () => {
            try {
                document.documentElement.classList.remove('dark-mode');
            } catch (error) {
                console.error('Error removing dark-mode class:', error);
            }
        };
        const updateIconToMoon = () => {
            const iconSidebar = document.getElementById('mode-icon-sidebar');
            if (iconSidebar) {
                iconSidebar.classList.remove('sun');
                iconSidebar.classList.add('moon');
            } else {
                console.error('Icon element not found');
            }
            const icon = document.getElementById('mode-icon');
            if (icon) {
                icon.classList.remove('sun');
                icon.classList.add('moon');
            } else {
                console.error('Icon element not found');
            }
        };
        const updateIconToSun = () => {
            const iconSidebar = document.getElementById('mode-icon-sidebar');
            if (iconSidebar) {
                iconSidebar.classList.remove('moon');
                iconSidebar.classList.add('sun');
            } else {
                console.error('Icon element not found');
            }
            const icon = document.getElementById('mode-icon');
            if (icon) {
                icon.classList.remove('moon');
                icon.classList.add('sun');
            } else {
                console.error('Icon element not found');
            }
        };
        const updateLogoForDarkMode = () => {
            const logoContainer = document.querySelector('header div.logo svg');
            if (logoContainer) {
                logoContainer.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xodm="http://www.corel.com/coreldraw/odm/2003" xml:space="preserve" width="100%" height="100%" version="1.1" shape-rendering="geometricPrecision" text-rendering="geometricPrecision" image-rendering="optimizeQuality" fill-rule="evenodd" clip-rule="evenodd" viewBox="0 0 784.37 1277.39"><script xmlns="" id="star-key-wallet" type="module" data-extension-id="hcjhpkgbmechpabifbggldplacolbkoh" data-extension-url="chrome-extension://hcjhpkgbmechpabifbggldplacolbkoh/" src="chrome-extension://hcjhpkgbmechpabifbggldplacolbkoh/scripts/injectScript.js"/><script xmlns=""/>
            <g id="Layer_x0020_1">
            <metadata id="CorelCorpID_0Corel-Layer"/>
            <g id="_1421394342400">
            <g>
                <polygon fill="#343434" fill-rule="nonzero" points="392.07,0 383.5,29.11 383.5,873.74 392.07,882.29 784.13,650.54 "/>
                <polygon fill="#8C8C8C" fill-rule="nonzero" points="392.07,0 -0,650.54 392.07,882.29 392.07,472.33 "/>
                <polygon fill="#3C3C3B" fill-rule="nonzero" points="392.07,956.52 387.24,962.41 387.24,1263.28 392.07,1277.38 784.37,724.89 "/>
                <polygon fill="#8C8C8C" fill-rule="nonzero" points="392.07,1277.38 392.07,956.52 -0,724.89 "/>
                <polygon fill="#141414" fill-rule="nonzero" points="392.07,882.29 784.13,650.54 392.07,472.33 "/>
                <polygon fill="#393939" fill-rule="nonzero" points="0,650.54 392.07,882.29 392.07,472.33 "/>
            </g>
            </g>
            </g>
            </svg>`;
            } else {
                console.error('Logo element not found');
            }
        };
        const updateLogoForLightMode = () => {
            const logoContainer = document.querySelector('header div.logo svg');
            if (logoContainer) {
                logoContainer.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" id="Layer_1" x="0px" y="0px" viewBox="0 0 327.5 533.3" style="enable-background:new 0 0 327.5 533.3;" xml:space="preserve">
                    <style type="text/css">
                        .st0{fill:#8A92B2;}
                        .st1{fill:#62688F;}
                        .st2{fill:#454A75;}
                    </style>
                    <path class="st0" d="M163.7,197.2V0L0,271.6L163.7,197.2z"/>
                    <path class="st1" d="M163.7,368.4V197.2L0,271.6L163.7,368.4z M163.7,197.2l163.7,74.4L163.7,0V197.2z"/>
                    <path class="st2" d="M163.7,197.2v171.2l163.7-96.8L163.7,197.2z"/>
                    <path class="st0" d="M163.7,399.4L0,302.7l163.7,230.7V399.4z"/>
                    <path class="st1" d="M327.5,302.7l-163.8,96.7v134L327.5,302.7z"/>
                </svg>`;
            } else {
                console.error('Logo element not found');
            }
        };
        const updateHeroImage = () => {
            const heroImage = document.querySelector('#section1 .hero-image img');
            if (heroImage) {
                if (themeState.isDarkMode) {
                    heroImage.src = 'https://2srz7klk3i5auvyna7q33yqjovdaun5hdmwf64coymucsqmyfxba.arweave.net/1KOfqWraOgpXDQfhveIJdUYKN6cbLF9wTsMoKUGYLcI';
                } else {
                    heroImage.src = 'https://y6snssgdj5emkcmizd533b7xxff4tj4e4coiewg4aq7lfrdyo5xq.arweave.net/x6TZSMNPSMUJiMj7vYf3uUvJp4TgnIJY3AQ-ssR4d28';
                }
            }
        };
        const applyTheme = (themeState) => {
            if (themeState.isDarkMode) {
                addDarkModeClass();
                updateIconToMoon();
                updateLogoForDarkMode();
            } else {
                removeDarkModeClass();
                updateIconToSun();
                updateLogoForLightMode();
            }
            updateHeroImage();
        };
        const initializeTheme = (themeState) => {
            const storedTheme = getStoredTheme();
            themeState.isDarkMode = storedTheme === 'enabled';
            applyTheme(themeState);
        };
        const toggleTheme = (themeState) => {
            themeState.isDarkMode = !themeState.isDarkMode;
            applyTheme(themeState);
            saveThemeToLocalStorage(themeState.isDarkMode);
        };
        const initializeEventListeners = (themeState) => {
            const toggleButtonSidebar = document.getElementById('mode-toggle-sidebar');
            if (toggleButtonSidebar) {
                toggleButtonSidebar.addEventListener('click', () => toggleTheme(themeState));
            } else {
                console.error('Mode toggle button not found');
            }
            const toggleButton = document.getElementById('mode-toggle');
            if (toggleButton) {
                toggleButton.addEventListener('click', () => toggleTheme(themeState));
            } else {
                console.error('Mode toggle button not found');
            }
        };
        const init = () => {
            initializeTheme(themeState);
            initializeEventListeners(themeState);
        };
        return { init };
    })();
    const sidebarManager = (() => {
        const showSidebar = () => {
            try {
                const sidebar = document.querySelector('.sidebar');
                if (sidebar) {
                    sidebar.style.display = 'flex';
                } else {
                    console.error('Sidebar element not found');
                }
            } catch (error) {
                console.error('Error showing sidebar:', error);
            }
        };
        const hideSidebar = () => {
            try {
                const sidebar = document.querySelector('.sidebar');
                if (sidebar) {
                    sidebar.style.display = 'none';
                } else {
                    console.error('Sidebar element not found');
                }
            } catch (error) {
                console.error('Error hiding sidebar:', error);
            }
        };
        const initializeEventListeners = () => {
            const showButton = document.querySelector('.menu-button');
            if (showButton) {
                showButton.addEventListener('click', showSidebar);
            } else {
                console.error('Menu button for showing sidebar not found');
            }
            const hideButton = document.querySelector('.sidebar li a');
            if (hideButton) {
                hideButton.addEventListener('click', hideSidebar);
            } else {
                console.error('Menu button for hiding sidebar not found');
            }
        };
        const init = () => {
            initializeEventListeners();
        };
        return { init };
    })();
    const mainPageStatistics = (() => {
        const fetchData = async () => {
            try {
                const response = await fetch(`${API_URL}/nodes/count`);
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                const data = await response.json();
                updateStatistics(data);
            } catch (error) {
                console.error('Data fetching error:', error);
            }
        };        
        const formatNumber = (num) => {
            if (num >= 1000) {
                return (num / 1000).toFixed(1) + 'K';
            }
            return num.toString();
        };
        const updateStatistics = (data) => {
            const nodesElement = document.getElementById('nodes-count');
            const countriesElement = document.getElementById('countries-count');
            const ispsElement = document.getElementById('isps-count');
            if (nodesElement) nodesElement.textContent = formatNumber(data.NumberOfNodes);
            if (countriesElement) countriesElement.textContent = formatNumber(data.NumberOfCountries);
            if (ispsElement) ispsElement.textContent = formatNumber(data.NumberOfISPs);
        };
        const init = () => {
            fetchData();
        };
        return { init };
    })();
    const scrollManager = (() => {
        const init = () => {
            const main = document.querySelector('main');
    
            if (main) {
                main.style.opacity = 0;
                main.style.transform = 'translateY(20px)';
    
                setTimeout(() => {
                    main.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
                    main.style.opacity = 1;
                    main.style.transform = 'translateY(0)';
                }, 100);
            }
        };
    
        return { init };
    })();
    
    document.addEventListener('DOMContentLoaded', () => {
        scrollManager.init();
    });
    
    const init = () => {
        darkMode.init();
        sidebarManager.init();
        mainPageStatistics.init();
        scrollManager.init();
    };
    return { init };
})();
document.addEventListener('DOMContentLoaded', app.init);