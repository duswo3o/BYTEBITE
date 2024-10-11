const API_BASE_URL = 'http://127.0.0.1:8000/api/v1/';

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
                                <img src="${product.image}" alt="${product.title}" class="product-image">
                                <h2 class="product-title">${product.title}</h2>
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
