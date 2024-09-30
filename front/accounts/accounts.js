import axios from "axios";

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1'

const signupBtn = document.getElementById("signup-btn");

const signupUser = () => {
    // 선택필드에 빈 값이 들어가는 경우
    // 나이의 경우 숫자형으로 들어가야하는데 빈 값일때 빈문자열을 반환해서 null값으로 처리
    var age = document.getElementById('InputAge').value
    if (!age){
        age = null
    }
    axios.post(`${API_BASE_URL}/accounts/`, {
        email : document.getElementById('InputEmail').value,
        password : document.getElementById('InputPassword').value,
        confirm_password : document.getElementById('confirmInputPassword').value,
        nickname : document.getElementById('InputNickname').value,
        gender : document.getElementById('inputGender').value,
        age : age,
        bio : document.getElementById('InputBio').value,
    })
        .then(response => {
            console.log(response);
            // 이동할 페이지
            // window.location.href = ""
        })
        .catch(error => {
            console.log(error)
            // alert(email)
        })

}

signupBtn.addEventListener('click', signupUser)