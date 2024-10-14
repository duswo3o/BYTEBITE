const API_BASE_URL = 'https://api.popcorngeek.store/api/v1/';

document.addEventListener('DOMContentLoaded', function () {
    const productList = document.getElementById('product-list');

    function fetchProducts() {
        axios.get(`${API_BASE_URL}products/`)
            .then(response => {
                const products = response.data;

                // 상품 목록을 카드 형식으로 출력
                let output = '';
                products.forEach(product => {
                    output += `
                        <li class="product-card">
                            <a href="details.html?id=${product.id}" class="product-link"> <!-- 상품 상세 페이지 링크 -->
                                <img src="${product.image}" alt="${product.name}" class="product-image">
                                <h2 class="product-name">${product.name}</h2>
                                <p class="product-content">${product.content}</p>
                                <p class="product-price">가격: ${product.price}원</p>
                            </a>
                        </li>
                    `;
                });
                productList.innerHTML = output;
            })
            .catch(error => {
                console.error('상품 데이터를 불러오는 중 오류 발생:', error);
                productList.innerHTML = '<p>상품 데이터를 불러오는 중 오류가 발생했습니다.</p>';
            });
    }

    fetchProducts();
});

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

