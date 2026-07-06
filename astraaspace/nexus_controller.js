document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'k') {
        const overlay = document.getElementById('nexus-overlay');
        overlay.style.display = overlay.style.display === 'block' ? 'none' : 'block';
        document.getElementById('nexus-input').focus();
    }
});
