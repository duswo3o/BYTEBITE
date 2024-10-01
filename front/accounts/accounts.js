// import axios from "axios";

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1'

const signupBtn = document.getElementById("signup-btn");
const signinBtn = document.getElementById("signin-btn");
// const profileBtn = document.getElementById("calluesrbtn");
const followBtn = document.getElementById("followUserBtn");


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

        // 토큰이 만료되었을 때 처리
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


// 회원가입
const signupUser = () => {
    // 선택필드에 빈 값이 들어가는 경우
    // 나이의 경우 숫자형으로 들어가야하는데 빈 값일때 빈문자열을 반환해서 null값으로 처리
    var age = document.getElementById('InputAge').value
    if (!age) {
        age = null
    }
    axios.post(`${API_BASE_URL}/accounts/`, {
        email: document.getElementById('InputEmail').value,
        password: document.getElementById('InputPassword').value,
        confirm_password: document.getElementById('confirmInputPassword').value,
        nickname: document.getElementById('InputNickname').value,
        gender: document.getElementById('inputGender').value,
        age: age,
        bio: document.getElementById('InputBio').value,
    })
        .then(response => {
            console.log(response);
            // 이동할 페이지
            window.location.href = "profile.html"
        })
        .catch(error => {
            console.log(error)
            // alert(email)
        })

}

// 로그인
const signinUser = () => {
    axios.post(`${API_BASE_URL}/accounts/signin/`, {
        email: document.getElementById("signinEmail").value,
        password: document.getElementById("signinPassword").value
    })
        .then(response => {
            // 로그인 성공 시 토큰 저장
            tokenManager.setTokens(response.data);
            console.log(response)
            // alert("로그인 성공")
            // 이동할 페이지
            window.location.href = "profile.html"
        })
        .catch(error => {
            console.log(error)
        })
}



// 로그아웃

const signoutBtn = document.getElementById("signoutBtn")

const signoutUser = () => {
    axios.post(`${API_BASE_URL}/accounts/signout/`, {
        refresh: localStorage.getItem("jwtRefreshToken")
    })
        .then(response => {
            console.log(response)
            alert("로그아웃 되었습니다")
        })
        .catch(error => {
            console.log(error)
            alert("로그아웃 실패")
        })
}


// 프로필 조회
const profileBtn = document.getElementById("searchUserBtn")

const userProfile = () => {
    var userPK = document.getElementById("userpk").value

    axios.get(`${API_BASE_URL}/accounts/${userPK}/`)
        .then(response => {
            console.log(response)

            // console.log(document)
            document.getElementById("nickname").innerText = response.data.nickname
            document.getElementById("email").innerText = response.data.email
            document.getElementById("gender").innerText = response.data.gender
            document.getElementById("age").innerText = response.data.age
            document.getElementById("bio").innerText = response.data.bio
            document.getElementById("followers").innerText = response.data.followers_count
            document.getElementById("followings").innerText = response.data.followings_count
            document.getElementById("wannawatch").innerText = response.data.liked_movies.length
            document.getElementById("likedreview").innerText = response.data.liked_reviews.length
            document.getElementById("ratedmovie").innerText = response.data.rated_movie.length
            document.getElementById("myreview").innerText = response.data.reviews.length
            // document.getElementById("testreview").innerText = response.data.reviews.length


            // 팔로워
            const followUsers = response.data.followers;
            const followUserList = document.getElementById("follower-users");
            followUsers.forEach(followUser => {
                const followUserdiv = document.createElement("div");
                followUserdiv.innerHTML = `
                    <div class="card">
                        <p>username : <span class="movieID">${followUser.nickname}</span></p>
                    </div>
                `;
                followUserList.appendChild(followUserdiv);
            });

            // 팔로워
            const followingUsers = response.data.followings;
            const followingUserList = document.getElementById("following-users");
            followingUsers.forEach(followingUser => {
                const followingUserdiv = document.createElement("div");
                followingUserdiv.innerHTML = `
                    <div class="card">
                        <p>username : <span class="movieID">${followingUser.nickname}</span></p>
                    </div>
                `;
                followingUserList.appendChild(followingUserdiv);
            });


            // 보고싶어요 영화
            const wishMovies = response.data.liked_movies;
            const wishMovieList = document.getElementById("wnat-to-watch");
            wishMovies.forEach(wishMovie => {
                const wishMoviediv = document.createElement("div");
                wishMoviediv.innerHTML = `
                    <div class="card">
                        <p>Movie Title : <span class="movieID">${wishMovie.title}</span></p>
                    </div>
                `;
                wishMovieList.appendChild(wishMoviediv);
            });

            // 좋아요 한 리뷰
            const likedReviews = response.data.liked_reviews;
            const likedReviewList = document.getElementById("liked-review");
            likedReviews.forEach(likedReview => {
                const likedReviewdiv = document.createElement("div");
                likedReviewdiv.innerHTML = `
                    <div class="card">
                        <p>Movie ID : <span class="movieID">${likedReview.review.movie}</span></p>
                        <p>Movie review : <span class="review">${likedReview.review.content}</span></p>
                    </div>
                `;
                likedReviewList.appendChild(likedReviewdiv);
            });

            // 작성한 리뷰
            const myReviews = response.data.reviews;
            const myReviewList = document.getElementById("my-movie-reviews");
            myReviews.forEach(myReview => {
                const reviewdiv = document.createElement("div");
                reviewdiv.innerHTML = `
                    <div class="card">
                        <p>MovieID : <span class="movieID">${myReview.movie}</span></p>
                        <p>review : <span class="myReview">${myReview.content}</span></p>
                    </div>
                `;
                myReviewList.appendChild(reviewdiv);
            });

            // 평가한 영화
            const myRatings = response.data.rated_movie;
            const myRatingList = document.getElementById("my-rated-movie");
            myRatings.forEach(myRating => {
                const ratingdiv = document.createElement("div");
                ratingdiv.innerHTML = `
                <div class="card">
                    <p>MovieID : <span class="movieID">${myRating.movie}</span></p>
                    <p>score : <span class="myReview">${myRating.score}</span></p>
                </div>
            `;
                myRatingList.appendChild(ratingdiv);
            });


        })
        .catch(error => {
            console.log(error)
            alert("없는 회원입니다")
        })

}

// document.addEventListener("DOMContentLoaded", () => {
//     userProfile(); // 페이지가 로드되면 userProfile 함수 호출
// });


const followUser = (event) => {
    event.preventDefault();  // 기본 동작 방지 (페이지 새로고침 방지)
    var userPK = document.getElementById("userpk").value

    axios.post(`${API_BASE_URL}/accounts/${userPK}/follow/`, {
    })
        .then(response => {
            console.log(response)
            alert(response.data.message)
        })
        .catch(error => {
            console.log(error)
            alert(error.response.data.message)
        })

    return false; // 기본 동작 방지
}



// 버튼 확인
if (signupBtn) {
    signupBtn.addEventListener('click', signupUser)
}

if (signinBtn) {
    signinBtn.addEventListener('click', signinUser)
}

if (signoutBtn) {
    signoutBtn.addEventListener('click', signoutUser)
}

if (profileBtn) {
    profileBtn.addEventListener('click', userProfile)
}

if (followBtn) {
    followBtn.addEventListener('click', followUser)
}