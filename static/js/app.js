/**
 * 32-Bit Python Media Server - Frontend Controller
 * Handles live stats polling, library rendering, search, filtering,
 * and seamless HTML5 video playback with resume memory.
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const mediaGrid = document.getElementById('mediaGrid');
    const emptyState = document.getElementById('emptyState');
    const searchInput = document.getElementById('searchInput');
    const mediaCountEl = document.getElementById('mediaCount');
    const filterPills = document.querySelectorAll('.pill');
    
    // Stats Elements
    const statRam = document.getElementById('statRam');
    const statCpu = document.getElementById('statCpu');
    const statStreams = document.getElementById('statStreams');
    const refreshScanBtn = document.getElementById('refreshScanBtn');
    const scanBtn = document.getElementById('scanBtn');

    // Player Elements
    const playerModal = document.getElementById('playerModal');
    const modalBackdrop = document.getElementById('modalBackdrop');
    const closePlayerBtn = document.getElementById('closePlayerBtn');
    const videoPlayer = document.getElementById('videoPlayer');
    const audioPlayer = document.getElementById('audioPlayer');
    const playerTitle = document.getElementById('playerTitle');
    const playerBadge = document.getElementById('playerBadge');
    const resumeAlert = document.getElementById('resumeAlert');
    const resumeTimeStr = document.getElementById('resumeTimeStr');

    // State Variables
    let allMediaItems = [];
    let activeFilter = 'all';
    let currentPlayingId = null;
    let timeUpdateSaveTimeout = null;

    // Fetch Live Server Stats
    async function updateServerStats() {
        try {
            const res = await fetch('/api/stats');
            if (res.ok) {
                const data = await res.json();
                statRam.textContent = `${data.process_ram_mb} MB`;
                statCpu.textContent = `${data.process_cpu_pct}%`;
                statStreams.textContent = data.active_streams;
            }
        } catch (e) {
            console.warn('Failed to fetch stats:', e);
        }
    }

    // Poll stats every 3 seconds
    updateServerStats();
    setInterval(updateServerStats, 3000);

    // Fetch Media Library
    async function loadMediaLibrary() {
        try {
            const res = await fetch('/api/media');
            if (res.ok) {
                const data = await res.json();
                allMediaItems = data.items || [];
                renderLibrary();
            }
        } catch (e) {
            console.error('Error loading library:', e);
        }
    }

    // Filter and Render Cards
    function renderLibrary() {
        const query = searchInput.value.trim().toLowerCase();
        
        let filtered = allMediaItems.filter(item => {
            // Text Search
            const matchesQuery = !query || 
                item.title.toLowerCase().includes(query) || 
                item.filename.toLowerCase().includes(query);

            // Filter Pills
            let matchesFilter = true;
            if (activeFilter === '720p') {
                matchesFilter = item.is_720p;
            } else if (activeFilter === 'video') {
                matchesFilter = item.media_type === 'video';
            } else if (activeFilter === 'audio') {
                matchesFilter = item.media_type === 'audio';
            }

            return matchesQuery && matchesFilter;
        });

        mediaCountEl.textContent = filtered.length;

        if (filtered.length === 0) {
            mediaGrid.innerHTML = '';
            emptyState.classList.remove('hidden');
            return;
        }

        emptyState.classList.add('hidden');
        mediaGrid.innerHTML = filtered.map(item => createMediaCardHTML(item)).join('');

        // Attach click handlers to cards
        document.querySelectorAll('.media-card').forEach(card => {
            card.addEventListener('click', () => {
                const id = card.dataset.id;
                const item = allMediaItems.find(i => i.id === id);
                if (item) openPlayer(item);
            });
        });
    }

    // Generate Card HTML
    function createMediaCardHTML(item) {
        const isVideo = item.media_type === 'video';
        const icon = isVideo ? '🎬' : '🎵';
        const badgeHTML = item.is_720p ? `<span class="badge-720p">720p HD</span>` : '';

        return `
            <div class="media-card" data-id="${item.id}">
                <div class="card-poster">
                    <span class="poster-icon">${icon}</span>
                    ${badgeHTML}
                    <div class="play-overlay">
                        <div class="play-btn-circle">▶</div>
                    </div>
                </div>
                <div class="card-body">
                    <div class="card-title" title="${escapeHtml(item.title)}">${escapeHtml(item.title)}</div>
                    <div class="card-meta">
                        <span>${item.size_formatted}</span>
                        <span>${item.added_date}</span>
                    </div>
                </div>
            </div>
        `;
    }

    // Open Video / Audio Player Modal
    function openPlayer(item) {
        currentPlayingId = item.id;
        playerTitle.textContent = item.title;
        playerBadge.textContent = item.is_720p ? '720p MP4' : item.extension.toUpperCase();
        
        const streamUrl = `/api/stream/${item.id}`;

        if (item.media_type === 'video') {
            audioPlayer.classList.add('hidden');
            audioPlayer.pause();
            videoPlayer.classList.remove('hidden');
            videoPlayer.src = streamUrl;

            // Check for saved resume position
            const savedTimeKey = `resume_pos_${item.id}`;
            const savedTime = parseFloat(localStorage.getItem(savedTimeKey) || '0');

            videoPlayer.onloadedmetadata = () => {
                if (savedTime > 10 && savedTime < (videoPlayer.duration - 15)) {
                    videoPlayer.currentTime = savedTime;
                    resumeTimeStr.textContent = formatTime(savedTime);
                    resumeAlert.classList.remove('hidden');
                    setTimeout(() => resumeAlert.classList.add('hidden'), 5000);
                } else {
                    resumeAlert.classList.add('hidden');
                }
            };

            videoPlayer.play().catch(err => console.log("Autoplay blocked:", err));
        } else {
            videoPlayer.classList.add('hidden');
            videoPlayer.pause();
            audioPlayer.classList.remove('hidden');
            audioPlayer.src = streamUrl;
            audioPlayer.play().catch(err => console.log("Autoplay blocked:", err));
        }

        playerModal.classList.remove('hidden');
    }

    // Save Playback Position
    videoPlayer.addEventListener('timeupdate', () => {
        if (!currentPlayingId || videoPlayer.paused) return;

        // Throttle saves to once every 3 seconds
        if (!timeUpdateSaveTimeout) {
            timeUpdateSaveTimeout = setTimeout(() => {
                if (videoPlayer.currentTime > 5) {
                    localStorage.setItem(`resume_pos_${currentPlayingId}`, videoPlayer.currentTime);
                }
                timeUpdateSaveTimeout = null;
            }, 3000);
        }
    });

    // Close Player
    function closePlayer() {
        videoPlayer.pause();
        audioPlayer.pause();
        videoPlayer.src = '';
        audioPlayer.src = '';
        playerModal.classList.add('hidden');
        resumeAlert.classList.add('hidden');
        currentPlayingId = null;
    }

    closePlayerBtn.addEventListener('click', closePlayer);
    modalBackdrop.addEventListener('click', closePlayer);
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !playerModal.classList.contains('hidden')) {
            closePlayer();
        }
    });

    // Search and Filters
    searchInput.addEventListener('input', renderLibrary);

    filterPills.forEach(pill => {
        pill.addEventListener('click', () => {
            filterPills.forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            activeFilter = pill.dataset.filter;
            renderLibrary();
        });
    });

    // Trigger Directory Scan
    async function triggerRescan() {
        try {
            refreshScanBtn.style.transform = 'rotate(360deg)';
            const res = await fetch('/api/scan', { method: 'POST' });
            if (res.ok) {
                setTimeout(loadMediaLibrary, 1500);
            }
        } catch (e) {
            console.error('Scan error:', e);
        }
    }

    refreshScanBtn.addEventListener('click', triggerRescan);
    scanBtn.addEventListener('click', triggerRescan);

    // Helpers
    function escapeHtml(text) {
        return text.replace(/[&<>"']/g, function(m) {
            return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[m];
        });
    }

    function formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }

    // Initial Load
    loadMediaLibrary();
});
