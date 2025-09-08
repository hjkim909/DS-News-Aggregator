/**
 * DS News Aggregator - Enhanced Frontend JavaScript
 * 사용자 요구사항 반영: 다크/라이트 모드, 읽은 글 관리, 모달 기능, API 호출
 */

// 전역 변수
let articlesData = window.articlesData || [];
let statsData = window.statsData || {};
let currentArticleId = null;
let isCollecting = false;

// 설정
const CONFIG = {
    STORAGE_KEYS: {
        READ_ARTICLES: 'ds_news_read_articles',
        DARK_MODE: 'ds_news_dark_mode',
        LAST_VISIT: 'ds_news_last_visit'
    },
    ANIMATION_DURATION: 300,
    TOAST_DURATION: 3000
};

// DOM 요소들
const elements = {};

/**
 * 초기화
 */
document.addEventListener('DOMContentLoaded', function() {
    initializeElements();
    initializeDarkMode();
    initializeEventListeners();
    initializeReadStatus();
    initializeData();
    setupInfiniteScroll();
    
    console.log('✅ DS News Aggregator 초기화 완료');
});

/**
 * DOM 요소들 초기화
 */
function initializeElements() {
    elements.articlesGrid = document.getElementById('articlesGrid');
    elements.articleModal = document.getElementById('articleModal');
    elements.loadingState = document.getElementById('loadingState');
    elements.emptyState = document.getElementById('emptyState');
    elements.darkModeToggle = document.getElementById('darkModeToggle');
    elements.collectBtn = document.getElementById('collectBtn');
    elements.collectIcon = document.getElementById('collectIcon');
    elements.sortSelect = document.getElementById('sortSelect');
    elements.filterSelect = document.getElementById('filterSelect');
    elements.toast = document.getElementById('toast');
    
    // 모달 요소들
    elements.modalTitle = document.getElementById('modalTitle');
    elements.modalMeta = document.getElementById('modalMeta');
    elements.modalSummary = document.getElementById('modalSummary');
    elements.modalTags = document.getElementById('modalTags');
    elements.modalContent = document.getElementById('modalContent');
    elements.modalOriginal = document.getElementById('modalOriginal');
    elements.originalContent = document.getElementById('originalContent');
    elements.toggleOriginalBtn = document.getElementById('toggleOriginalBtn');
    elements.markReadBtn = document.getElementById('markReadBtn');
    elements.openOriginalBtn = document.getElementById('openOriginalBtn');
    
    console.log('DOM 요소 초기화 완료');
}

/**
 * 다크 모드 초기화 (사용자 요구사항: 다크/라이트 모드 토글)
 */
function initializeDarkMode() {
    const savedDarkMode = localStorage.getItem(CONFIG.STORAGE_KEYS.DARK_MODE);
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    const isDark = savedDarkMode ? JSON.parse(savedDarkMode) : prefersDark;
    
    if (isDark) {
        document.documentElement.classList.add('dark');
        updateDarkModeIcon(true);
    }
    
    // 시스템 테마 변경 감지
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!localStorage.getItem(CONFIG.STORAGE_KEYS.DARK_MODE)) {
            toggleDarkMode(e.matches);
        }
    });
}

/**
 * 다크 모드 토글
 */
function toggleDarkMode(forceDark = null) {
    const isDark = forceDark !== null ? forceDark : !document.documentElement.classList.contains('dark');
    
    if (isDark) {
        document.documentElement.classList.add('dark');
    } else {
        document.documentElement.classList.remove('dark');
    }
    
    localStorage.setItem(CONFIG.STORAGE_KEYS.DARK_MODE, JSON.stringify(isDark));
    updateDarkModeIcon(isDark);
    
    showToast(isDark ? '다크 모드로 전환되었습니다' : '라이트 모드로 전환되었습니다', 'success');
}

/**
 * 다크 모드 아이콘 업데이트
 */
function updateDarkModeIcon(isDark) {
    if (elements.darkModeToggle) {
        const icon = elements.darkModeToggle.querySelector('i');
        if (icon) {
            icon.className = isDark ? 'fas fa-sun text-lg' : 'fas fa-moon text-lg';
        }
    }
}

