const API_BASE_URL = "https://43.201.150.34/api/v1/"; // API 기본 URL

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

// 리뷰 코맨트 가져오기 함수
async function getReviews(moviePk) {
    try {
        const response = await axios.get(`${API_BASE_URL}reviews/${moviePk}/`);
        const reviews = response.data;

        // 각 리뷰에 대한 댓글을 동시에 가져오기 (Promise.all 활용)
        const commentPromises = reviews.map(review => {
            return axios.get(`${API_BASE_URL}reviews/${review.id}/comments/`);
        });
        const commentResponses = await Promise.all(commentPromises);

        // 각 리뷰에 댓글 할당
        reviews.forEach((review, index) => {
            review.comments = commentResponses[index].data;
        });

        console.log('리뷰 및 댓글 가져오기 성공:', reviews);
        return reviews;
    } catch (error) {
        console.error('리뷰 가져오기 실패:', error);
        throw error;
    }
}

// 리뷰 목록 갱신 함수
async function refreshReviews(moviePk) {
    try {
        const reviews = await getReviews(moviePk);
        displayReviews(reviews);
    } catch (error) {
        console.error('리뷰 목록 갱신 실패:', error);
        alert('리뷰 목록을 가져오는데 실패했습니다.');
    }
}

// 공통 에러 처리 함수
function handleError(action, error) {
    console.error(`${action} 실패:`, error.response ? error.response.data : error.message);
    alert(`${action} 실패`);
}

// 리뷰 좋아요 토글 함수
async function toggleLike(reviewId) {
    try {
        const response = await axios.post(`${API_BASE_URL}reviews/likes/review/${reviewId}/`);
        alert(response.data.message);
        await refreshReviews(document.getElementById('moviePkInput').value);
    } catch (error) {
        handleError('좋아요 처리', error);
    }
}

// 리뷰 작성하기 함수
async function postReview(moviePk, content) {
    if (!content.trim()) {
        alert('리뷰 내용을 입력해주세요.');
        return;
    }

    try {
        await axios.post(`${API_BASE_URL}reviews/${moviePk}/`, { content });
        alert('리뷰 작성 성공');
        await refreshReviews(moviePk);
    } catch (error) {
        handleError('리뷰 작성', error);
    }
}

// 리뷰 수정하기 함수
async function updateReview(reviewId, content) {
    if (!content.trim()) {
        alert('수정할 내용을 입력해주세요.');
        return;
    }

    try {
        await axios.put(`${API_BASE_URL}reviews/detail/${reviewId}/`, { content });
        alert('리뷰 수정 성공');
        await refreshReviews(document.getElementById('moviePkInput').value);
    } catch (error) {
        handleError('리뷰 수정', error);
    }
}

// 리뷰 삭제하기 함수
async function deleteReview(reviewId) {
    try {
        await axios.delete(`${API_BASE_URL}reviews/detail/${reviewId}/`);
        alert('리뷰 삭제 성공');
        await refreshReviews(document.getElementById('moviePkInput').value);
    } catch (error) {
        handleError('리뷰 삭제', error);
    }
}

// 댓글 작성하기 함수
async function postComment(reviewId, content) {
    if (!content.trim()) {
        alert('댓글 내용을 입력해주세요.');
        return;
    }

    try {
        await axios.post(`${API_BASE_URL}reviews/${reviewId}/comments/`, { content });
        alert('댓글 작성 성공');
        await refreshReviews(document.getElementById('moviePkInput').value);
    } catch (error) {
        handleError('댓글 작성', error);
    }
}

// 댓글 수정하기 함수
async function updateComment(reviewId, commentId, content) {
    if (!content.trim()) {
        alert('수정할 댓글 내용을 입력해주세요.');
        return;
    }

    try {
        await axios.put(`${API_BASE_URL}reviews/${reviewId}/comments/${commentId}/`, { content });
        alert('댓글 수정 성공');
        await refreshReviews(document.getElementById('moviePkInput').value);
    } catch (error) {
        handleError('댓글 수정', error);
    }
}

