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

    // 테이블 생성
    const table = document.createElement('table');
    table.style.width = '100%'; // 테이블 너비 설정
    table.border = '1'; // 테두리 설정
    table.style.textAlign = 'center'; // 테이블 내 모든 셀의 텍스트를 가운데 정렬

    // 테이블 헤더 생성
    const headerRow = document.createElement('tr');
    const headers = ['확인', '이미지', '상품명', '수량', '가격'];
    headers.forEach(headerText => {
        const th = document.createElement('th');
        th.textContent = headerText;
        th.style.textAlign = 'center'; // 헤더 셀의 텍스트를 가운데 정렬
        headerRow.appendChild(th);
    });
    table.appendChild(headerRow);

    // products 속성이 존재하고 배열인지 확인
    if (Array.isArray(basketData.products) && basketData.products.length > 0) {
        let totalAmount = 0; // 총 금액 변수

        basketData.products.forEach(product => {
            const row = document.createElement('tr');

            // 체크박스 생성
            const checkBoxCell = document.createElement('td');
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.value = JSON.stringify(product); // 체크박스 값으로 상품 정보를 저장
            checkBoxCell.appendChild(checkbox);
            row.appendChild(checkBoxCell);

            // 이미지 생성
            const imageCell = document.createElement('td');
            const productImage = document.createElement('img');
            productImage.src = product.image;
            productImage.alt = product.name;
            productImage.style.width = '50px';
            imageCell.appendChild(productImage);
            row.appendChild(imageCell);

            // 상품명 생성
            const productNameCell = document.createElement('td');
            productNameCell.textContent = product.name;
            row.appendChild(productNameCell);

            // 수량 선택 박스 생성
            const quantityCell = document.createElement('td');
            const quantitySelect = document.createElement('select');
            for (let i = 1; i <= 10; i++) {
                const option = document.createElement('option');
                option.value = i;
                option.textContent = i;
                quantitySelect.appendChild(option);
            }
            quantityCell.appendChild(quantitySelect);
            row.appendChild(quantityCell);

            // 가격 생성
            const priceCell = document.createElement('td');
            const totalPrice = product.price * (parseInt(quantitySelect.value) || 1);
            priceCell.textContent = `${totalPrice}원`;
            row.appendChild(priceCell);

            // 체크박스와 수량 선택 박스의 change 이벤트 리스너
            checkbox.addEventListener('change', () => {
                updateTotalAmount();
                togglePaymentForm();
            });
            quantitySelect.addEventListener('change', () => {
                const updatedPrice = product.price * parseInt(quantitySelect.value);
                priceCell.textContent = `${updatedPrice}원`;
                updateTotalAmount();
            });

            // 행을 테이블에 추가
            table.appendChild(row);
        });

        // 총 금액 표시
        const totalAmountCell = document.createElement('tr');
        totalAmountCell.innerHTML = `<td colspan="4" style="text-align: right;">총 금액:</td><td id="total-amount">0원</td>`;
        table.appendChild(totalAmountCell);

        // 체크박스 상태에 따라 결제 폼 표시 또는 숨기기
        const togglePaymentForm = () => {
            const selectedCheckboxes = document.querySelectorAll('input[type="checkbox"]:checked');
            if (selectedCheckboxes.length > 0) {
                showPaymentForm(selectedCheckboxes);
            } else {
                hidePaymentForm(); // 모든 체크박스가 해제된 경우 폼 숨기기
            }
        };

    } else {
        const noProductsMessage = document.createElement('p');
        noProductsMessage.textContent = '장바구니에 상품이 없습니다.';
        basketContainer.appendChild(noProductsMessage);
    }

    // 테이블을 컨테이너에 추가
    basketContainer.appendChild(table);

    // 초기 총 금액 계산
    updateTotalAmount();
}

// 총 금액 업데이트 함수
function updateTotalAmount() {
    const checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
    let total = 0;

    checkboxes.forEach(checkbox => {
        const product = JSON.parse(checkbox.value);
        const quantity = checkbox.closest('tr').querySelector('select').value;
        total += product.price * parseInt(quantity);
    });

    document.getElementById('total-amount').textContent = `${total}원`;
}