/**
 * 이벤트 리스너 초기화
 */
function initializeEventListeners() {
    // 다크 모드 토글
    if (elements.darkModeToggle) {
        elements.darkModeToggle.addEventListener('click', () => toggleDarkMode());
    }
    
    // 키보드 단축키
    document.addEventListener('keydown', handleKeyboardShortcuts);
    
    // 모달 바깥 클릭시 닫기
    if (elements.articleModal) {
        elements.articleModal.addEventListener('click', function(e) {
            if (e.target === elements.articleModal || e.target.classList.contains('modal-backdrop')) {
                closeArticleModal();
            }
        });
    }
    
    // 정렬/필터 변경 이벤트
    if (elements.sortSelect) {
        elements.sortSelect.addEventListener('change', function() {
            sortArticles(this.value);
        });
    }
    
    if (elements.filterSelect) {
        elements.filterSelect.addEventListener('change', function() {
            filterArticles(this.value);
        });
    }
    
    // 무한 스크롤
    window.addEventListener('scroll', debounce(handleScroll, 100));
    
    // 온라인/오프라인 상태 감지
    window.addEventListener('online', () => showToast('연결이 복원되었습니다', 'success'));
    window.addEventListener('offline', () => showToast('인터넷 연결이 끊어졌습니다', 'warning'));
}

/**
 * 읽은 글 상태 초기화 (사용자 요구사항: localStorage 활용)
 */
function initializeReadStatus() {
    const readArticles = getReadArticles();
    
    readArticles.forEach(articleId => {
        const card = document.querySelector(`[data-article-id="${articleId}"]`);
        if (card) {
            markCardAsRead(card, false); // 애니메이션 없이
        }
    });
    
    console.log(`읽은 글 ${readArticles.length}개 로드됨`);
}

/**
 * 데이터 초기화
 */
function initializeData() {
    if (articlesData && articlesData.length > 0) {
        console.log(`글 데이터 ${articlesData.length}개 로드됨`);
        updateLastVisit();
    }
}

/**
 * 키보드 단축키 처리
 */
function handleKeyboardShortcuts(e) {
    // ESC: 모달 닫기
    if (e.key === 'Escape' && currentArticleId) {
        closeArticleModal();
        e.preventDefault();
    }
    
    // Ctrl+D: 다크 모드 토글
    if (e.ctrlKey && e.key === 'd') {
        e.preventDefault();
        toggleDarkMode();
    }
    
    // Ctrl+R: 새로고침 (수집)
    if (e.ctrlKey && e.key === 'r') {
        e.preventDefault();
        collectArticles();
    }
    
    // 숫자 키: 정렬 변경
    if (!e.ctrlKey && !e.altKey && !e.shiftKey && elements.sortSelect) {
        switch(e.key) {
            case '1':
                elements.sortSelect.value = 'score';
                sortArticles('score');
                break;
            case '2':
                elements.sortSelect.value = 'date';
                sortArticles('date');
                break;
            case '3':
                elements.sortSelect.value = 'source';
                sortArticles('source');
                break;
        }
    }
}

/**
 * 스크롤 처리 (무한 스크롤 향후 확장용)
 */
function handleScroll() {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const windowHeight = window.innerHeight;
    const docHeight = document.documentElement.scrollHeight;
    
    // 페이지 하단 근처에서 추가 로딩 로직 (향후 구현)
    if (scrollTop + windowHeight >= docHeight - 200) {
        // loadMoreArticles(); // 향후 구현
    }
    
    // 스크롤에 따른 헤더 스타일 변경
    const header = document.querySelector('header');
    if (header) {
        if (scrollTop > 100) {
            header.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)';
        } else {
            header.style.boxShadow = '';
        }
    }
}

/**
 * 무한 스크롤 설정 (향후 확장용)
 */
function setupInfiniteScroll() {
    // Intersection Observer를 사용한 무한 스크롤 준비
    // 향후 페이지네이션 구현시 사용
    console.log('무한 스크롤 준비 완료 (향후 확장)');
}

/**
 * 글 모달 표시 (사용자 요구사항: 카드 클릭시 모달창 팝업)
 */
