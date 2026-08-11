/**
 * 32-Bit Python Media Server - Frontend Controller
 * Handles live stats polling, server-side pagination, state persistence
 * (retains page/filter state across reloads via localStorage), search,
 * and seamless HTML5 video playback with auto-resume memory.
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const mediaGrid = document.getElementById('mediaGrid');
    const emptyState = document.getElementById('emptyState');
    const searchInput = document.getElementById('searchInput');
    const mediaCountEl = document.getElementById('mediaCount');
    const filterPills = document.querySelectorAll('.pill');
    
    // Pagination Elements
    const paginationBar = document.getElementById('paginationBar');
    const prevPageBtn = document.getElementById('prevPageBtn');
    const nextPageBtn = document.getElementById('nextPageBtn');
    const pageIndicator = document.getElementById('pageIndicator');
    const pageSizeSelect = document.getElementById('pageSizeSelect');

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

    // -------------------------------------------------------------
    // State Persistence (Restores page & filter state on reload)
    // -------------------------------------------------------------
    const STORAGE_KEY = 'media_server_view_state';

    function loadSavedState() {
        try {
            const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
            return {
                page: parseInt(saved.page || '1', 10),
                limit: parseInt(saved.limit || '24', 10),
                filter: saved.filter || 'all',
                search: saved.search || ''
            };
        } catch (e) {
            return { page: 1, limit: 24, filter: 'all', search: '' };
        }
    }

    function saveState() {
        try {
            const state = {
                page: currentPage,
                limit: pageSize,
                filter: activeFilter,
                search: searchQuery
            };
            localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
            
            // Sync with URL query params
            const url = new URL(window.location);
            url.searchParams.set('page', currentPage);
            url.searchParams.set('limit', pageSize);
            if (activeFilter !== 'all') url.searchParams.set('filter', activeFilter);
            else url.searchParams.delete('filter');
            if (searchQuery) url.searchParams.set('q', searchQuery);
            else url.searchParams.delete('q');
            window.history.replaceState({}, '', url);
        } catch (e) {
            console.warn('Failed to save state:', e);
        }
    }

    // Initialize State
    const savedState = loadSavedState();
    let currentPage = savedState.page;
    let pageSize = savedState.limit;
    let activeFilter = savedState.filter;
    let searchQuery = savedState.search;
    let totalPages = 1;
    let currentItems = [];
    let currentPlayingId = null;
    let timeUpdateSaveTimeout = null;

    // Set UI to match restored state
    searchInput.value = searchQuery;
    pageSizeSelect.value = pageSize.toString();
    filterPills.forEach(pill => {
        if (pill.dataset.filter === activeFilter) {
            pill.classList.add('active');
        } else {
            pill.classList.remove('active');
        }
    });

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

    updateServerStats();
    setInterval(updateServerStats, 3000);

    // Fetch Paginated Media Library
    async function fetchMediaLibrary() {
        try {
            const params = new URLSearchParams({
                page: currentPage.toString(),
                limit: pageSize.toString()
            });

            if (searchQuery) params.append('q', searchQuery);
            if (activeFilter === '720p') params.append('only_720p', 'true');
            else if (activeFilter === 'video') params.append('media_type', 'video');
            else if (activeFilter === 'audio') params.append('media_type', 'audio');

            const res = await fetch(`/api/media?${params.toString()}`);
            if (res.ok) {
                const data = await res.json();
                currentItems = data.items || [];
                currentPage = data.page;
                totalPages = data.total_pages;
                mediaCountEl.textContent = data.total_items;

                saveState();
                renderLibrary(data.total_items);
            }
        } catch (e) {
            console.error('Error fetching media library:', e);
        }
    }

    // Render Cards and Update Pagination Controls
    function renderLibrary(totalItems) {
        if (totalItems === 0) {
            mediaGrid.innerHTML = '';
            emptyState.classList.remove('hidden');
            paginationBar.classList.add('hidden');
            return;
        }

        emptyState.classList.add('hidden');
        paginationBar.classList.remove('hidden');
        mediaGrid.innerHTML = currentItems.map(item => createMediaCardHTML(item)).join('');

        // Update Pagination Bar UI
        pageIndicator.textContent = `Page ${currentPage} of ${totalPages}`;
        prevPageBtn.disabled = currentPage <= 1;
        nextPageBtn.disabled = currentPage >= totalPages;

        // Attach click handlers to cards
        document.querySelectorAll('.media-card').forEach(card => {
            card.addEventListener('click', () => {
                const id = card.dataset.id;
                const item = currentItems.find(i => i.id === id);
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

    // Pagination Event Listeners
    prevPageBtn.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            fetchMediaLibrary();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    });

    nextPageBtn.addEventListener('click', () => {
        if (currentPage < totalPages) {
            currentPage++;
            fetchMediaLibrary();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    });

    pageSizeSelect.addEventListener('change', (e) => {
        pageSize = parseInt(e.target.value, 10);
        currentPage = 1;
        fetchMediaLibrary();
    });

    // Search Input with Debounce
    let searchDebounceTimeout = null;
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchDebounceTimeout);
        searchDebounceTimeout = setTimeout(() => {
            searchQuery = e.target.value.trim();
            currentPage = 1;
            fetchMediaLibrary();
        }, 250);
    });

    // Filter Pills
    filterPills.forEach(pill => {
        pill.addEventListener('click', () => {
            filterPills.forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            activeFilter = pill.dataset.filter;
            currentPage = 1;
            fetchMediaLibrary();
        });
    });

    // Open Player Modal
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

    // Trigger Rescan
    async function triggerRescan() {
        try {
            refreshScanBtn.style.transform = 'rotate(360deg)';
            const res = await fetch('/api/scan', { method: 'POST' });
            if (res.ok) {
                setTimeout(fetchMediaLibrary, 1500);
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

    // Initial Fetch
    fetchMediaLibrary();
});
