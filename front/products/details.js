const API_BASE_URL = 'http://127.0.0.1:8000/api/v1/';

function getProductIdFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('id'); // 'id' 매개변수로 상품 ID를 가져옴
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
                    <button onclick="goToPayment('${product.id}', '${product.name}', ${product.price})">구매하기</button>
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
