import axios from "axios";

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1'

const signupBtn = document.getElementById("signup-btn");

const signupUser = () => {
    axios.post(`${API_BASE_URL}/accounts/`, {
        email : document.getElementById('InputEmail').value,
        password : document.getElementById('InputPassword').value,
        confirm_password : document.getElementById('confirmInputPassword').value,
        nickname : document.getElementById('InputNickname').value,
        gender : document.getElementById('inputGender').value,
        age : document.getElementById('InputAge').value,
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