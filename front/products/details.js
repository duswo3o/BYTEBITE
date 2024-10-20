const API_BASE_URL = 'https://api.popcorngeek.store/api/v1/';

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
            config.headers.Authorization = `Bearer ${token}`;
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

function getProductIdFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('id'); // 'id' 매개변수로 상품 ID를 가져옴
}

function addToCart(productId) {
    axios.post(`${API_BASE_URL}products/${productId}/`)
        .then(response => {
            alert(response.data.detail); // 서버로부터의 응답 메시지 표시
        })
        .catch(error => {
            console.error('장바구니 요청 중 오류 발생:', error);
            alert('장바구니 요청 중 오류가 발생했습니다.');
        });
}

function loadProductDetail() {
    const productId = getProductIdFromURL();
    const productDetail = document.getElementById('product-detail');

    if (!productId) {
        productDetail.innerHTML = '<p>상품 ID가 제공되지 않았습니다.</p>';
        return;
    }

    axios.get(`${API_BASE_URL}products/${productId}/`)
        .then(response => {
            const product = response.data;

            // 상품 상세 정보를 HTML로 출력
            productDetail.innerHTML = `
                <div class="product-item">
                    <img src="${product.image}" alt="${product.name}" width="300">
                    <h2>${product.name}</h2>
                    <p>${product.content}</p>
                    <p>가격: ${product.price}원</p>
                    <button onclick="addToCart('${product.id}')">장바구니에 추가</button>
                </div>
            `;
        })
        .catch(error => {
            console.error('상품 정보를 불러오는 중 오류 발생:', error);
            productDetail.innerHTML = '<p>상품 정보를 불러오는 중 오류가 발생했습니다.</p>';
        });
}


// 결제 페이지로 이동하는 함수
function goToPayment(productId) {

    const paymentURL = `payment.html?productId=${productId}`;
    window.location.href = paymentURL; // 결제 페이지로 이동
}

// 페이지가 로드될 때 상품 상세 정보를 가져옴
document.addEventListener('DOMContentLoaded', loadProductDetail);

// 뒤로가기 버튼 클릭 시 이전 페이지로 이동
function goBack() {
    window.history.back();
}

// 세션에서 구매자 이메일을 가져오는 함수
function getBuyerEmailFromSession() {
    return 'buyer@example.com'; // 테스트용 이메일
}

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
