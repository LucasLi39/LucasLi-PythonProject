const fileInput = document.getElementById('file-input');
const fileName = document.getElementById('file-name');
const uploadBtn = document.getElementById('upload-btn');
const uploadSection = document.getElementById('upload-section');
const readerSection = document.getElementById('reader-section');
const loading = document.getElementById('loading');
const bookTitle = document.getElementById('book-title');
const content = document.getElementById('content');
const chapterSelect = document.getElementById('chapter-select');
const toggleFurigana = document.getElementById('toggle-furigana');
const backBtn = document.getElementById('back-btn');
const prevPageBtn = document.getElementById('prev-page');
const nextPageBtn = document.getElementById('next-page');
const pageInfo = document.getElementById('page-info');

// Search elements
const searchInput = document.getElementById('search-input');
const searchBtn = document.getElementById('search-btn');
const searchBar = document.getElementById('search-bar');
const searchCount = document.getElementById('search-count');
const searchPrev = document.getElementById('search-prev');
const searchNext = document.getElementById('search-next');
const searchClose = document.getElementById('search-close');

// Vocabulary elements
const vocabBtn = document.getElementById('vocab-btn');
const vocabSidebar = document.getElementById('vocab-sidebar');
const vocabClose = document.getElementById('vocab-close');
const vocabList = document.getElementById('vocab-list');
const vocabEmpty = document.getElementById('vocab-empty');

let chapters = [];
let currentChapter = 0;
let currentPage = 0;
let pages = [];
let furiganaVisible = true;

// Search state
let searchMatches = [];
let currentMatchIndex = -1;
let searchQuery = '';

// Vocabulary state
let vocab = [];
const VOCAB_KEY = 'kanjilens_vocabulary';

// Load saved vocabulary from localStorage
function loadVocab() {
    try {
        const saved = localStorage.getItem(VOCAB_KEY);
        vocab = saved ? JSON.parse(saved) : [];
    } catch {
        vocab = [];
    }
    renderVocab();
}

// Save vocabulary to localStorage
function saveVocab() {
    localStorage.setItem(VOCAB_KEY, JSON.stringify(vocab));
}

