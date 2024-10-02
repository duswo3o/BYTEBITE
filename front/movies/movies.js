const API_BASE_URL = 'http://127.0.0.1:8000/api/v1'

// 메인페이지 영화 정보 가져오기
axios.get(`${API_BASE_URL}/movies/`)
    .then(response => {
        // 박스오피스 순
        const boxofficeMovies = response.data.boxoffice_movies;
        const boxofficeList = document.getElementById('boxoffice-movies-list');
        boxofficeMovies.forEach(movie => {
            const li = document.createElement('li');
            li.textContent = `${movie.rank}위: ${movie.title}`;
            boxofficeList.appendChild(li);
        });

        // 평균 평점 순
        const gradedMovies = response.data.graded_movies;
        const gradedList = document.getElementById('graded-movies-list');
        gradedMovies.forEach(movie => {
            const li = document.createElement('li');

            const gradelink = document.createElement('a');
            gradelink.href = `http://127.0.0.1:5501/front/movies/details.html?pk=${movie.id}`;
            gradelink.textContent = movie.title;

            li.appendChild(gradelink);
            li.appendChild(document.createTextNode(`, Average Grade: ${movie.average_grade || 0}`));
            
            gradedList.appendChild(li);
        });

        // 좋아요 순
        const likedMovies = response.data.liked_movies;
        const likedList = document.getElementById('liked-movies-list');
        likedMovies.forEach(movie => {
            const li = document.createElement('li');

            const likelink = document.createElement('a');
            likelink.href = `http://127.0.0.1:5501/front/movies/details.html?pk=${movie.id}`;
            likelink.textContent = movie.title;

            li.appendChild(likelink);
            li.appendChild(document.createTextNode(`, likes: ${movie.like || 0}`));
            likedList.appendChild(li);
        });
    })
    .catch(error => {
        console.error('Error fetching movies:', error);
    });

// 검색 기능
const searchForm = document.getElementById('searchForm');

if (searchForm) {
    searchForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const searchKeyword = document.getElementById('search_keyword').value.trim();
        const searchType = document.getElementById('lang').value;

        // 검색어가 비어있을 경우 경고
        if (!searchKeyword) {
            alert('검색어를 입력하세요.');
            return;
        }

        // 페이지 이동
        const searchUrl = `search.html?search_keyword=${encodeURIComponent(searchKeyword)}&search_type=${searchType}`;
        window.location.href = searchUrl;
    });
}

// url주소에서 데이터 추출
const urlParams = new URLSearchParams(window.location.search);

// search.html에서 검색 결과 처리
const searchKeyword = urlParams.get('search_keyword');
const searchType = urlParams.get('search_type');

if (searchKeyword) {
    axios.get(`${API_BASE_URL}/movies/search/?search_type=${searchType}&search_keyword=${encodeURIComponent(searchKeyword)}`)
        .then(response => {
            const resultsList = document.getElementById('searchresults');
            resultsList.innerHTML = '';

            // 검색 결과를 출력
            response.data.forEach(item => {
                const li = document.createElement('li');

                if (searchType === 'movies') {
                    const genreNames = item.genre.map(genre => genre.name).join(', ');

                    const searchlink = document.createElement('a');
                    searchlink.href = `http://127.0.0.1:5501/front/movies/details.html?pk=${item.id}`;
                    searchlink.textContent = item.title;

                    li.appendChild(searchlink);
                    li.appendChild(document.createTextNode(`, 장르: ${genreNames}`));

                } else if (searchType === 'staff') {
                    li.textContent = `이름: ${item.name}`;
                } else if (searchType === 'member') {
                    li.textContent = `닉네임: ${item.nickname}`;
                }
                resultsList.appendChild(li);
            });
        })
        .catch(error => {
            console.error('검색 결과를 가져오는 중 오류 발생:', error);
        });
}

// 상세 페이지
const moviepk = urlParams.get('pk');
const token = localStorage.getItem('jwtAccessToken');

axios.get(`${API_BASE_URL}/movies/${moviepk}/`)
    .then(response => {
        const movie = response.data;

        document.getElementById('movie-title').textContent = movie.title;

        const genreNames = movie.genre.map(genre => genre.name).join(', ');
        document.getElementById('movie-genre').textContent = genreNames;
        document.getElementById('movie-plot').textContent = movie.plot;

        // 보고싶어요,관심없어요
        const likeButton = document.getElementById('like');
        const dislikeButton = document.getElementById('dislike');
        
        // '보고싶어요'와 '관심없어요' 버튼에 각각 반응 추가
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
        
            axios.post(`${API_BASE_URL}/movies/${moviepk}/score/`, scoreData, {
                headers: {
                    Authorization: `Bearer ${token}`  // JWT 토큰을 Authorization 헤더에 포함
                }
            })
            .then(response => {
                console.log('성공적으로 전송되었습니다:', response.data);
            })
            .catch(error => {
                console.error('전송 중 오류가 발생했습니다:', error);
            });
        });

        // 취소하기
        cancelButton.addEventListener('click', () => {
            const scoreData = {
                evaluate: 0
            };

            axios.post(`${API_BASE_URL}/movies/${moviepk}/score/`, scoreData, {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            })
            .then(response => {
                console.log('성공적으로 전송되었습니다:', response.data);
            })
            .catch(error => {
                console.error('전송 중 오류가 발생했습니다:', error);
            });
        });
    });

// 데이터 전송
function sendReaction(moviepk, movieData) {
    axios.post(`${API_BASE_URL}/movies/${moviepk}/`, movieData, {
        headers: {
            Authorization: `Bearer ${token}`
        }
    })
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
        sendReaction(moviepk, movieData);
    });
}
