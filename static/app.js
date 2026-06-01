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

let chapters = [];
let currentChapter = 0;
let currentPage = 0;
let pages = [];
let furiganaVisible = true;

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

    // Split content into paragraphs
    const html = chapters[index].content;
    content.innerHTML = html;

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
