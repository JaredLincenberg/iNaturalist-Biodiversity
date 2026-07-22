
const toggle = document.getElementById('theme-toggle');
const label = document.getElementById('theme-toggle-label');
const html = document.documentElement;

// Listen for checkbox state change
toggle.addEventListener('change', function () {

    // Determine theme based on checkbox state
    const newTheme = this.checked ? 'dark' : 'light';

    localStorage.setItem('myTheme', newTheme);
    // Set the new theme on the <html> tag
    html.setAttribute('data-bs-theme', newTheme);

    // Update label text
    label.textContent = newTheme === 'dark' ? 'Dark Mode' : 'Light Mode';
});
function applyLightDarkTheme(theme){

    localStorage.setItem('myTheme', theme);
    html.setAttribute('data-bs-theme', theme);

    if(theme ==="light")
        toggle.checked = false
        
    else if (theme==="dark")
        toggle.checked = true
    label.textContent = theme === 'dark' ? 'Dark Mode' : 'Light Mode';
}

document.addEventListener('DOMContentLoaded', function () {
    if(localStorage.getItem("myTheme") !==null){
        applyLightDarkTheme(localStorage.getItem('myTheme'))
    }
    else if(matchMedia('(prefers-color-scheme: dark)').matches){
        applyLightDarkTheme('dark')
    }
    else{
        applyLightDarkTheme('light')
    }
    // applyLightDarkTheme(document.documentElement.getAttribute('data-bs-theme'));
});