async function showArticleModal(articleId) {
    if (!articleId) return;
    
    currentArticleId = articleId;
    
    // 로딩 상태 표시
    showModalLoading();
    
    try {
        // API에서 개별 글 데이터 가져오기
        const article = await fetchArticleById(articleId);
        
        if (!article) {
            showToast('글을 불러올 수 없습니다', 'error');
            return;
        }
        
        populateModal(article);
        
        // 모달 표시
        if (elements.articleModal) {
            elements.articleModal.classList.remove('hidden');
            document.body.style.overflow = 'hidden';
            
            // 접근성: 포커스 설정
            setTimeout(() => {
                const closeButton = elements.articleModal.querySelector('button');
                if (closeButton) closeButton.focus();
            }, CONFIG.ANIMATION_DURATION);
        }
        
        // 읽은 글로 자동 표시
        setTimeout(() => {
            markAsRead(articleId, false);
        }, 3000); // 3초 후 자동으로 읽음 처리
        
    } catch (error) {
        console.error('모달 표시 실패:', error);
        showToast('글을 불러오는 중 오류가 발생했습니다', 'error');
    }
}

/**
 * 모달 로딩 상태 표시
 */
function showModalLoading() {
    if (elements.modalTitle) elements.modalTitle.textContent = '로딩 중...';
    if (elements.modalContent) {
        elements.modalContent.innerHTML = `
            <div class="flex items-center justify-center py-12">
                <div class="loading-spinner"></div>
                <span class="ml-3 text-gray-600 dark:text-gray-400">글을 불러오는 중...</span>
            </div>
        `;
    }
}

/**
 * API에서 개별 글 데이터 가져오기
 */
async function fetchArticleById(articleId) {
    try {
        // 먼저 로컬 데이터에서 찾기
        const localArticle = articlesData.find(article => article.id === articleId);
        if (localArticle) {
            return localArticle;
        }
        
        // API에서 가져오기
        const response = await fetch(`/api/article/${articleId}`);
        const data = await response.json();
        
        if (data.success) {
            return data.article;
        } else {
            throw new Error(data.error || '글을 찾을 수 없습니다');
        }
        
    } catch (error) {
        console.error('글 데이터 가져오기 실패:', error);
        return null;
    }
}

/**
 * 모달 콘텐츠 채우기 (사용자 요구사항: 번역된 전문 + "원문 보기" 버튼)
 */
function populateModal(article) {
    // 제목 (한글 우선)
    if (elements.modalTitle) {
        elements.modalTitle.textContent = article.title_ko || article.title;
    }
    
    // 메타 정보
    if (elements.modalMeta) {
        const meta = [];
        if (article.source) meta.push(`소스: ${getSourceName(article.source)}`);
        if (article.score) meta.push(`점수: ${Math.round(article.score)}`);
        if (article.published) meta.push(`날짜: ${formatDate(article.published)}`);
        
        elements.modalMeta.innerHTML = meta.join(' • ');
    }
    
    // 요약
    if (elements.modalSummary && article.summary) {
        elements.modalSummary.innerHTML = `
            <h4 class="font-semibold text-blue-800 dark:text-blue-200 mb-2">
                <i class="fas fa-file-text mr-2"></i>요약
            </h4>
            <p class="text-blue-700 dark:text-blue-300">${article.summary}</p>
        `;
        elements.modalSummary.classList.remove('hidden');
    } else if (elements.modalSummary) {
        elements.modalSummary.classList.add('hidden');
    }
    
    // 태그
    if (elements.modalTags && article.tags && article.tags.length > 0) {
        const tagsHTML = article.tags.map(tag => 
            `<span class="tag ${getTagClass(tag)} mr-2 mb-2">${tag}</span>`
        ).join('');
        
        elements.modalTags.innerHTML = `
            <h4 class="font-semibold text-gray-800 dark:text-gray-200 mb-2">
                <i class="fas fa-tags mr-2"></i>태그
            </h4>
            <div class="flex flex-wrap">${tagsHTML}</div>
        `;
    }
    
    // 번역된 전문 (사용자 요구사항)
    if (elements.modalContent) {
        const content = article.content_ko || article.content || '내용을 불러올 수 없습니다.';
        elements.modalContent.innerHTML = formatContent(content);
    }
    
    // 원문 설정 (토글 가능)
    if (elements.originalContent && article.content && article.content_ko) {
        elements.originalContent.innerHTML = formatContent(article.content);
        if (elements.toggleOriginalBtn) {
            elements.toggleOriginalBtn.style.display = article.content !== article.content_ko ? 'inline-flex' : 'none';
        }
    }
    
    // 외부 링크 설정
    if (elements.openOriginalBtn) {
        elements.openOriginalBtn.onclick = () => openOriginalLink(article.url);
    }
}