// Render vocabulary list
function renderVocab() {
    vocabList.innerHTML = '';
    if (vocab.length === 0) {
        vocabEmpty.style.display = 'block';
    } else {
        vocabEmpty.style.display = 'none';
        vocab.forEach((item, index) => {
            const li = document.createElement('li');
            li.innerHTML = `
                <span class="vocab-kanji">${escapeHtml(item.kanji)}</span>
                <span class="vocab-reading">${escapeHtml(item.reading)}</span>
                <button class="vocab-delete" data-index="${index}" title="Remove">✕</button>
            `;
            vocabList.appendChild(li);
        });
    }
    vocabBtn.textContent = `📖 Vocab (${vocab.length})`;
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Add a word to vocabulary
function addToVocab(kanji, reading) {
    // Check for duplicates
    if (vocab.some(v => v.kanji === kanji && v.reading === reading)) {
        return;
    }
    vocab.push({ kanji, reading, added: new Date().toISOString() });
    saveVocab();
    renderVocab();
}

// Remove a word from vocabulary
function removeFromVocab(index) {
    vocab.splice(index, 1);
    saveVocab();
    renderVocab();
}

// Make ruby tags clickable for vocabulary
function makeRubyClickable() {
    const rubies = content.querySelectorAll('ruby');
    rubies.forEach(ruby => {
        ruby.style.cursor = 'pointer';
        ruby.title = 'Click to save to vocabulary';
        ruby.addEventListener('click', (e) => {
            e.stopPropagation();
            const kanji = ruby.childNodes[0]?.textContent?.trim() || '';
            const rt = ruby.querySelector('rt');
            const reading = rt ? rt.textContent.trim() : '';
            if (kanji && reading) {
                addToVocab(kanji, reading);
                // Visual feedback
                ruby.style.background = '#d4edda';
                setTimeout(() => { ruby.style.background = ''; }, 300);
            }
        });
    });
}

// Vocabulary sidebar toggle
vocabBtn.addEventListener('click', () => {
    vocabSidebar.classList.toggle('hidden');
});

vocabClose.addEventListener('click', () => {
    vocabSidebar.classList.add('hidden');
});

// Handle vocabulary delete clicks
vocabList.addEventListener('click', (e) => {
    if (e.target.classList.contains('vocab-delete')) {
        const index = parseInt(e.target.dataset.index);
        removeFromVocab(index);
    }
});

// Initialize vocabulary
loadVocab();

// Search functionality
function performSearch() {
    const query = searchInput.value.trim();
    if (!query) {
        clearSearch();
        return;
    }

    searchQuery = query;
    searchMatches = [];
    currentMatchIndex = -1;

    // Search across all pages in current chapter
    const rubies = content.querySelectorAll('ruby');
    rubies.forEach((ruby, idx) => {
        const kanji = ruby.childNodes[0]?.textContent?.trim() || '';
        const rt = ruby.querySelector('rt');
        const reading = rt ? rt.textContent.trim() : '';

        if (kanji.includes(query) || reading.includes(query)) {
            searchMatches.push({ element: ruby, index: idx });
        }
    });

    if (searchMatches.length > 0) {
        searchBar.classList.remove('hidden');
        currentMatchIndex = 0;
        highlightMatch();
    } else {
        searchCount.textContent = 'No matches';
        searchBar.classList.remove('hidden');
    }
}

function highlightMatch() {
    // Clear previous highlights
    content.querySelectorAll('.search-highlight').forEach(el => {
        el.classList.remove('search-highlight');
    });

    if (searchMatches.length === 0) return;

    const match = searchMatches[currentMatchIndex];
    match.element.classList.add('search-highlight');
    match.element.scrollIntoView({ behavior: 'smooth', block: 'center' });

    searchCount.textContent = `${currentMatchIndex + 1} / ${searchMatches.length}`;
}

function clearSearch() {
    searchMatches = [];
    currentMatchIndex = -1;
    searchQuery = '';
    searchBar.classList.add('hidden');
    content.querySelectorAll('.search-highlight').forEach(el => {
        el.classList.remove('search-highlight');
    });
}

function nextMatch() {
    if (searchMatches.length === 0) return;
    currentMatchIndex = (currentMatchIndex + 1) % searchMatches.length;
    highlightMatch();
}

function prevMatch() {
    if (searchMatches.length === 0) return;
    currentMatchIndex = (currentMatchIndex - 1 + searchMatches.length) % searchMatches.length;
    highlightMatch();
}

searchBtn.addEventListener('click', performSearch);
searchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') performSearch();
    if (e.key === 'Escape') clearSearch();
});
searchNext.addEventListener('click', nextMatch);
searchPrev.addEventListener('click', prevMatch);
searchClose.addEventListener('click', clearSearch);

// File selection
fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
        fileName.textContent = fileInput.files[0].name;
        uploadBtn.disabled = false;
    } else {
        fileName.textContent = '';
        uploadBtn.disabled = true;
    }
});

// Upload
uploadBtn.addEventListener('click', async () => {
    const file = fileInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    loading.classList.remove('hidden');
    uploadBtn.disabled = true;

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }

        const data = await response.json();
        chapters = data.chapters;

        // Set up chapter selector
        chapterSelect.innerHTML = '';
        chapters.forEach((ch, i) => {
            const option = document.createElement('option');
            option.value = i;
            option.textContent = ch.title;
            chapterSelect.appendChild(option);
        });

        bookTitle.textContent = data.title;
        currentChapter = 0;
        furiganaVisible = true;
        toggleFurigana.classList.add('active');

        // Show reader
        uploadSection.classList.add('hidden');
        readerSection.classList.remove('hidden');

        loadChapter(0);

    } catch (err) {
        alert('Error: ' + err.message);
    } finally {
        loading.classList.add('hidden');
        uploadBtn.disabled = false;
    }
});

// Load a chapter
function loadChapter(index) {
    currentChapter = index;
    currentPage = 0;
    chapterSelect.value = index;
    clearSearch();

    // Split content into paragraphs
    const html = chapters[index].content;
    content.innerHTML = html;

    // Make ruby tags clickable
    makeRubyClickable();

    // Paginate
    paginateContent();
    renderPage();
}

