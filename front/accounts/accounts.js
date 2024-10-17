// import axios from "axios";

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1'

const signupBtn = document.getElementById("signup-btn");
const signinBtn = document.getElementById("signin-btn");
// const profileBtn = document.getElementById("calluesrbtn");
const followBtn = document.getElementById("followUserBtn");


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
            const response = await axios.post(`${API_BASE_URL}/accounts/token/refresh/`, {
                refresh: refreshToken
            });
            this.setTokens(response.data); // 새로운 토큰 저장
            console.log('토큰이 갱신되었습니다:', response.data.access);
        } catch (error) {
            console.error('토큰 갱신 실패:', error.response ? error.response.data : error.message);
            this.clearTokens(); // 실패 시 토큰 제거
            localStorage.clear()
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


// Axios 응답 인터셉터 설정
axios.interceptors.response.use(
    (response) => {
        // 정상 응답은 그대로 반환
        return response;
    },
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
                console.log("세션 스토리지를 삭제합니다.")
                sessionStorage.clear()
                localStorage.clear()

                alert("토큰이 만료되었습니다. 다시 로그인해주세요.")
                window.location.href = "signin.html"

                return Promise.reject(error);
            }
        }

        // 기타 오류는 그대로 반환
        return Promise.reject(error);
    }
);

// 버튼 보여주기 설정
document.addEventListener('DOMContentLoaded', function () {
    const accessToken = sessionStorage.getItem('jwtAccessToken');
    // 로컬스토리지에 토큰이 있는 경우
    if (accessToken) {
        // 로그아웃 버튼만 보여주기
        document.getElementById('signinBtn').style.display = 'none';
        document.getElementById('signupBtn').style.display = 'none';
        document.getElementById('signoutBtn').style.display = 'block';
    }
    // 로컬스토리지에 토큰이 없는 경우 
    else {
        document.getElementById('signinBtn').style.display = 'block';
        document.getElementById('signupBtn').style.display = 'block';
        document.getElementById('signoutBtn').style.display = 'none';
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const helloUser = document.getElementById("helloUser");
    const nickname = localStorage.getItem("nickname")
    if (nickname) {
        var userMessage = "hello, " + localStorage.getItem("nickname")
    } else {
        var userMessage = "welcome!"
    }
    helloUser.innerHTML = `
<span>${userMessage}</span>
`;
});

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
            alert("이메일을 확인하여 인증을 진행해주세요")
            // 이동할 페이지
            window.location.href = "signin.html"
        })
        .catch(error => {
            console.log(error)
            alert(error.response.data.message || "회원가입에 실패하였습니다")
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
            // sessionStorage.setItem('jwtAccessToken', access);
            // sessionStorage.setItem('jwtRefreshToken', refresh);

            // 회원정보 스토리지에 저장
            localStorage.setItem('id', response.data.id)
            localStorage.setItem('email', response.data.email)
            localStorage.setItem('nickname', response.data.nickname)
            localStorage.setItem('gender', response.data.gender)
            localStorage.setItem('age', response.data.age)
            localStorage.setItem('bio', response.data.bio)

            console.log(response)
            // alert("로그인 성공")
            // 이동할 페이지
            window.location.href = "profile.html"
        })
        .catch(error => {
            console.log(error)
            if (error.response.data.non_field_errors) {
                alert(error.response.data.non_field_errors)
            } else if (error.response.data.email) {
                alert(error.response.data.email)
            }
        })
}


// 로그아웃

const signoutBtn = document.getElementById("signoutBtn")

const signoutUser = (event) => {
    event.preventDefault()
    const refreshToken = tokenManager.getRefreshToken();

    axios.post(`${API_BASE_URL}/accounts/signout/`, {
        refresh: refreshToken
    })
        .then(response => {
            sessionStorage.clear()
            localStorage.clear()
            console.log(response)
            alert("로그아웃 되었습니다")
        })
        .catch(error => {
            console.log(error)
            sessionStorage.clear()
            localStorage.clear()
            // alert("로그아웃 실패")
        })
}


// 프로필 조회
const profileBtn = document.getElementById("searchUserBtn")