/**
 * 글 모달 닫기
 */
function closeArticleModal() {
    if (elements.articleModal) {
        elements.articleModal.classList.add('hidden');
        document.body.style.overflow = '';
    }
    
    // 원문 숨기기
    if (elements.modalOriginal) {
        elements.modalOriginal.classList.add('hidden');
    }
    
    currentArticleId = null;
}

/**
 * 원문 텍스트 토글
 */
function toggleOriginalText() {
    if (!elements.modalOriginal || !elements.toggleOriginalBtn) return;
    
    const isVisible = !elements.modalOriginal.classList.contains('hidden');
    
    if (isVisible) {
        elements.modalOriginal.classList.add('hidden');
        elements.toggleOriginalBtn.innerHTML = '<i class="fas fa-globe mr-2"></i>원문 보기';
    } else {
        elements.modalOriginal.classList.remove('hidden');
        elements.toggleOriginalBtn.innerHTML = '<i class="fas fa-globe mr-2"></i>원문 숨기기';
        
        // 원문 영역으로 스크롤
        elements.modalOriginal.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

/**
 * 원문 링크 열기 (사용자 요구사항: "원문 보기" 버튼)
 */
function openOriginalLink(url = null) {
    if (!url && currentArticleId) {
        const article = articlesData.find(a => a.id === currentArticleId);
        url = article?.url;
    }
    
    if (url) {
        window.open(url, '_blank', 'noopener,noreferrer');
        showToast('원문 사이트로 이동합니다', 'info');
    } else {
        showToast('원문 링크를 찾을 수 없습니다', 'error');
    }
}

/**
 * 읽은 글로 표시 (사용자 요구사항: 읽은 글 체크 표시)
 */
function markAsRead(articleId = null, showToastMessage = true) {
    const id = articleId || currentArticleId;
    if (!id) return;
    
    // localStorage에 저장
    const readArticles = getReadArticles();
    if (!readArticles.includes(id)) {
        readArticles.push(id);
        setReadArticles(readArticles);
        
        if (showToastMessage) {
            showToast('읽음 표시되었습니다', 'success');
        }
    }
    
    // UI 업데이트
    const card = document.querySelector(`[data-article-id="${id}"]`);
    if (card) {
        markCardAsRead(card, true);
    }
    
    // API 호출 (선택적 - 서버에 기록)
    fetch('/api/mark-read', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ article_id: id })
    }).catch(error => {
        console.warn('서버 읽음 상태 기록 실패:', error);
    });
}

/**
 * 카드를 읽은 상태로 표시
 */
function markCardAsRead(card, animate = true) {
    if (!card) return;
    
    card.classList.add('read');
    
    const readIndicator = card.querySelector('.read-indicator');
    if (readIndicator) {
        if (animate) {
            readIndicator.style.opacity = '0';
            setTimeout(() => {
                readIndicator.style.opacity = '1';
            }, 100);
        } else {
            readIndicator.style.opacity = '1';
        }
    }
}

/**
 * 읽은 글 목록 가져오기
 */
function getReadArticles() {
    try {
        const stored = localStorage.getItem(CONFIG.STORAGE_KEYS.READ_ARTICLES);
        return stored ? JSON.parse(stored) : [];
    } catch (error) {
        console.warn('읽은 글 목록 로드 실패:', error);
        return [];
    }
}

/**
 * 읽은 글 목록 저장
 */
function setReadArticles(articles) {
    try {
        // 최근 1000개만 유지 (성능 최적화)
        const trimmedArticles = articles.slice(-1000);
        localStorage.setItem(CONFIG.STORAGE_KEYS.READ_ARTICLES, JSON.stringify(trimmedArticles));
    } catch (error) {
        console.warn('읽은 글 목록 저장 실패:', error);
    }
}

