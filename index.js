
const button = document.querySelector('#my-button');
const textarea = document.querySelector('textarea');
const divContainer = document.querySelector('.inner-div');
const keysDiv = document.querySelector('.keys');
const prevDocs = document.querySelector('.prev-docs');
let icons = document.getElementsByTagName('i');

const buttonLogin = document.querySelector('#button-login');
const buttonRegister = document.querySelector('#button-register');
const modal = document.querySelector('.modal');
const modal2 = document.querySelector('.modal2');



buttonLogin.addEventListener('click', function() {
  modal.style.display = 'block';  // modeli göster
});

buttonRegister.addEventListener('click', function() {
  modal2.style.display = "block";
});

textarea.addEventListener('input', function() {
  divContainer.innerHTML = "";
  const pElements = keysDiv.querySelectorAll('p');
  pElements.forEach(p => p.remove());  // tüm p elementlerini kaldır
  keysDiv.style.display="none"
});

button.addEventListener('click', function() {
  const textarea = document.querySelector('textarea');
  const text = textarea.value;
  const data = {
    "document": [
      text
    ]
  };
  if(text.length>30){
    document.getElementById("loadingSpin").style.display = "flex";
    fetch('http://localhost:8080/newDocument', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
      document.getElementById("loadingSpin").style.display = "none";
      divContainer.innerHTML = data.summary;
      keysDiv.style.display="flex"
      for (let i = 0; i < 10; i++) {
        const p = document.createElement('p');
        p.style.marginRight = "10px"; 
        p.textContent = data.keys[i];
        keysDiv.appendChild(p);
      }
      var userId = sessionStorage.getItem("user_id");
      if(userId){
        fetch('http://localhost:8080/saveNewDocument', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            document:text,
            user_id:userId
          })
        })
        .then(response => response.json())
        .then(data=>{
          console.log(data)


          const p = document.createElement('p');
          const div = document.createElement('div');

          const deleteIcon = document.createElement('i');
          deleteIcon.classList.add("fa","fa-trash");
          deleteIcon.setAttribute('aria-hidden', true);
          deleteIcon.style.cssFloat = "right";
          deleteIcon.id = "deleteIcon";
          deleteIcon.dataset.myValue=data.text_id
          div.dataset.myValue=data.text_id

          div.id="innerDiv"
          p.setAttribute('id', 'special-p');
          div.appendChild(deleteIcon);
          p.textContent = text
          p.style.marginRight = "10px"; 
          
          div.appendChild(p);
          prevDocs.insertBefore(div, prevDocs.firstChild);
          iconsDetect();
        }).catch(err=>console.log(err))
      }
    })
    .catch(error => console.error(error));
  }
});



const modalContent = document.querySelector('.modal-content');

const closeButton = document.querySelector('.close');
const closeButton2 = document.querySelector('.close2');

closeButton2.addEventListener("click", function() {
  modal2.style.display = "none";
});

window.onclick = function(event) {
  if (event.target == modal || event.target == closeButton) {
    modal.style.display = 'none';  // gizle
  }
}
modal2.addEventListener("click", function(event) {
  if (event.target.className === 'modal2') {
    modal2.style.display = "none";
  }
});

document.getElementById("registerButton").addEventListener("click", function(event) {
  event.preventDefault();
  const pElements = prevDocs.querySelectorAll('div');
  pElements.forEach(p => p.remove());  // tüm p elementlerini kaldır
  const password = document.getElementById("password2").value;
  const passwordConfirm = document.getElementById("passwordConfirm").value;
  if (password === passwordConfirm) {
    fetch('http://localhost:8080/newUser', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username: document.getElementById("username2").value,
        password: password
      })
    })
    .then(response => response.json())
    .then(data => {
      console.log(data)
      sessionStorage.setItem("user_id", data.user_id);
      sessionStorage.setItem("username", data.username);
      buttonLogin.innerHTML  = data.username;
      modal2.style.display = 'none';  // gizle
    }).catch(err=>console.log(err))
  }
  else {
    alert("Şifreler eşleşmiyor!");
  }
});

document.getElementById("login").addEventListener("click", function() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  if (!username || !password) {
    alert("Lütfen alanları doldurun");
    return;
  }

  const data = {
    "username": username,
    "password": password
  };

  fetch("http://localhost:8080/user", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(data)
  })
  .then(response => response.json())
  .then(data => {
    console.log(data)
    sessionStorage.setItem("user_id", data.user_id);
    sessionStorage.setItem("username", data.username);
    buttonLogin.innerHTML  = data.username;
    modal.style.display = 'none';  // gizle
    fetch("http://localhost:8080/getDocuments", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        user_id:data.user_id
      })
    })
    .then(response => response.json())
    .then(data => {
      console.log(data)
      const pElements = prevDocs.querySelectorAll('div');
      pElements.forEach(p => p.remove());  // tüm p elementlerini kaldır
      if(data?.texts){
        for (let i =0; i <data?.texts?.length; i++) {
          const p = document.createElement('p');
          const div = document.createElement('div');

          const deleteIcon = document.createElement('i');
          deleteIcon.classList.add("fa","fa-trash");
          deleteIcon.setAttribute('aria-hidden', true);
          deleteIcon.style.cssFloat = "right";
          deleteIcon.id = "deleteIcon";
          deleteIcon.dataset.myValue=data.texts[i][0]
          div.dataset.myValue=data.texts[i][0]

          div.id="innerDiv"
          p.setAttribute('id', 'special-p');
          div.appendChild(deleteIcon);
/*           let textTemp=text.split(',')[1] */
          p.dataset.myValue=data.texts[i][0]
          p.textContent = data.texts[i][1];
          p.style.marginRight = "10px"; 
          
          div.appendChild(p);
          prevDocs.appendChild(div);
        }
        iconsDetect();
      }
    })
    .catch(function(error) {
      console.error(error);
      alert("Invalid username or password")
    });
  })
  .catch(function(error) {
    console.error(error);
    alert("Invalid username or password")
  });

  if(!sessionStorage.getItem("username")){
    alert("Invalid username or password")
  }
});

function iconsDetect(){
  icons = document.getElementsByTagName('i');
  for (let i = 0; i < icons.length; i++) {
    icons[i].addEventListener('click', event => {
      const document_id= icons[i].getAttribute('data-my-value');
      const user_id = sessionStorage.getItem("user_id");
      fetch("http://localhost:8080/deleteDocument", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          user_id:user_id,
          document_id:document_id,
        })
      })
      .then(response => {
        const divs = document.getElementsByTagName('div');
        for (let i = 0; i < divs.length; i++) {
          const element = divs[i];
          if (element.getAttribute('data-my-value') === document_id) {
            element.remove();
          }
        }
      })
      .then(data => {
        console.log(data)
      })
      .catch(function(error) {
        console.error(error);   
      });
    });
  }
}