// 댓글 삭제하기 함수
async function deleteComment(reviewId, commentId) {
    try {
        await axios.delete(`${API_BASE_URL}reviews/${reviewId}/comments/${commentId}/`);
        alert('댓글 삭제 성공');
        await refreshReviews(document.getElementById('moviePkInput').value);
    } catch (error) {
        handleError('댓글 삭제', error);
    }
}

// 댓글 좋아요 토글 함수
async function toggleCommentLike(commentId) {
    try {
        const response = await axios.post(`${API_BASE_URL}reviews/likes/comment/${commentId}/`);
        alert(response.data.message);
        await refreshReviews(document.getElementById('moviePkInput').value);
    } catch (error) {
        handleError('댓글 좋아요 처리', error);
    }
}

// 리뷰 표시 함수
function displayReviews(reviews) {
    const responseDiv = document.getElementById('response');
    responseDiv.innerHTML = ''; // 기존 결과 초기화
    reviews.forEach(review => {
        const reviewDiv = document.createElement('div');
        reviewDiv.classList.add('review');
        reviewDiv.setAttribute('data-review-id', review.id);
        reviewDiv.innerHTML = `
            <div class="header">
                <span class="author">${review.author}</span>
                <span class="date">${new Date(review.created_at).toLocaleString()}</span>
            </div>
            <div class="content" id="review-content-${review.id}">${review.content}</div>
            <div class="footer">
                <span class="like-count">좋아요: ${review.like_count}</span>
                <span class="comment_count">댓글수: ${review.comments.length}</span>
                <span class="like-text" data-review-id="${review.id}">[❤]</span>
                <span class="edit-text" data-review-id="${review.id}">[수정]</span>
                <span class="delete-text" data-review-id="${review.id}">[삭제]</span>
                <textarea id="edit-content-${review.id}" style="display:none;"></textarea>
                <button class="save-btn" data-review-id="${review.id}" style="display:none;">수정 완료</button>
                <span class="comment-text" data-review-id="${review.id}">[댓글 달기]</span>
                <textarea id="comment-content-${review.id}" style="display:none;" placeholder="댓글을 입력하세요..."></textarea>
                <button class="submit-comment-btn" data-review-id="${review.id}" style="display:none;">댓글 작성 완료</button>
                <div class="comments" id="comments-${review.id}">
                    ${review.comments.map(comment => `
                        <div class="comment" id="comment-${comment.id}">
                            <span class="comment-author">${comment.author}</span>: 
                            <span class="comment-content" id="comment-content-${comment.id}">${comment.content}</span>
                            <span class="comment-like-count">좋아요: ${comment.like_count}</span>
                            <span class="comment-like-text" data-comment-id="${comment.id}">[❤]</span>
                            <span class="comment-edit-text" data-comment-id="${comment.id}">[수정]</span>
                            <span class="comment-delete-text" data-comment-id="${comment.id}">[삭제]</span>
                            <textarea id="edit-comment-${comment.id}" style="display:none;"></textarea>
                            <button class="save-comment-btn" data-comment-id="${comment.id}" style="display:none;">수정 완료</button>
                        </div>
                    `).join('')}
                </div>
            `;
            responseDiv.appendChild(reviewDiv);
        });

    // 이벤트 리스너 추가
    addEventListeners();
    }