/**
 * 글 정렬
 */
function sortArticles(criteria) {
    if (!elements.articlesGrid) return;
    
    const cards = Array.from(elements.articlesGrid.children);
    
    cards.sort((a, b) => {
        switch (criteria) {
            case 'score':
                return parseFloat(b.dataset.score || 0) - parseFloat(a.dataset.score || 0);
            case 'date':
                return new Date(b.dataset.published) - new Date(a.dataset.published);
            case 'source':
                return a.dataset.source.localeCompare(b.dataset.source);
            default:
                return 0;
        }
    });
    
    // 부드러운 애니메이션과 함께 재배치
    cards.forEach((card, index) => {
        card.style.order = index;
        card.style.animation = 'fadeIn 0.3s ease-out';
        elements.articlesGrid.appendChild(card);
    });
    
    showToast(`${getSortName(criteria)} 정렬되었습니다`, 'info');
}

/**
 * 글 필터링
 */
function filterArticles(filter) {
    const cards = document.querySelectorAll('.article-card');
    let visibleCount = 0;
    const readArticles = getReadArticles();
    
    cards.forEach(card => {
        let show = true;
        const articleId = card.dataset.articleId;
        const source = card.dataset.source;
        const isRead = readArticles.includes(articleId);
        
        switch (filter) {
            case 'reddit':
                show = source === 'reddit';
                break;
            case 'naver_d2':
                show = source === 'naver_d2';
                break;
            case 'kakao_tech':
                show = source === 'kakao_tech';
                break;
            case 'ai_times':
                show = source === 'ai_times';
                break;
            case 'unread':
                show = !isRead;
                break;
            case 'all':
            default:
                show = true;
        }
        
        if (show) {
            card.style.display = 'block';
            card.classList.add('fade-in');
            visibleCount++;
        } else {
            card.style.display = 'none';
            card.classList.remove('fade-in');
        }
    });
    
    // 필터 결과 표시
    showFilterResults(filter, visibleCount);
}

/**
 * 필터 결과 표시
 */
function showFilterResults(filter, count) {
    // 기존 결과 메시지 제거
    const existingMessage = document.querySelector('.filter-results');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    if (filter !== 'all' && elements.articlesGrid) {
        const message = document.createElement('div');
        message.className = 'filter-results text-sm text-gray-600 dark:text-gray-400 mb-4 p-3 bg-blue-50 dark:bg-blue-900 rounded-lg border border-blue-200 dark:border-blue-700 animate-fade-in';
        message.innerHTML = `<i class="fas fa-filter mr-2"></i>${count}개의 글이 "${getFilterName(filter)}" 조건과 일치합니다.`;
        
        elements.articlesGrid.parentNode.insertBefore(message, elements.articlesGrid);
        
        // 3초 후 자동 제거
        setTimeout(() => {
            if (message.parentNode) {
                message.remove();
            }
        }, 5000);
    }
    
    showToast(`${count}개 글이 필터링되었습니다`, 'info');
}

/**
 * 글 수집 (API 호출 및 에러 처리)
 */
async function collectArticles() {
    if (isCollecting) return;
    
    isCollecting = true;
    
    // UI 업데이트
    if (elements.collectIcon) {
        elements.collectIcon.classList.add('spin');
    }
    if (elements.collectBtn) {
        elements.collectBtn.disabled = true;
        elements.collectBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i><span class="hidden sm:inline">수집 중...</span>';
    }
    
    showToast('글 수집을 시작합니다...', 'info');
    
    try {
        const response = await fetch('/api/collect', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast(result.message || '수집이 완료되었습니다', 'success');
            
            // 3초 후 새로고침
            setTimeout(() => {
                window.location.reload();
            }, 3000);
        } else {
            throw new Error(result.error || '수집 중 오류가 발생했습니다');
        }
        
    } catch (error) {
        console.error('수집 실패:', error);
        showToast(`수집 실패: ${error.message}`, 'error');
    } finally {
        isCollecting = false;
        
        // UI 복원
        if (elements.collectIcon) {
            elements.collectIcon.classList.remove('spin');
        }
        if (elements.collectBtn) {
            elements.collectBtn.disabled = false;
            elements.collectBtn.innerHTML = '<i class="fas fa-sync-alt mr-2"></i><span class="hidden sm:inline">수집하기</span>';
        }
    }
}

