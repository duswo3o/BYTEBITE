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

// 리뷰 가져오기 함수
async function getReviews(moviePk) {
    try {
        const response = await axios.get(`${API_BASE_URL}reviews/${moviePk}/`);
        const reviews = response.data;
        console.log('리뷰 가져오기 성공:', reviews);
        return reviews;
    } catch (error) {
        console.error('리뷰 가져오기 실패:', error);
        throw error;
    }
}

// 리뷰 표시 함수
function displayReviews(reviews) {
    const responseDiv = document.getElementById('response');
    responseDiv.innerHTML = ''; // 기존 결과 초기화
    reviews.forEach(review => {
        const reviewDiv = document.createElement('div');
        reviewDiv.innerHTML = `
            <div class="review-header">
                <span class="author">${review.author}</span>
                <span class="date">${new Date(review.created_at).toLocaleString()}</span>
            </div>
            <div class="content">${review.content}</div>
            <div class="review-footer">
                <span class="like-count">좋아요: ${review.like_count}</span>
                <button class="like-btn" data-review-id="${review.id}">좋아요</button>
            </div>
        `;
        responseDiv.appendChild(reviewDiv); // 리뷰 추가
    });

    // 좋아요 버튼에 이벤트 리스너 추가
    const likeButtons = document.querySelectorAll('.like-btn');
    likeButtons.forEach(button => {
        button.addEventListener('click', async (event) => {
            const reviewId = event.target.getAttribute('data-review-id');
            await toggleLike(reviewId);
        });
    });
}

// 좋아요 토글 함수
async function toggleLike(reviewId) {
    try {
        const response = await axios.post(`${API_BASE_URL}reviews/likes/review/${reviewId}/`);
        console.log(response.data.message);
        alert(response.data.message);

        // 좋아요 변경 후 리뷰 목록 다시 가져오기
        const moviePk = document.getElementById('moviePkInput').value;
        const reviews = await getReviews(moviePk);
        displayReviews(reviews); // 리뷰를 화면에 표시하는 함수 호출
    } catch (error) {
        console.error('좋아요 처리 실패:', error.response ? error.response.data : error.message);
        alert('좋아요 처리 실패');
    }
}


// 리뷰 작성하기 함수
async function postReview(moviePk, content) {
    if (!content.trim()) {
        alert('리뷰 내용을 입력해주세요.'); // 비어 있는 경우 경고
        return;
    }

    try {
        await axios.post(`${API_BASE_URL}reviews/${moviePk}/`, { content });
        console.log('리뷰 작성 성공');
        alert('리뷰 작성 성공');

        // 리뷰 작성 후 리뷰 목록 다시 가져오기
        await refreshReviews(moviePk); // 전체 리뷰 목록 갱신
    } catch (error) {
        console.error('리뷰 작성 실패:', error.response ? error.response.data : error.message);
        alert('리뷰 작성 실패');
    }
}
// 리뷰 목록 갱신 함수
async function refreshReviews(moviePk) {
    try {
        const reviews = await getReviews(moviePk); // 리뷰 목록 가져오기
        displayReviews(reviews); // 화면에 리뷰 표시
    } catch (error) {
        console.error('리뷰 목록 갱신 실패:', error);
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

document.getElementById('getReviewsBtn').addEventListener('click', async () => {
    const moviePk = document.getElementById('moviePkInput').value;
    const reviews = await getReviews(moviePk);
    displayReviews(reviews); // 리뷰를 화면에 표시하는 함수 호출
});

document.getElementById('postReviewBtn').addEventListener('click', () => {
    const moviePk = document.getElementById('moviePkInput').value;
    const content = document.getElementById('reviewContent').value;
    postReview(moviePk, content);
});