// 주소 검색 호출 함수
function openPostcode() {
    new daum.Postcode({
        oncomplete: function(data) {
            // 선택된 주소 정보를 주소 입력란에 채우기
            const address = data.address; // 기본 주소
            let extraAddress = ''; // 상세 주소 (필요한 경우 추가)

            // 주소 구성
            if (data.bname !== '') {
                extraAddress += data.bname; // 건물명 추가
            }
            if (data.buildingName !== '') {
                extraAddress += (extraAddress !== '' ? ', ' + data.buildingName : data.buildingName); // 상세 주소 추가
            }
            if (extraAddress !== '') {
                extraAddress = ' (' + extraAddress + ')';
            }

            // 최종 주소
            const fullAddress = address + extraAddress;

            // 주소 입력란에 채우기
            document.getElementById('address').value = fullAddress;
        }
    }).open();
}

// 로그인 중인 사용자 정보 로드
function loadUserInfo() {
    return axios.get(`${API_BASE_URL}products/login_user/`)
        .then(response => {
            const user = response.data;
            return { user_id: user.id, email: user.email };
        })
        .catch(error => {
            console.error('사용자 정보를 불러오는 중 오류 발생:', error);
            alert('사용자 정보를 불러오는 중 오류가 발생했습니다.');
            throw error;
        });
}

// 결제 정보 입력 필드 표시 함수
function showPaymentForm(selectedCheckboxes) {
    // 기존에 생성된 필드 제거
    const existingForm = document.getElementById('payment-form');
    if (existingForm) {
        existingForm.remove(); 
    }

    // 결제 정보 입력 필드 생성
    const paymentFormContainer = document.createElement('div');
    paymentFormContainer.id = 'payment-form'; // 고유 ID 추가

    // 구매자 이름 입력 필드
    const nameInput = document.createElement('input');
    nameInput.placeholder = '구매자 이름';
    nameInput.classList.add('input-address');
    paymentFormContainer.appendChild(nameInput);

    // 줄 바꿈 추가
    paymentFormContainer.appendChild(document.createElement('br'));

    // 주소 입력 필드
    const addressInput = document.createElement('input');
    addressInput.id = 'address';
    addressInput.placeholder = '주소';
    addressInput.required = true;
    addressInput.readOnly = true;
    addressInput.onclick = openPostcode; // 주소 입력 클릭 시 주소 찾기 함수 호출
    addressInput.classList.add('input-address');
    paymentFormContainer.appendChild(addressInput);

    // 줄 바꿈 추가
    paymentFormContainer.appendChild(document.createElement('br'));

    // 상세주소 입력 필드
    const address2Input = document.createElement('input');
    address2Input.placeholder = '상세주소';
    address2Input.classList.add('input-address');
    paymentFormContainer.appendChild(address2Input);

    // 줄 바꿈 추가
    paymentFormContainer.appendChild(document.createElement('br'));

    // 결제 진행 버튼
    const submitButton = document.createElement('button');
    submitButton.textContent = '결제 진행';
    submitButton.type = 'button'; // 기본 동작 방지

    // 버튼 클릭 시 결제 요청
    submitButton.onclick = () => {
        loadUserInfo()
            .then(({ user_id, email }) => {
                // 사용자 정보 로드가 완료된 후 결제 요청
                requestPay(selectedCheckboxes, nameInput.value, addressInput.value, address2Input.value, user_id, email);
            })
            .catch(error => {
                // 오류 처리
                console.error('결제 진행 중 오류 발생:', error);
            });
    };

    // 결제 버튼을 컨테이너에 추가
    paymentFormContainer.appendChild(submitButton);

    // 장바구니 컨테이너에 결제 필드 추가
    document.getElementById('basket-container').appendChild(paymentFormContainer);
}

// 결제 정보 입력 폼 숨기는 함수
function hidePaymentForm() {
    const existingForm = document.getElementById('payment-form');
    if (existingForm) {
        existingForm.remove(); // 결제 폼이 있으면 제거
    }
}

