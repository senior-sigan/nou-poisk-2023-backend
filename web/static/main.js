console.log('Hello!');

const input = document.getElementById('message-input');
input.addEventListener("keypress", (event) => {
  if (event.key === "Enter") {
    send(event);
  }
});

const host = window.location.host;
const ws = new WebSocket(`ws://${host}/ws`);


const messages = document.getElementById('messages');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
  const li = document.createElement('li');
  if (data.text) {
    li.textContent = `FROM: ${data.from} > ${data.text}`;
  }
  if (data.image) {
    const img = document.createElement('img');
    img.src = data.image;
    img.style = "width: 400px";
    const p = document.createElement('p');
    p.textContent =  `FROM: ${data.from}`;
    li.appendChild(p);
    li.appendChild(img);
  }
  messages.appendChild(li);
}

function send(event) {
  sendFile();
  const txt = input.value.trim();
  if (txt.length > 0) {
    ws.send(input.value);
  }  
  input.value = "";
  event.preventDefault();
}

function sendFile() {
  const fileInput = document.getElementById('uploader'); // получаем элемент input для загрузки файла 
  const file = fileInput.files[0]; // получаем выбранный файл 
  if (!file) return;
  const xhr = new XMLHttpRequest(); // создаем объект XMLHttpRequest 
  const formData = new FormData(); // создаем объект FormData для передачи файла 
  formData.append('file', file); // добавляем файл в объект FormData 
  xhr.open('POST', '/upload'); // указываем метод и URL сервера, куда будет отправлен файл 
  xhr.send(formData); // отправляем запрос на сервер с помощью метода send()
  fileInput.value = '';
}
