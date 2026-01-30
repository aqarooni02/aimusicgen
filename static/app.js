let ws = null;

function generate() {
    const theme = document.getElementById('theme').value.trim();
    
    if (!theme) {
        showError('Please enter a theme');
        return;
    }
    
    // Reset UI
    resetUI();
    
    // Disable button
    const btn = document.getElementById('generateBtn');
    btn.disabled = true;
    btn.textContent = 'Generating...';
    
    // Show progress
    document.getElementById('progress').classList.remove('hidden');
    
    // Connect WebSocket
    ws = new WebSocket(`ws://${window.location.host}/ws`);
    
    ws.onopen = () => {
        ws.send(JSON.stringify({ theme }));
    };
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.error) {
            showError(data.error);
            resetButton();
            return;
        }
        
        updateStep(data.step, data.status);
        
        // Show lyrics after step 1
        if (data.step === 1 && data.lyrics) {
            showLyrics(data.lyrics);
        }
        
        // Show result after step 4
        if (data.step === 4 && data.video_url) {
            showResult(data.video_url);
        }
    };
    
    ws.onerror = (error) => {
        showError('Connection error. Please try again.');
        resetButton();
    };
    
    ws.onclose = () => {
        resetButton();
    };
}

function updateStep(stepNum, status) {
    // Mark previous steps complete
    for (let i = 1; i < stepNum; i++) {
        const stepEl = document.getElementById(`step${i}`);
        stepEl.classList.remove('active');
        stepEl.classList.add('complete');
        document.getElementById(`status${i}`).textContent = 'Done';
    }
    
    // Update current step
    const currentStep = document.getElementById(`step${stepNum}`);
    currentStep.classList.add('active');
    document.getElementById(`status${stepNum}`).textContent = status;
}

function showLyrics(lyrics) {
    const lyricsEl = document.getElementById('lyrics-display');
    lyricsEl.innerHTML = `
        <h3>Generated Lyrics</h3>
        <pre>${lyrics}</pre>
    `;
    lyricsEl.classList.remove('hidden');
}

function showResult(videoUrl) {
    const resultEl = document.getElementById('result');
    const videoPlayer = document.getElementById('videoPlayer');
    const downloadBtn = document.getElementById('downloadBtn');
    
    videoPlayer.src = videoUrl;
    downloadBtn.href = videoUrl;
    
    resultEl.classList.remove('hidden');
    
    // Scroll to result
    resultEl.scrollIntoView({ behavior: 'smooth' });
}

function showError(message) {
    const errorEl = document.getElementById('error');
    errorEl.textContent = message;
    errorEl.classList.remove('hidden');
}

function resetUI() {
    // Hide all sections
    document.getElementById('progress').classList.add('hidden');
    document.getElementById('lyrics-display').classList.add('hidden');
    document.getElementById('result').classList.add('hidden');
    document.getElementById('error').classList.add('hidden');
    
    // Reset steps
    for (let i = 1; i <= 4; i++) {
        const stepEl = document.getElementById(`step${i}`);
        stepEl.classList.remove('active', 'complete');
        document.getElementById(`status${i}`).textContent = 'Waiting...';
    }
}

function resetButton() {
    const btn = document.getElementById('generateBtn');
    btn.disabled = false;
    btn.textContent = 'Generate Music Video';
}

// Enter key support
document.getElementById('theme').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        generate();
    }
});