// Paginate content into pages
function paginateContent() {
    const containerHeight = document.getElementById('reader').clientHeight - 40;
    pages = [];

    // Get all direct children (paragraphs, etc.)
    const children = Array.from(content.children);
    let currentPageHtml = '';
    let currentHeight = 0;

    // Create a temporary container to measure
    const tempDiv = document.createElement('div');
    tempDiv.style.cssText = `
        max-width: 700px;
        font-size: 1.2rem;
        line-height: 2;
        visibility: hidden;
        position: absolute;
    `;
    document.body.appendChild(tempDiv);

    for (const child of children) {
        tempDiv.innerHTML = currentPageHtml + child.outerHTML;
        const newHeight = tempDiv.scrollHeight;

        if (newHeight > containerHeight && currentPageHtml !== '') {
            pages.push(currentPageHtml);
            currentPageHtml = child.outerHTML;
        } else {
            currentPageHtml += child.outerHTML;
        }
    }

    if (currentPageHtml) {
        pages.push(currentPageHtml);
    }

    document.body.removeChild(tempDiv);

    // If no pages (empty chapter), create one empty page
    if (pages.length === 0) {
        pages.push('');
    }
}

// Render current page
function renderPage() {
    content.innerHTML = pages[currentPage] || '';
    pageInfo.textContent = `Page ${currentPage + 1} of ${pages.length}`;
    prevPageBtn.disabled = currentPage === 0;
    nextPageBtn.disabled = currentPage >= pages.length - 1;

    // Re-attach click handlers and re-highlight search on new page
    makeRubyClickable();
    if (searchQuery) {
        // Re-run search on this page
        const rubies = content.querySelectorAll('ruby');
        searchMatches = [];
        rubies.forEach((ruby, idx) => {
            const kanji = ruby.childNodes[0]?.textContent?.trim() || '';
            const rt = ruby.querySelector('rt');
            const reading = rt ? rt.textContent.trim() : '';
            if (kanji.includes(searchQuery) || reading.includes(searchQuery)) {
                searchMatches.push({ element: ruby, index: idx });
            }
        });
        if (searchMatches.length > 0) {
            currentMatchIndex = 0;
            highlightMatch();
        }
    }
}

// Chapter navigation
chapterSelect.addEventListener('change', () => {
    loadChapter(parseInt(chapterSelect.value));
});

// Page navigation
prevPageBtn.addEventListener('click', () => {
    if (currentPage > 0) {
        currentPage--;
        renderPage();
    }
});

nextPageBtn.addEventListener('click', () => {
    if (currentPage < pages.length - 1) {
        currentPage++;
        renderPage();
    }
});

// Furigana toggle
toggleFurigana.addEventListener('click', () => {
    furiganaVisible = !furiganaVisible;
    content.classList.toggle('furigana-hidden', !furiganaVisible);
    toggleFurigana.classList.toggle('active', furiganaVisible);
});

// Back to upload
backBtn.addEventListener('click', () => {
    readerSection.classList.add('hidden');
    uploadSection.classList.remove('hidden');
    fileInput.value = '';
    fileName.textContent = '';
    uploadBtn.disabled = true;
    content.innerHTML = '';
    chapters = [];
    clearSearch();
    vocabSidebar.classList.add('hidden');
});

// Keyboard navigation
document.addEventListener('keydown', (e) => {
    if (readerSection.classList.contains('hidden')) return;

    if (e.key === 'ArrowRight' || e.key === ' ') {
        e.preventDefault();
        if (currentPage < pages.length - 1) {
            currentPage++;
            renderPage();
        }
    } else if (e.key === 'ArrowLeft') {
        e.preventDefault();
        if (currentPage > 0) {
            currentPage--;
            renderPage();
        }
    } else if (e.key === 'Escape') {
        clearSearch();
        vocabSidebar.classList.add('hidden');
    }
});

// Repaginate on window resize
let resizeTimeout;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
        if (!readerSection.classList.contains('hidden') && chapters.length > 0) {
            paginateContent();
            currentPage = Math.min(currentPage, pages.length - 1);
            renderPage();
        }
    }, 250);
});
