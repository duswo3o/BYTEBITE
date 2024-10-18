const API_BASE_URL = 'http://127.0.0.1:8000/api/v1/';

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

// 장바구니 데이터를 가져오는 함수
async function fetchBasket() {
    try {
        const response = await axios.get(`${API_BASE_URL}accounts/basket/`);
        const basketData = response.data;
        displayBasket(basketData); // 가져온 데이터를 화면에 출력하는 함수 호출
    } catch (error) {
        console.error('장바구니 데이터를 가져오는 데 실패했습니다:', error);
    }
}

// 장바구니 데이터를 화면에 표시하는 함수
function displayBasket(basketData) {
    const basketContainer = document.getElementById('basket-container');
    basketContainer.innerHTML = ''; // 기존 내용을 초기화

    // products 속성이 존재하고 배열인지 확인
    if (Array.isArray(basketData.products) && basketData.products.length > 0) {
        basketData.products.forEach(product => {
            const productItem = document.createElement('div');
            productItem.classList.add('product-item');

            // 이미지 생성
            const productImage = document.createElement('img');
            productImage.src = product.image || '기본이미지경로.jpg'; // 기본 이미지 경로
            productImage.alt = product.name;
            productItem.appendChild(productImage);

            // 정보 컨테이너 생성
            const productInfo = document.createElement('div');
            productInfo.classList.add('product-info');

            const productName = document.createElement('h3');
            productName.textContent = product.name;
            productInfo.appendChild(productName);

            const productPrice = document.createElement('p');
            productPrice.textContent = `가격: ${product.price}원`;
            productInfo.appendChild(productPrice);

            productItem.appendChild(productInfo);
            basketContainer.appendChild(productItem);
        });
    } else {
        const noProductsMessage = document.createElement('p');
        noProductsMessage.textContent = '장바구니에 상품이 없습니다.';
        basketContainer.appendChild(noProductsMessage);
    }
}

// 뒤로가기 함수 정의
function goBack() {
    window.history.back(); // 이전 페이지로 돌아감
}

// 예시: 함수 호출 (필요 시 호출하는 곳에서 처리)
document.addEventListener('DOMContentLoaded', fetchBasket);