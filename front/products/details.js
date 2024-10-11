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
                    <img src="${product.image}" alt="${product.title}" width="300">
                    <h2>${product.title}</h2>
                    <p>${product.content}</p>
                    <p>가격: ${product.price}원</p>
                </div>
            `;
        })
        .catch(error => {
            console.error('상품 정보를 불러오는 중 오류 발생:', error);
            productDetail.innerHTML = '<p>상품 정보를 불러오는 중 오류가 발생했습니다.</p>';
        });
}

// 페이지가 로드될 때 상품 상세 정보를 가져옴
document.addEventListener('DOMContentLoaded', loadProductDetail);

// 뒤로가기 버튼 클릭 시 이전 페이지로 이동
function goBack() {
    window.history.back();
}