/**
 * 토스트 알림 표시
 */
function showToast(message, type = 'info') {
    if (!elements.toast) return;
    
    const toastIcon = elements.toast.querySelector('#toastIcon');
    const toastMessage = elements.toast.querySelector('#toastMessage');
    
    // 아이콘 설정
    const icons = {
        success: '<i class="fas fa-check-circle text-green-500"></i>',
        error: '<i class="fas fa-exclamation-circle text-red-500"></i>',
        warning: '<i class="fas fa-exclamation-triangle text-yellow-500"></i>',
        info: '<i class="fas fa-info-circle text-blue-500"></i>'
    };
    
    if (toastIcon) toastIcon.innerHTML = icons[type] || icons.info;
    if (toastMessage) toastMessage.textContent = message;
    
    // 표시
    elements.toast.classList.remove('hidden');
    elements.toast.classList.add('show');
    
    // 자동 숨김
    setTimeout(() => {
        elements.toast.classList.remove('show');
        elements.toast.classList.add('hide');
        
        setTimeout(() => {
            elements.toast.classList.add('hidden');
            elements.toast.classList.remove('hide');
        }, CONFIG.ANIMATION_DURATION);
    }, CONFIG.TOAST_DURATION);
}

/**
 * 유틸리티 함수들
 */

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function formatDate(dateString) {
    try {
        const date = new Date(dateString);
        const now = new Date();
        const diffTime = Math.abs(now - date);
        const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
        
        if (diffDays === 0) return '오늘';
        if (diffDays === 1) return '어제';
        if (diffDays < 7) return `${diffDays}일 전`;
        
        return date.toLocaleDateString('ko-KR');
    } catch (e) {
        return dateString.split('T')[0];
    }
}

function formatContent(content) {
    if (!content) return '';
    
    let formatted = content.replace(/\n/g, '<br>');
    
    // URL을 링크로 변환
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    formatted = formatted.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener noreferrer" class="text-blue-600 dark:text-blue-400 hover:underline">$1</a>');
    
    // 코드 블록 스타일링
    formatted = formatted.replace(/`([^`]+)`/g, '<code class="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded text-sm font-mono">$1</code>');
    
    return formatted;
}

function getSourceName(source) {
    const sourceNames = {
        'reddit': 'Reddit',
        'naver_d2': '네이버 D2',
        'kakao_tech': '카카오테크',
        'ai_times': 'AI타임스'
    };
    return sourceNames[source] || source;
}

function getSortName(criteria) {
    const sortNames = {
        'score': '품질 점수순으로',
        'date': '최신순으로',
        'source': '소스순으로'
    };
    return sortNames[criteria] || '기본순으로';
}

function getFilterName(filter) {
    const filterNames = {
        'reddit': 'Reddit',
        'naver_d2': '네이버 D2',
        'kakao_tech': '카카오테크',
        'ai_times': 'AI타임스',
        'unread': '읽지 않은 글'
    };
    return filterNames[filter] || filter;
}

function getTagClass(tag) {
    const tagClasses = {
        'LLM': 'tag-llm',
        '시계열': 'tag-timeseries',
        '머신러닝': 'tag-ml',
        '딥러닝': 'tag-dl',
        'Python': 'tag-python'
    };
    return tagClasses[tag] || '';
}

function updateLastVisit() {
    localStorage.setItem(CONFIG.STORAGE_KEYS.LAST_VISIT, new Date().toISOString());
}

// 전역 함수로 노출 (HTML에서 사용)
window.showArticleModal = showArticleModal;
window.closeArticleModal = closeArticleModal;
window.toggleOriginalText = toggleOriginalText;
window.openOriginalLink = openOriginalLink;
window.markAsRead = markAsRead;
window.sortArticles = sortArticles;
window.filterArticles = filterArticles;
window.collectArticles = collectArticles;
window.toggleDarkMode = toggleDarkMode;