const userProfile = () => {

    var userNickname = document.getElementById("userNickname").value.trim() || localStorage.getItem("nickname");

    axios.get(`${API_BASE_URL}/accounts/${userNickname}/`)
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
            followUserList.innerHTML = ""
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
            followingUserList.innerHTML = ""
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
            wishMovieList.innerHTML = ""
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
            likedReviewList.innerHTML = ""
            likedReviews.forEach(likedReview => {
                const likedReviewdiv = document.createElement("div");
                likedReviewdiv.innerHTML = `
                    <div class="card">
                        <p>Movie title : <span class="movieID">${likedReview.review.movie}</span></p>
                        <p>Movie review : <span class="review">${likedReview.review.content}</span></p>
                    </div>
                `;
                likedReviewList.appendChild(likedReviewdiv);
            });

            // 작성한 리뷰
            const myReviews = response.data.reviews;
            const myReviewList = document.getElementById("my-movie-reviews");
            myReviewList.innerHTML = ""
            myReviews.forEach(myReview => {
                const reviewdiv = document.createElement("div");
                reviewdiv.innerHTML = `
                    <div class="card">
                        <p>Movie title : <span class="movieID">${myReview.movie}</span></p>
                        <p>review : <span class="myReview">${myReview.content}</span></p>
                    </div>
                `;
                myReviewList.appendChild(reviewdiv);
            });

            // 평가한 영화
            const myRatings = response.data.rated_movie;
            const myRatingList = document.getElementById("my-rated-movie");
            myRatingList.innerHTML = ""
            myRatings.forEach(myRating => {
                const ratingdiv = document.createElement("div");
                ratingdiv.innerHTML = `
                <div class="card">
                    <p>Movie title : <span class="movieID">${myRating.movie}</span></p>
                    <p>score : <span class="myReview">${myRating.score}</span></p>
                </div>
            `;
                myRatingList.appendChild(ratingdiv);
            });

            // 로컬 스토리지 또는 서버에서 로그인한 사용자의 정보를 가져옴
            const loggedInUser = localStorage.getItem('nickname'); // 예: 로그인한 사용자 닉네임
            const viewedProfileUser = response.data.nickname; // 예: 조회한 프로필 닉네임 (이 값을 서버에서 받아온다고 가정)

            // 버튼 요소 가져오기
            const profileBtn = document.getElementById('profile-btn');

            // 로그인한 사용자와 조회한 프로필 사용자가 같을 때만 버튼을 표시
            if (loggedInUser === viewedProfileUser) {
                profileBtn.style.display = 'block'; // 버튼 보이게 설정
            } else {
                profileBtn.style.display = 'none'; // 버튼 숨기기
            }


        })
        .catch(error => {
            console.log(error)
            alert("없는 회원입니다")
        })

}

// document.addEventListener("DOMContentLoaded", () => {
//     userProfile(); // 페이지가 로드되면 userProfile 함수 호출
// });

