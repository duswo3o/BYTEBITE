const API_BASE_URL = 'http://127.0.0.1:8000/api/v1/'

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

var IMP = window.IMP;
IMP.init("imp43760436");

// 로그인 중인 사용자 정보 로드
function loadUserInfo() {
  axios.get(`${API_BASE_URL}products/login_user/`)
      .then(response => {
          const user = response.data;
          const email = user.email;

          document.getElementById('user-email').textContent = email;
      })
      .catch(error => {
          console.error('사용자 정보를 불러오는 중 오류 발생:', error);
          alert('사용자 정보를 불러오는 중 오류가 발생했습니다.');
      });
}

// 상품 정보 로드
function loadProductInfo() {
  const urlParams = new URLSearchParams(window.location.search);
  const productId = urlParams.get('productId');

  axios.get(`${API_BASE_URL}products/${productId}/`)
      .then(response => {
          const product = response.data;
          const productName = product.title;
          const productPrice = product.price;

          // 상품명과 가격을 HTML에 설정
          document.getElementById('product-name').textContent = productName; // 상품명 설정
          document.getElementById('product-price').textContent = productPrice; // 가격 설정
      })
      .catch(error => {
          console.error('상품 정보를 불러오는 중 오류 발생:', error);
          alert('상품 정보를 불러오는 중 오류가 발생했습니다.');
      });
}

// 결제 요청 함수
function requestPay() {
  const name = document.getElementById('name').value;
  const address = document.getElementById('address').value;
  const address2 = document.getElementById('address2').value;

  // URL 파라미터에서 상품 ID 가져오기
  const urlParams = new URLSearchParams(window.location.search);
  const productId = urlParams.get('productId');

  // purchaseNumber 설정
  let purchaseNumber = localStorage.getItem('purchaseNumber');
  if (!purchaseNumber) {
      purchaseNumber = 1; // 초기값 설정
  } else {
      purchaseNumber = parseInt(purchaseNumber) + 1; // 1씩 증가
  }
  localStorage.setItem('purchaseNumber', purchaseNumber); 

  // 현재 날짜 포맷팅 (YYYYMMDD)
  const today = new Date();
  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, '0'); // 월은 0부터 시작하므로 +1
  const day = String(today.getDate()).padStart(2, '0');
  const dateString = `${year}${month}${day}`;

  // merchant_uid 설정
  const merchant_uid = `${productId}-${dateString}-${purchaseNumber}`;

  // 결제 요청
  IMP.request_pay(
      {
          pg: "kakaopay.TC0ONETIME",
          pay_method: "card",
          merchant_uid: merchant_uid, // 동적으로 설정된 merchant_uid 사용
          name: document.getElementById('product-name').textContent, // 상품명
          amount: document.getElementById('product-price').textContent, // 가격
          buyer_name: name,
          buyer_addr: address,
          buyer_addr2: address2,
          buyer_postcode: "123-456", // 필요한 경우 여기에 우편번호를 추가하세요.
      },
      rsp => {
          if (rsp.success) {
              axios({
                  url: `${API_BASE_URL}products/payments/`,
                  method: "post",
                  headers: { "Content-Type": "application/json" },
                  data: {
                      imp_uid: rsp.imp_uid,
                      merchant_uid: rsp.merchant_uid,
                      name: name,
                      address: address,
                      address2: address2 // address2를 올바르게 전송
                  }
              })
              .then(function (response) {
                  alert("결제가 성공적으로 완료되었습니다!");
              })
              .catch(function (error) {
                  alert("서버에서 결제 검증에 실패했습니다.");
              });
          } else {
              alert(`결제에 실패하였습니다. 에러 내용: ${rsp.error_msg}`);
          }
      }
  );
}

window.onload = function() {
  loadProductInfo();
  loadUserInfo();
};