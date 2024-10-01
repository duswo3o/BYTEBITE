// 메인페이지 영화 정보 가져오기
axios.get('http://127.0.0.1:8000/api/v1/movies/')
    .then(response => {
        const boxofficeMovies = response.data.boxoffice_movies;
        const boxofficeList = document.getElementById('boxoffice-movies-list');
        boxofficeMovies.forEach(movie => {
            const li = document.createElement('li');
            li.textContent = `Title: ${movie.title}, Rank: ${movie.rank}`;
            boxofficeList.appendChild(li);
        });

        const gradedMovies = response.data.graded_movies;
        const gradedList = document.getElementById('graded-movies-list');
        gradedMovies.forEach(movie => {
            const li = document.createElement('li');
            li.textContent = `Title: ${movie.title}, Average Grade: ${movie.average_grade || 0}`;
            gradedList.appendChild(li);
        });

        const likedMovies = response.data.liked_movies;
        const likedList = document.getElementById('liked-movies-list');
        likedMovies.forEach(movie => {
            const li = document.createElement('li');
            li.textContent = `Title: ${movie.title}, Likes: ${movie.like}`;
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
    axios.get(`http://127.0.0.1:8000/api/v1/movies/search/?search_type=${searchType}&search_keyword=${encodeURIComponent(searchKeyword)}`)
        .then(response => {
            const resultsList = document.getElementById('searchresults');
            resultsList.innerHTML = '';

            // 검색 결과를 출력
            response.data.forEach(item => {
                const li = document.createElement('li');

                if (searchType === 'movies') {
                    const genreNames = item.genre.map(genre => genre.name).join(', ');

                    const link = document.createElement('a');
                    link.href = `http://127.0.0.1:5501/front/movies/details.html?pk=${item.id}`;
                    link.textContent = item.title;

                    li.appendChild(link);

                    li.appendChild(document.createTextNode(`, 장르: ${genreNames}`));
                    
                    console.log(link.href);
                    console.log(link);

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
const pk = urlParams.get('pk');

axios.get(`http://127.0.0.1:8000/api/v1/movies/${pk}/`)
    .then(response => {
        const movie = response.data;

        document.getElementById('movie-title').textContent = movie.title;

        const genreNames = movie.genre.map(genre => genre.name).join(', ');
        document.getElementById('movie-genre').textContent = genreNames;
        document.getElementById('movie-plot').textContent = movie.plot;
    })
    .catch(error => {
        console.error('영화 정보를 가져오는 중 오류 발생:', error);
    });
