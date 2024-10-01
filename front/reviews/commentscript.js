const API_BASE_URL = "http://localhost:8000/api/v1/"; // API 기본 URL

// 토큰 저장 및 관리 함수
const tokenManager = {
    getAccessToken: () => localStorage.getItem('jwtAccessToken'),
    getRefreshToken: () => localStorage.getItem('jwtRefreshToken'),
    setTokens: ({ access, refresh }) => {
        localStorage.setItem('jwtAccessToken', access);
        localStorage.setItem('jwtRefreshToken', refresh);
    },
    clearTokens: () => {
        localStorage.removeItem('jwtAccessToken');
        localStorage.removeItem('jwtRefreshToken');
    },
    async refreshAccessToken() {
        const refreshToken = this.getRefreshToken();
        if (!refreshToken) {
            throw new Error('No refresh token available');
        }
        try {
            const response = await axios.post(`${API_BASE_URL}token/refresh/`, {
                refresh: refreshToken
            });
            this.setTokens(response.data); // 새로운 토큰 저장
            console.log('토큰이 갱신되었습니다:', response.data.access);
        } catch (error) {
            console.error('토큰 갱신 실패:', error.response ? error.response.data : error.message);
            this.clearTokens(); // 실패 시 토큰 제거
            throw error;
        }
    }
};

// Axios 요청 인터셉터 설정
axios.interceptors.request.use(
    async (config) => {
        let token = tokenManager.getAccessToken(); // access token 가져오기
        if (token) {
            config.headers.Authorization = `Bearer ${token}`; // 헤더에 토큰 추가
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Axios 응답 인터셉터 설정 (토큰 만료 시 갱신 및 재요청)
axios.interceptors.response.use(
    (response) => response, // 응답이 성공적일 때는 그대로 반환
    async (error) => {
        const originalRequest = error.config;

        if (error.response && error.response.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            try {
                await tokenManager.refreshAccessToken(); // 토큰 갱신
                const newAccessToken = tokenManager.getAccessToken(); // 갱신된 토큰 가져오기
                originalRequest.headers.Authorization = `Bearer ${newAccessToken}`; // 새로운 토큰 설정
                return axios(originalRequest); // 원래 요청 다시 시도
            } catch (err) {
                console.error('새로운 토큰으로 재요청 실패:', err);
                return Promise.reject(error);
            }
        }

        return Promise.reject(error);
    }
);

// 로그인 함수
async function login(email, password) {
    try {
        const response = await axios.post(`${API_BASE_URL}accounts/signin/`, { email, password });
        tokenManager.setTokens(response.data); // 로그인 성공 시 토큰 저장
        console.log('로그인 성공:', response.data);
        alert('로그인 성공');
    } catch (error) {
        console.error('로그인 실패:', error.response ? error.response.data : error.message);
        alert('로그인 실패');
    }
}

// 로그아웃 함수
function logout() {
    tokenManager.clearTokens(); // 저장된 토큰 삭제
    alert('로그아웃 성공');
}

// 코멘트 가져오기 함수
async function getComments(reviewPk) {
    try {
        const response = await axios.get(`${API_BASE_URL}reviews/${reviewPk}/comments/`);
        const comments = response.data;
        console.log('코멘트 가져오기 성공:', comments);
        return comments;
    } catch (error) {
        console.error('코멘트 가져오기 실패:', error);
        throw error;
    }
}

// 코멘트 표시 함수
function displayComments(comments) {
    const responseDiv = document.getElementById('response');
    responseDiv.innerHTML = ''; // 기존 결과 초기화
    comments.forEach(comment => {
        const commentDiv = document.createElement('div');
        commentDiv.innerHTML = `
            <div class="header">
                <span class="author">${comment.author}</span>
                <span class="date">${new Date(comment.created_at).toLocaleString()}</span>
            </div>
            <div class="content">${comment.content}</div>
            <div class="footer">
                <span class="like-count">좋아요: ${comment.like_count}</span>
                <button class="like-btn" data-comment-id="${comment.id}">좋아요</button>
            </div>
        `;
        responseDiv.appendChild(commentDiv); // 코멘트 추가
    });

    // 좋아요 버튼에 이벤트 리스너 추가
    const likeButtons = document.querySelectorAll('.like-btn');
    likeButtons.forEach(button => {
        button.addEventListener('click', async (event) => {
            const commentId = event.target.getAttribute('data-comment-id');
            await toggleLike(commentId);
        });
    });
}

// 좋아요 토글 함수
async function toggleLike(commentId) {
    try {
        const response = await axios.post(`${API_BASE_URL}reviews/likes/comment/${commentId}/`);
        console.log(response.data.message);
        alert(response.data.message);

        // 좋아요 변경 후 코멘트 목록 다시 가져오기
        const reviewPK = document.getElementById('commentPkInput').value;
        const comments = await getComments(reviewPK);
        displayComments(comments); // 코멘트를 화면에 표시하는 함수 호출
    } catch (error) {
        console.error('좋아요 처리 실패:', error.response ? error.response.data : error.message);
        alert('좋아요 처리 실패');
    }
}

// 코멘트 작성하기 함수
async function postComment(reviewPk, content) {
    if (!content.trim()) {
        alert('코멘트 내용을 입력해주세요.'); // 비어 있는 경우 경고
        return;
    }

    try {
        await axios.post(`${API_BASE_URL}reviews/${reviewPk}/comments/`, { content });
        console.log('코멘트 작성 성공');
        alert('코멘트 작성 성공');

        // 코멘트 작성 후 코멘트 목록 다시 가져오기
        await refreshComments(reviewPk); // 전체 코멘트 목록 갱신
    } catch (error) {
        console.error('코멘트 작성 실패:', error.response ? error.response.data : error.message);
        alert('코멘트 작성 실패');
    }
}

// 코멘트 목록 갱신 함수
async function refreshComments(reviewPk) {
    try {
        const comments = await getComments(reviewPk); // 코멘트 목록 가져오기
        displayComments(comments); // 화면에 코멘트 표시
    } catch (error) {
        console.error('코멘트 목록 갱신 실패:', error);
    }
}

// 버튼 이벤트 리스너 설정
document.getElementById('loginBtn').addEventListener('click', () => {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    login(email, password);
});

document.getElementById('logoutBtn').addEventListener('click', () => {
    logout();
});

document.getElementById('getCommentsBtn').addEventListener('click', async () => {
    const reviewPk = document.getElementById('commentPkInput').value;
    const comments = await getComments(reviewPk);
    displayComments(comments); // 코멘트를 화면에 표시하는 함수 호출
});

document.getElementById('postBtn').addEventListener('click', () => {
    const reviewPk = document.getElementById('commentPkInput').value;
    const content = document.getElementById('commentContent').value;
    postComment(reviewPk, content);
});
