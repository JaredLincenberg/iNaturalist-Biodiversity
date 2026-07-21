
const toggle = document.getElementById('theme-toggle');
const label = document.getElementById('theme-toggle-label');

// Listen for checkbox state change
toggle.addEventListener('change', function () {
    const html = document.documentElement;

    // Determine theme based on checkbox state
    const newTheme = this.checked ? 'dark' : 'light';

    // Set the new theme on the <html> tag
    html.setAttribute('data-bs-theme', newTheme);

    // Update label text
    label.textContent = newTheme === 'dark' ? 'Dark Mode' : 'Light Mode';
});