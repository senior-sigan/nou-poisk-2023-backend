console.log("Hello!");

const input = document.getElementById("message-input");
input.addEventListener("keypress", (event) => {
  if (event.key === "Enter") {
    send(event);
  }
});

const host = window.location.host;
const ws = new WebSocket(`ws://${host}/ws`);
let me = "";

const usersList = document.getElementById("users_list"); 
const messages = document.getElementById("messages");
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);

  if (data.from === "ChatBot" && data.type === "me") {
    me = data.me;
    return;
  }

  if (data.type == "users_list" && data.from == "ChatBot") {
    while (usersList.firstChild) {
      usersList.removeChild(usersList.firstChild);
    }

    data.users.sort();

    for (const user of data.users) {
      const li = document.createElement("li");
      li.textContent = `${user}`;
      usersList.appendChild(li);
    }

    return;
  }

  const li = document.createElement("li");
  if (data.text) {
    li.textContent = `FROM: ${data.from} > ${data.text}`;
  }
  if (data.content_type === "image") {
    const img = document.createElement("img");
    img.src = data.file;
    img.style = "width: 400px";
    const p = document.createElement("p");
    p.textContent = `FROM: ${data.from}`;
    li.appendChild(p);
    li.appendChild(img);
  } else if (data.content_type === "video") {
    const video = document.createElement("video");
    video.src = data.file;
    video.style = "width: 400px";
    video.controls = true;
    video.muted = true;
    const p = document.createElement("p");
    p.textContent = `FROM: ${data.from}`;
    li.appendChild(p);
    li.appendChild(video);
  } else if (data.content_type === "audio") {
    const audio = document.createElement("audio");
    audio.src = data.file;
    audio.controls = true;
    const p = document.createElement("p");
    p.textContent = `FROM: ${data.from}`;
    li.appendChild(p);
    li.appendChild(audio);
  } else if (data.content_type) {
    const link = document.createElement("a");
    link.textContent = data.file;
    link.href = data.file;
    link.target = "_blank";
    const p = document.createElement("p");
    p.textContent = `FROM: ${data.from}`;
    li.appendChild(p);
    li.appendChild(link);
  }

  messages.appendChild(li);
};

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
  const fileInput = document.getElementById("uploader"); // получаем элемент input для загрузки файла
  const file = fileInput.files[0]; // получаем выбранный файл
  if (!file) return;
  const xhr = new XMLHttpRequest(); // создаем объект XMLHttpRequest
  const formData = new FormData(); // создаем объект FormData для передачи файла
  formData.append("file", file); // добавляем файл в объект FormData
  xhr.open("POST", "/upload"); // указываем метод и URL сервера, куда будет отправлен файл
  xhr.send(formData); // отправляем запрос на сервер с помощью метода send()
  fileInput.value = "";
}