// 이벤트 리스너 추가 함수
function addEventListeners() {
    // 리뷰 좋아요 버튼 이벤트 리스너
    document.querySelectorAll('.like-text').forEach(button => {
        button.addEventListener('click', async (event) => {
            const reviewId = event.target.getAttribute('data-review-id');
            await toggleLike(reviewId);
        });
    });

    // 리뷰 수정 버튼 이벤트 리스너
    document.querySelectorAll('.edit-text').forEach(button => {
        button.addEventListener('click', (event) => {
            const reviewId = event.target.getAttribute('data-review-id');
            const contentDiv = document.getElementById(`review-content-${reviewId}`);
            const editTextArea = document.getElementById(`edit-content-${reviewId}`);
            const saveButton = document.querySelector(`.save-btn[data-review-id="${reviewId}"]`);

            editTextArea.value = contentDiv.innerText;
            contentDiv.style.display = 'none';
            editTextArea.style.display = 'block';
            saveButton.style.display = 'inline';
        });
    });

    // 리뷰 수정 완료 버튼 이벤트 리스너
    document.querySelectorAll('.save-btn').forEach(button => {
        button.addEventListener('click', async (event) => {
            const reviewId = event.target.getAttribute('data-review-id');
            const editTextArea = document.getElementById(`edit-content-${reviewId}`);
            const newContent = editTextArea.value;
            await updateReview(reviewId, newContent);
        });
    });

    // 리뷰 삭제 버튼 이벤트 리스너
    document.querySelectorAll('.delete-text').forEach(button => {
        button.addEventListener('click', async (event) => {
            const reviewId = event.target.getAttribute('data-review-id');
            await deleteReview(reviewId);
        });
    });

    // 댓글 달기 버튼 이벤트 리스너
    document.querySelectorAll('.comment-text').forEach(button => {
        button.addEventListener('click', (event) => {
            const reviewId = event.target.getAttribute('data-review-id');
            const commentTextArea = document.getElementById(`comment-content-${reviewId}`);
            const submitButton = document.querySelector(`.submit-comment-btn[data-review-id="${reviewId}"]`);

            commentTextArea.style.display = 'block';
            submitButton.style.display = 'inline';
        });
    });

    // 댓글 작성 완료 버튼 이벤트 리스너
    document.querySelectorAll('.submit-comment-btn').forEach(button => {
        button.addEventListener('click', async (event) => {
            const reviewId = event.target.getAttribute('data-review-id');
            const commentTextArea = document.getElementById(`comment-content-${reviewId}`);
            const content = commentTextArea.value;
            await postComment(reviewId, content);
        });
    });

    // 댓글 좋아요 버튼 이벤트 리스너
    document.querySelectorAll('.comment-like-text').forEach(button => {
        button.addEventListener('click', async (event) => {
            const commentId = event.target.getAttribute('data-comment-id');
            await toggleCommentLike(commentId);
        });
    });

    // 댓글 수정 버튼 이벤트 리스너
    document.querySelectorAll('.comment-edit-text').forEach(button => {
        button.addEventListener('click', (event) => {
            const commentId = event.target.getAttribute('data-comment-id');
            const contentSpan = document.getElementById(`comment-content-${commentId}`);
            const editTextArea = document.getElementById(`edit-comment-${commentId}`);
            const saveButton = document.querySelector(`.save-comment-btn[data-comment-id="${commentId}"]`);

            editTextArea.value = contentSpan.innerText;
            contentSpan.style.display = 'none';
            editTextArea.style.display = 'block';
            saveButton.style.display = 'inline';
        });
    });

    // 댓글 수정 완료 버튼 이벤트 리스너
    document.querySelectorAll('.save-comment-btn').forEach(button => {
        button.addEventListener('click', async (event) => {
            const commentId = event.target.getAttribute('data-comment-id');
            const reviewId = event.target.closest('.review').getAttribute('data-review-id');
            const editTextArea = document.getElementById(`edit-comment-${commentId}`);
            const newContent = editTextArea.value;
            await updateComment(reviewId, commentId, newContent);
        });
    });

    // 댓글 삭제 버튼 이벤트 리스너
    document.querySelectorAll('.comment-delete-text').forEach(button => {
        button.addEventListener('click', async (event) => {
            const commentId = event.target.getAttribute('data-comment-id');
            const reviewId = event.target.closest('.review').getAttribute('data-review-id');
            await deleteComment(reviewId, commentId);
        });
    });
}

// 페이지 로드 시 이벤트 리스너 설정
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('loginBtn').addEventListener('click', () => {
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        login(email, password);
    });

    document.getElementById('logoutBtn').addEventListener('click', logout);

    document.getElementById('getReviewsBtn').addEventListener('click', async () => {
        const moviePk = document.getElementById('moviePkInput').value;
        const reviews = await getReviews(moviePk);
        displayReviews(reviews);
    });

    document.getElementById('postReviewBtn').addEventListener('click', () => {
        const moviePk = document.getElementById('moviePkInput').value;
        const content = document.getElementById('reviewContent').value;
        postReview(moviePk, content);
    });
});