// 팔로우
const followUser = (event) => {
    event.preventDefault();  // 기본 동작 방지 (페이지 새로고침 방지)
    var userNickname = document.getElementById("userNickname").value

    axios.post(`${API_BASE_URL}/accounts/${userNickname}/follow/`, {})
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


// 프로필 수정
const updateProfileBtn = document.getElementById("update-profile-btn")

const updateNickname = document.getElementById("updateNickname")
if (updateNickname) {
    updateNickname.value = localStorage.getItem('nickname')
}
;
const updateGender = document.getElementById("updateGender")
if (updateGender) {
    updateGender.value = localStorage.getItem('gender')
}
;
const updateAge = document.getElementById("updateAge")
if (updateAge) {
    updateAge.value = localStorage.getItem('age')
}
;
const updateBio = document.getElementById("updateBio")
if (updateBio) {
    updateBio.value = localStorage.getItem('bio')
}
;


const updateProfile = () => {
    // 선택필드에 빈 값이 들어가는 경우
    // 나이의 경우 숫자형으로 들어가야하는데 빈 값일때 빈문자열을 반환해서 null값으로 처리
    var age = document.getElementById('updateAge').value
    if (!age) {
        age = null
    }


    axios.put(`${API_BASE_URL}/accounts/`, {
        nickname: document.getElementById('updateNickname').value,
        gender: document.getElementById('updateGender').value,
        age: age,
        bio: document.getElementById('updateBio').value,
    })
        .then(response => {
            console.log(response)

            localStorage.setItem('nickname', response.data.nickname)
            localStorage.setItem('gender', response.data.gender)
            localStorage.setItem('age', age)
            localStorage.setItem('bio', response.data.bio)

            window.location.href = "profile.html"

        })
        .catch(error => {
            console.log(error)
            alert("수정 실패")
        })
}


// 패스워드 변경
const changePasswordBtn = document.getElementById('change-password-btn') // 패스워드 변경 버튼

const changePassword = () => {
    // const oldPassword = document.getElementById("oldPassword")
    // const newPassword = document.getElementById("newPassword")
    // const confirmPassword = document.getElementById("confirmPassword")

    axios.put(`${API_BASE_URL}/accounts/password/`, {
        old_password: document.getElementById("oldPassword").value,
        new_password: document.getElementById("newPassword").value,
        confirm_password: document.getElementById("confirmPassword").value
    })
        .then(response => {
            console.log(response)
            // alert("패스워드 변경 완료")

            // 이동할 페이지
            window.location.href = 'profile.html'
        })
        .catch(error => {
            console.log(error)
            alert("비밀번호 변경에 실패하였습니다")
        })

}


// 회원탈퇴
const withdrawBtn = document.getElementById('withdrawUser')
const withdrawUser = () => {
    const password = document.getElementById("withdrawPassword").value
    axios.delete(`${API_BASE_URL}/accounts/`, {
        data: { password: password }
    })
        .then(response => {
            console.log(response)
            sessionStorage.clear()
            localStorage.clear()
            window.location.href = 'profile.html'
        })
        .catch(error => {
            if (error.response) {
                console.error("Response error:", error);
                alert("탈퇴에 실패하였습니다: " + error.response.data.password);
            } else {
                console.error("Error:", error.message);
                alert("탈퇴 요청 중 오류가 발생했습니다.");
            }
        })
}


// 페이지가 완전히 로드된 후에 실행되는 함수
document.addEventListener('DOMContentLoaded', () => {
    // 카카오 로그인 버튼 이벤트 리스너 설정
    const kakaoLoginButton = document.getElementById('kakao-login-btn');
    if (kakaoLoginButton) {
        kakaoLoginButton.onclick = function () {
            window.location.href = 'http://127.0.0.1:8000/api/v1/accounts/social/login/kakao/';
        };
    }

    // 네이버 로그인 버튼 이벤트 리스너 설정
    const naverLoginButton = document.getElementById('naver-login-btn');
    if (naverLoginButton) {
        naverLoginButton.onclick = function () {
            window.location.href = 'http://127.0.0.1:8000/api/v1/accounts/social/login/naver/';
        };
    }

    // 구글 로그인 버튼 이벤트 리스너 설정
    const googleLoginButton = document.getElementById('google-login-btn');
    if (googleLoginButton) {
        googleLoginButton.onclick = function () {
            window.location.href = 'http://127.0.0.1:8000/api/v1/accounts/social/login/google/';
        };
    }

    // URL 파라미터 확인
    const urlParams = new URLSearchParams(window.location.search);
    const accessToken = urlParams.get('access_token');
    const refreshToken = urlParams.get('refresh_token');
    const nickname = urlParams.get('nickname');
    const email = urlParams.get('email');

    // 토큰과 사용자 정보가 있을 경우 처리
    if (accessToken && refreshToken && nickname && email) {
        handleTokens(accessToken, refreshToken, nickname, email);
    }
});


// 토큰 처리 함수
const handleTokens = (accessToken, refreshToken, nickname, email) => {
    // 세션 스토리지에 토큰 저장
    sessionStorage.setItem('jwtAccessToken', accessToken);
    sessionStorage.setItem('jwtRefreshToken', refreshToken);
    console.log("Tokens saved to sessionStorage");

    // 로컬 스토리지에 사용자 정보 저장
    localStorage.setItem('nickname', nickname);
    localStorage.setItem('email', email);
    console.log("User information saved to localStorage");

    // 프로필 페이지로 리다이렉트
    window.location.href = "profile.html";
};


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
    profileBtn.addEventListener('click', userProfile);

    // 닉네임이 localStorage에 있을 때만 페이지 로드 시 userProfile 실행
    if (localStorage.getItem("nickname")) {
        window.addEventListener('DOMContentLoaded', userProfile);
    }
}

if (followBtn) {
    followBtn.addEventListener('click', followUser)
}

if (updateProfileBtn) {
    updateProfileBtn.addEventListener('click', updateProfile)
}

if (changePasswordBtn) {
    changePasswordBtn.addEventListener('click', changePassword)
}

if (withdrawBtn) {
    withdrawBtn.addEventListener('click', withdrawUser)
}
