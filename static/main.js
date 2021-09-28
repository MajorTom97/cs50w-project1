/* User Login */

document.addEventListener('DOMContentLoaded'),
var attempt = 3;
function validate() {
    var username = document.getElementbyId("username: ").value;
    var password = document.getElementbyId("password: ").value;
    var email = document.getElementbyId("email: ").value();
    if (username == ull  || username == ""){
        alert("Enter an username!")
        return false;
    }
    if (password == null  || password == ""){
        alert("Enter the password");
        return false;
    }
    if (email == null  || email == ""){
        alert("Enter the E-mail");
        return false;
    }
    else{
        attempt --;
        alert("You have left" + attempt +"attempt;");
    }
    //Disable field after three attempts
    //Check the page https://www.formget.com/javascript-login-form/
    if (attempt == 0){
        document.getElementById("username").disabled = true;
        document.getElementById("password").disabled = true;
        document.getElementById("email").disabled = true;
        return false;
    }
}