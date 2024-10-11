const API_BASE_URL = 'https://api.popcorngeek.store/api/v1/'

// 토큰 저장 및 관리 함수
const tokenManager = {
    getAccessToken: () => sessionStorage.getItem('jwtAccessToken'),
    getRefreshToken: () => sessionStorage.getItem('jwtRefreshToken'),
    setTokens: ({ access, refresh }) => {
        sessionStorage.setItem('jwtAccessToken', access);
        sessionStorage.setItem('jwtRefreshToken', refresh);
    },
    clearTokens: () => {
        sessionStorage.removeItem('jwtAccessToken');
        sessionStorage.removeItem('jwtRefreshToken');
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

// url주소에서 데이터 추출
const urlParams = new URLSearchParams(window.location.search);

// 메인페이지 영화 정보 가져오기
const fetchMovies = () => {
    axios.get(`${API_BASE_URL}movies/`)
        .then(response => {
            const moviepk = urlParams.get('pk');
            if (moviepk) {
                fetchMovieDetails(moviepk);
            }

            renderBoxOfficeMovies(response.data.boxoffice_movies); // 박스오피스 순 영화 출력
            renderGradedMovies(response.data.graded_movies);       // 평균 평점 순 영화 출력
            renderLikedMovies(response.data.liked_movies);         // 좋아요 순 영화 출력
            renderComingMovies(response.data.coming_movies);       // 개봉 예정작 출력
        })
        .catch(error => {
            console.error('Error fetching movies:', error);
        });
};

// 영화 상세페이지
function fetchMovieDetails(moviepk) {
    axios.get(`${API_BASE_URL}movies/${moviepk}/`)
        .then(response => {
            const movie = response.data;

            // 제목, 장르, 줄거리 설정
            document.getElementById('movie-title').textContent = movie.title;
            const genreNames = movie.genre.map(genre => genre.name).join(', ');
            document.getElementById('movie-genre').textContent = genreNames;
            document.getElementById('movie-plot').textContent = movie.plot;

            // 포스터 설정
            const posterImage = document.getElementById('movie-poster');
            const posterUrl = movie.poster.startsWith('http') ? movie.poster : `${API_BASE_URL}${movie.poster}`;
            posterImage.src = posterUrl;
            posterImage.alt = `${movie.title} 포스터`;

            // 보고싶어요,관심없어요
            const likeButton = document.getElementById('like');
            const dislikeButton = document.getElementById('dislike');

            handleReaction(likeButton, moviepk, 'like');
            handleReaction(dislikeButton, moviepk, 'dislike');

            // 평점
            const scoreButton = document.getElementById('score-button');
            const scoreInput = document.getElementById('score-input');
            const cancelButton = document.getElementById('cancel-score');

            // 평가하기
            scoreButton.addEventListener('click', (event) => {
                event.preventDefault();

                const scoreValue = parseFloat(scoreInput.value);
                const scoreData = {
                    evaluate: scoreValue
                };

                sendScoreData(moviepk, scoreData);
            });

            // 취소하기
            cancelButton.addEventListener('click', () => {
                const scoreData = {
                    evaluate: 0
                };
                // 리뷰 출력
                sendScoreData(moviepk, scoreData);
            });

            refreshReviews(moviepk);

            document.getElementById('postReviewBtn').addEventListener('click', () => {
                const content = document.getElementById('reviewContent').value;
                postReview(moviepk, content);
            });
        })
        .catch(error => {
            console.error('Error fetching movie details:', error);
        });
}

// 박스오피스순 출력
const renderBoxOfficeMovies = (boxofficeMovies) => {
    const boxofficeList = document.getElementById('boxoffice-movies-list');
    boxofficeMovies.forEach(movie => {
        const card = createMovieCard(movie, movie.movie_pk, `${movie.rank}위`);
        boxofficeList.appendChild(card);
    });
};

// 평균 평점순 출력
const renderGradedMovies = (gradedMovies) => {
    const gradedList = document.getElementById('graded-movies-list');
    gradedMovies.forEach(movie => {
        const card = createMovieCard(movie, movie.id, `Average Grade: ${movie.average_grade || 0}`);
        gradedList.appendChild(card);
    });
};

// 좋아요 많은순 출력
const renderLikedMovies = (likedMovies) => {
    const likedList = document.getElementById('liked-movies-list');
    likedMovies.forEach(movie => {
        const card = createMovieCard(movie, movie.id, `Likes: ${movie.like || 0}`);
        likedList.appendChild(card);
    });
};

// 개봉예정작 출력
const renderComingMovies = (comingMovies) => {
    const comingList = document.getElementById('coming-movies-list');
    comingMovies.forEach(movie => {
        const card = createMovieCard(movie, movie.id, `Coming: ${movie.release_date}`);
        comingList.appendChild(card);
    });
};

// 영화 카드 생성
const createMovieCard = (movie, moviePk, infoText) => {
    const li = document.createElement('li');
    const card = document.createElement('div');
    card.classList.add('movie-card');

    const link = document.createElement('a');
    link.href = `/front/movies/details.html?pk=${moviePk}`;
    link.classList.add('movie-link');

    const posterImage = document.createElement('img');
    posterImage.src = movie.poster;
    posterImage.alt = `${movie.title} 포스터`;

    const title = document.createElement('h3');
    title.textContent = movie.title;

    const info = document.createElement('p');
    info.textContent = infoText;

    link.appendChild(posterImage);
    link.appendChild(title);
    link.appendChild(info);
    card.appendChild(link);
    li.appendChild(card);

    return li;
};

// 검색 기능
function initSearch() {
    const searchForm = document.getElementById('searchForm');

    if (searchForm) {
        searchForm.addEventListener('submit', handleSearchSubmit);
    }

    // URL에서 데이터 추출 및 검색 결과 처리
    const urlParams = new URLSearchParams(window.location.search);
    const searchKeyword = urlParams.get('search_keyword');
    const searchType = urlParams.get('search_type');

    if (searchKeyword) {
        fetchSearchResults(searchType, searchKeyword);
    }
}

// 검색어 제출
function handleSearchSubmit(event) {
    event.preventDefault();

    const searchKeyword = document.getElementById('search_keyword').value.trim();
    const searchType = document.getElementById('lang').value;

    // 검색어가 비어있을 경우
    if (!searchKeyword) {
        alert('검색어를 입력하세요.');
        return;
    }

    // 페이지 이동
    const searchUrl = `search.html?search_keyword=${encodeURIComponent(searchKeyword)}&search_type=${searchType}`;
    window.location.href = searchUrl;
}

// 검색 결과 가져오기
function fetchSearchResults(searchType, searchKeyword) {
    axios.get(`${API_BASE_URL}movies/search/?search_type=${searchType}&search_keyword=${encodeURIComponent(searchKeyword)}`)
        .then(response => {
            displaySearchResults(response.data, searchType);
        })
        .catch(error => {
            console.error('검색 결과를 가져오는 중 오류 발생:', error);
        });
}

// 검색 결과
function displaySearchResults(results, searchType) {
    const resultsList = document.getElementById('searchresults');
    resultsList.innerHTML = '';

    // 검색 결과를 출력
    results.forEach(item => {
        if (searchType === 'movies') {
            // 영화 카드 생성
            const movieCard = document.createElement('div');
            movieCard.classList.add('movie-card');

            // 영화 포스터
            const posterUrl = item.poster.startsWith('http') ? item.poster : `${API_BASE_URL}${item.poster}`; // 포스터 URL 설정

            // 영화 링크
            const movieLink = document.createElement('a');
            movieLink.href = `/front/movies/details.html?pk=${item.id}`;

            // 영화 포스터 이미지를 링크에 추가
            const moviePoster = document.createElement('img');
            moviePoster.src = posterUrl ? posterUrl : 'placeholder_image_url'; // 포스터가 없으면 기본 이미지 사용
            moviePoster.alt = `${item.title} 포스터`;
            movieLink.appendChild(moviePoster); // 포스터를 링크에 추가

            // 영화 제목
            const movieTitle = document.createElement('h3');
            movieTitle.textContent = item.title;

            // 장르 정보
            const genreNames = item.genre.map(genre => genre.name).join(', ');
            const movieGenre = document.createElement('p');
            movieGenre.textContent = `장르: ${genreNames}`;

            // 영화 카드 구성
            movieCard.appendChild(movieLink); // 영화 링크를 카드에 추가
            movieCard.appendChild(movieTitle);
            movieCard.appendChild(movieGenre);

            // 카드 추가
            resultsList.appendChild(movieCard);
        } else if (searchType === 'staff') {
            const li = document.createElement('li');
            li.textContent = `이름: ${item.name}`;
            resultsList.appendChild(li);
        } else if (searchType === 'member') {
            const li = document.createElement('li');
            li.textContent = `닉네임: ${item.nickname}`;
            resultsList.appendChild(li);
        }
    });
}

// 초기화 함수
initSearch();

// 보고싶어요, 관심없어요 데이터 전송
function sendLikeData(moviepk, movieData) {
    axios.post(`${API_BASE_URL}movies/${moviepk}/`, movieData)
        .then(response => {
            console.log('영화 정보가 성공적으로 전송되었습니다:', response.data);
        })
        .catch(error => {
            console.error('영화 정보 전송 중 오류가 발생했습니다:', error);
        });
}

// 보고싶어요, 관심 없어요 로직 처리
function handleReaction(button, moviepk, reactionType) {
    button.addEventListener('click', () => {
        const movieData = {};
        movieData[reactionType] = reactionType;
        sendLikeData(moviepk, movieData);
    });
}

// 영화 평가하기 데이터 전송
function sendScoreData(moviepk, scoreData) {
    axios.post(`${API_BASE_URL}movies/${moviepk}/score/`, scoreData)
        .then(response => {
            console.log('성공적으로 전송되었습니다:', response.data);
        })
        .catch(error => {
            console.error('전송 중 오류가 발생했습니다:', error);
        });
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
    // Axios 오류만 처리
    if (error.isAxiosError) {
        console.error(`${action} 실패:`, error.response ? error.response.data : error.message);
        alert(`${action} 실패`);
    }
}

// 리뷰 좋아요 토글 함수
async function toggleLike(reviewId) {
    try {
        const response = await axios.post(`${API_BASE_URL}reviews/likes/review/${reviewId}/`);
        alert(response.data.message);
    } catch (error) {
        handleError('좋아요 처리', error);
    }
}

// 리뷰 작성하기 함수 수정
async function postReview(moviePk, content) {
    if (!content.trim()) {
        alert('리뷰 내용을 입력해주세요.');
        return;
    }

    const isSpoiler= document.getElementById('isSpoiler').checked;

    try {
        await axios.post(`${API_BASE_URL}reviews/${moviePk}/`, { content, is_spoiler: isSpoiler });
        
        alert('리뷰 작성 성공');
        await refreshReviews(moviePk);
        document.getElementById('reviewContent').value = ''; // 입력 필드 초기화
        document.getElementById('isSpoiler').checked = false; // 체크박스 초기화
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
    } catch (error) {
        handleError('리뷰 수정', error);
    }
}

// 리뷰 삭제하기 함수
async function deleteReview(reviewId) {
    try {
        await axios.delete(`${API_BASE_URL}reviews/detail/${reviewId}/`);
        alert('리뷰 삭제 성공');
    } catch (error) {
        handleError('리뷰 삭제', error);
    }
}

// 리뷰 신고 함수
async function reportReview(reviewId) {
    try {
        const response = await axios.post(`${API_BASE_URL}reviews/report/review/${reviewId}/`);
        console.log(response);
        alert(response.data.message);

    } catch (error) {
        console.log(error)
        alert(error.response.data.message)
    }
}


// 댓글 작성하기 함수
async function postComment(reviewId, content) {
    if (!content.trim()) {
        alert('댓글 내용을 입력해주세요.');
        return;
    }

    const isSpoiler = document.getElementById(`comment-is-spoiler-${reviewId}`).checked;

    try {
        await axios.post(`${API_BASE_URL}reviews/${reviewId}/comments/`, { content, is_spoiler: isSpoiler });
        alert('댓글 작성 성공');
        // 댓글 작성 후 입력 필드 및 체크박스 초기화
        document.getElementById(`comment-content-${reviewId}`).value = '';
        document.getElementById(`comment-is-spoiler-${reviewId}`).checked = false;
        await refreshReviews(moviepk); 
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
    } catch (error) {
        handleError('댓글 수정', error);
    }
}

// 댓글 삭제하기 함수
async function deleteComment(reviewId, commentId) {
    try {
        await axios.delete(`${API_BASE_URL}reviews/${reviewId}/comments/${commentId}/`);
        alert('댓글 삭제 성공');
    } catch (error) {
        handleError('댓글 삭제', error);
    }
}

// 댓글 좋아요 토글 함수
async function toggleCommentLike(commentId) {
    try {
        const response = await axios.post(`${API_BASE_URL}reviews/likes/comment/${commentId}/`);
        alert(response.data.message);
    } catch (error) {
        handleError('댓글 좋아요 처리', error);
    }
}

// 댓글 신고 함수
async function reportComment(commentId) {
    try {
        const response = await axios.post(`${API_BASE_URL}reviews/report/comment/${commentId}/`);
        console.log(response);
        alert(response.data.message);

    } catch (error) {
        console.log(error)
        alert(error.response.data.message)
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

        let contentHTML;
        if (review.is_spoiler) {
            contentHTML = `<div class="content spoiler" id="review-content-${review.id}">${review.content}</div>`;
        } else {
            contentHTML = `<div class="content" id="review-content-${review.id}">${review.content}</div>`;
        }

        reviewDiv.innerHTML = `
            <div class="header">
                <span class="author">${review.author}</span>
                <span class="date">${new Date(review.created_at).toLocaleString()}</span>
            </div>
            ${contentHTML}
            <div class="footer">
                <span class="like-count">좋아요: ${review.like_count}</span>
                <span class="comment_count">댓글수: ${review.comments.length}</span>
                <span class="like-text" data-review-id="${review.id}">[❤]</span>
                <span class="edit-text" data-review-id="${review.id}">[수정]</span>
                <span class="delete-text" data-review-id="${review.id}">[삭제]</span>
                <textarea id="edit-content-${review.id}" style="display:none;"></textarea>
                <button class="save-btn" data-review-id="${review.id}" style="display:none;">수정 완료</button>
                <span class="comment-text" data-review-id="${review.id}">[댓글 달기]</span>
                <span class="report-text" data-review-id="${review.id}">[신고]</span>
                <textarea id="comment-content-${review.id}" style="display:none;" placeholder="댓글을 입력하세요..."></textarea>
                <label style="display:none;" id="comment-is-spoiler-label-${review.id}">
                    <input type="checkbox" id="comment-is-spoiler-${review.id}">스포일러 포함</label>
                <button class="submit-comment-btn" data-review-id="${review.id}" style="display:none;">댓글 작성 완료</button>
                <div class="comments" id="comments-${review.id}">
                    ${review.comments.map(comment => {
                        // 스포일러 여부에 따라 댓글 콘텐츠 처리
                        let commentContentHTML;
                        if (comment.is_spoiler) {
                            commentContentHTML = `<span class="comment-content spoiler" id="comment-content-${comment.id}">${comment.content}</span>`;
                        } else {
                            commentContentHTML = `<span class="comment-content" id="comment-content-${comment.id}">${comment.content}</span>`;
                        }

                        return `
                            <div class="comment" id="comment-${comment.id}">
                                <span class="comment-author">${comment.author}</span>:
                                ${commentContentHTML}
                                <span class="comment-like-count">좋아요: ${comment.like_count}</span>
                                <span class="comment-like-text" data-comment-id="${comment.id}">[❤]</span>
                                <span class="comment-edit-text" data-comment-id="${comment.id}">[수정]</span>
                                <span class="comment-delete-text" data-comment-id="${comment.id}">[삭제]</span>
                                <span class="comment-report-text" data-comment-id="${comment.id}">[신고]</span>
                                <textarea id="edit-comment-${comment.id}" style="display:none;"></textarea>
                                <button class="save-comment-btn" data-comment-id="${comment.id}" style="display:none;">수정 완료</button>
                            </div>
                        `;
                    }).join('')}
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

    // 스포일러 내용 토글 이벤트 리스너
    document.querySelectorAll('.spoiler').forEach(element => {
        element.addEventListener('click', () => {
            element.classList.toggle('revealed');
        });
    });

    // 리뷰 신고 버튼 이벤트 리스너
    document.querySelectorAll('.report-text').forEach(button => {
        button.addEventListener('click', async (event) => {
            const reviewId = event.target.getAttribute('data-review-id');
            await reportReview(reviewId);
        })
    })

    // 댓글 달기 버튼 이벤트 리스너
    document.querySelectorAll('.comment-text').forEach(button => {
        button.addEventListener('click', (event) => {
            const reviewId = event.target.getAttribute('data-review-id');
            const commentTextArea = document.getElementById(`comment-content-${reviewId}`);
            const submitButton = document.querySelector(`.submit-comment-btn[data-review-id="${reviewId}"]`);
            const isSpoilerLabel = document.getElementById(`comment-is-spoiler-label-${reviewId}`);

            commentTextArea.style.display = 'block';
            submitButton.style.display = 'inline';
            isSpoilerLabel.style.display = 'inline';
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

    // 댓글 신고 버튼 이벤트 리스너
    document.querySelectorAll('.comment-report-text').forEach(button => {
        button.addEventListener('click', async (event) => {
            const commentId = event.target.getAttribute('data-comment-id');
            await reportComment(commentId);
        })
    })
}

async function transformReviewContent(style) {
    const reviewContent = document.getElementById('reviewContent').value.trim();
    if (!reviewContent) {
        alert('리뷰를 입력하세요.');
        return;
    }

    try {
        const response = await axios.post(`${API_BASE_URL}reviews/transform-review/`, {
            content: reviewContent,
            style: style  // 말투 스타일을 동적으로 전달
        });
        document.getElementById('reviewContent').value = response.data.transformedContent;
        alert('말투가 변환되었습니다.');
    } catch (error) {
        console.error('말투 변경 중 오류가 발생했습니다:', error);
    }
}

// 버튼별로 말투 스타일을 전달
document.getElementById('transformToJoseon').addEventListener('click', () => {
    transformReviewContent('조선시대');
});

document.getElementById('transformToCritic').addEventListener('click', () => {
    transformReviewContent('평론가');
});

document.getElementById('transformToMz').addEventListener('click', () => {
    transformReviewContent('Mz');
});