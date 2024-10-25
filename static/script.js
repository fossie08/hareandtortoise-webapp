// Detect System Theme and Toggle Light/Dark Mode
function applyTheme() {
    const prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const theme = localStorage.getItem('theme') || (prefersDarkScheme ? 'dark' : 'light');
    document.body.classList.toggle('dark-mode', theme === 'dark');
    document.body.classList.toggle('light-mode', theme === 'light');
}

document.getElementById('theme-toggle').addEventListener('click', () => {
    const isDarkMode = document.body.classList.contains('dark-mode');
    document.body.classList.toggle('dark-mode', !isDarkMode);
    document.body.classList.toggle('light-mode', isDarkMode);
    localStorage.setItem('theme', isDarkMode ? 'light' : 'dark');
});

// Loading Screen Control
function showLoadingScreen() {
    document.getElementById('loading-screen').classList.remove('hide');
}

function hideLoadingScreen() {
    document.getElementById('loading-screen').classList.add('hide');
}

// Apply theme on page load
applyTheme();
window.addEventListener('load', hideLoadingScreen);
