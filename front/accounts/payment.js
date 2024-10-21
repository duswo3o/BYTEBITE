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

// 객체 초기화
var IMP = window.IMP;
IMP.init("imp43760436");

function requestPay() {
    const name = document.getElementById('name').value;
    const address = document.getElementById('address').value;
    const tel = document.getElementById('tel').value;
  
    IMP.request_pay(
      {
        pg: "kakaopay.TC0ONETIME",
        pay_method: "card",
        merchant_uid: "57008833-33018",
        name: "포트원 테스트",
        amount: 10,
        buyer_name: name,
        buyer_tel: tel,
        buyer_addr: address,
        buyer_postcode: "123-456", // 필요한 경우 여기에 우편번호를 추가하세요.
      },
      rsp => {
        if (rsp.success) {
          axios({
            url: `${API_BASE_URL}accounts/payments/`,
            method: "post",
            headers: { "Content-Type": "application/json" },
            data: {
              imp_uid: rsp.imp_uid,
              merchant_uid: rsp.merchant_uid,
              name: name,
              address: address,
              tel: tel
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
  