var IMP = window.IMP;
IMP.init("imp43760436");

// 결제 요청 함수
function requestPay(selectedCheckboxes, name, address, address2, user_id, email) {
    const selectedProducts = [];
    const productQuantities = {};

    // 선택된 상품 정보를 수집
    selectedCheckboxes.forEach(checkbox => {
        const product = JSON.parse(checkbox.value);
        const quantity = parseInt(checkbox.closest('tr').querySelector('select').value);

        // 상품 정보 저장
        selectedProducts.push({ ...product, quantity });

        // 상품명별 수량 업데이트
        if (productQuantities[product.name]) {
            productQuantities[product.name] += quantity; // 기존 수량 추가
        } else {
            productQuantities[product.name] = quantity; // 새로운 상품 추가
        }
    });

    // 상품명 설정
    let productName;
    const productNames = Object.keys(productQuantities); // 상품명 목록

    if (productNames.length === 1 && productQuantities[productNames[0]] === 1) {
        productName = productNames[0]; // 상품이 하나이고 수량이 1일 경우
    } else {
        const primaryProduct = productNames[0]; // 대표 상품명
        const totalQuantity = Object.values(productQuantities).reduce((acc, qty) => acc + qty, 0); // 총 수량

        productName = `${primaryProduct} 외 ${totalQuantity - 1}개`; // 대표 상품명과 총 수량
    }

    // 현재 날짜 포맷팅 (YYYYMMDD)
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    const dateString = `${year}${month}${day}`;

    const min = 100000; // 6자리 수의 최소값
    const max = 999999; // 6자리 수의 최대값
    const randomNumber = Math.floor(Math.random() * (max - min + 1)) + min;

    // merchant_uid 설정
    const merchant_uid = `${user_id}-${dateString}-${randomNumber}`;
    const totalAmount = parseInt(document.getElementById('total-amount').textContent.replace('원', ''));

    // 결제 요청 로직
    IMP.request_pay(
        {
            pg: "kakaopay.TC0ONETIME",
            pay_method: "card",
            merchant_uid: merchant_uid, // 동적으로 설정된 merchant_uid 사용
            name: productName, // 상품명
            amount: totalAmount, // 가격
            buyer_name: name,
            buyer_addr: address,
            buyer_addr2: address2,
            buyer_postcode: "123-456", // 필요한 경우 여기에 우편번호를 추가하세요.
        },
        rsp => {
            if (rsp.success) {
                // 여러 상품 정보 서버로 전송
                const productsData = selectedProducts.map(product => ({
                    product_id: product.id,     // 상품 ID
                    product_name: product.name, // 상품명
                    quantity: product.quantity  // 수량
                }));
    
                axios({
                    url: `${API_BASE_URL}products/payments/`,
                    method: "post",
                    headers: { "Content-Type": "application/json" },
                    data: {
                        imp_uid: rsp.imp_uid,
                        merchant_uid: rsp.merchant_uid,
                        name: name,           // 구매자 이름
                        address: address,     // 구매자 주소
                        address2: address2,   // 구매자 추가 주소
                        products: productsData, // 여러 상품 정보
                        total_amount: totalAmount // 총 금액
                    }
                })
                .then(function (response) {
                    console.log("서버 응답:", response);
                    alert("결제가 성공적으로 완료되었습니다!"); // 성공 메시지 추가
                })
                .catch(function (error) {
                    console.error("결제 검증 실패:", error);
                    alert("서버에서 결제 검증에 실패했습니다. 관리자에게 문의하세요.");
                });
            } else {
                console.error("결제 실패:", rsp);
                alert(`결제에 실패하였습니다. 에러 내용: ${rsp.error_msg}`); // 실패 메시지 추가
            }
        }
    );
}

// 뒤로가기 함수 정의
function goBack() {
    window.history.back(); // 이전 페이지로 돌아감
}

// 함수 호출
document.addEventListener('DOMContentLoaded', fetchBasket);


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