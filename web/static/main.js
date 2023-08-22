let me = "";
const users = new Map();

let canSendIsTyping = true;

const input = document.getElementById("message-input");
input.addEventListener("keypress", (event) => {
  if (event.key === "Enter") {
    send(event);
  } else {
    if (canSendIsTyping) {
      ws.send(
        JSON.stringify({
          type: "typing",
        })
      );
      canSendIsTyping = false;
      setTimeout(() => {
        canSendIsTyping = true;
      }, 200);
    }
  }
});
const fileInput = document.getElementById("uploader");
const clearBtn = document.getElementById("clear-btn");
clearBtn.addEventListener("click", clearInputs);

// DUMMY scroll
// setTimeout(() => {
//   const scroller = document.getElementById("scroller");
//   scroller.scrollTo(0, scroller.scrollHeight);
// }, 200);

const host = window.location.host;
const ws = new WebSocket(`ws://${host}/ws`);
const usersList = document.getElementById("users_list");
const messages = document.getElementById("messages");

ws.onopen = (event) => {
  console.log("Connected");
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.from === "ChatBot" && data.type === "me") {
    me = data.me;
  } else if (data.type == "users_list" && data.from == "ChatBot") {
    handleUsersList(data);
  } else if (data.type === "message") {
    handleChatMessage(data);
  } else if (data.type === "typing") {
    activity_user(data);
  } else {
    console.warn("Unknown message type", data);
  }
};

ws.onclose = (event) => {
  console.log("Connection closed");
  input.setAttribute("disabled", "");
};

function send(event) {
  sendFile();
  const txt = input.value.trim();
  if (txt.length > 0) {
    ws.send(
      JSON.stringify({
        type: "message",
        text: input.value,
      })
    );
  }
  input.value = "";
  event.preventDefault();
}

function sendFile() {
  const file = fileInput.files[0]; // получаем выбранный файл
  if (!file) return;
  const xhr = new XMLHttpRequest(); // создаем объект XMLHttpRequest
  const formData = new FormData(); // создаем объект FormData для передачи файла
  formData.append("file", file); // добавляем файл в объект FormData
  xhr.open("POST", "/upload"); // указываем метод и URL сервера, куда будет отправлен файл
  xhr.send(formData); // отправляем запрос на сервер с помощью метода send()
  fileInput.value = "";
}

function createFileTag(file) {
  if (file.content_type === "image") {
    const img = document.createElement("img");
    img.src = file.path;
    img.style = "width: 400px";
    return img;
  } else if (file.content_type === "video") {
    const video = document.createElement("video");
    video.src = file.path;
    video.style = "width: 400px";
    video.controls = true;
    video.muted = true;
    return video;
  } else if (file.content_type === "audio") {
    const audio = document.createElement("audio");
    audio.src = file.path;
    audio.controls = true;
    return audio;
  } else if (file.content_type) {
    const link = document.createElement("a");
    link.textContent = file.path;
    link.href = file.path;
    link.target = "_blank";
    return link;
  }
}

function handleChatMessage(data) {
  const li = document.createElement("li");
  if (data.text) {
    li.textContent = `FROM: ${data.from} > ${data.text}`;
  }
  if (data.file) {
    const file = createFileTag(data.file);
    if (file) li.appendChild(file);
  }

  let shouldScroll = isAtBottom();
  
  messages.appendChild(li);

  if (shouldScroll) {
    scrollDown();
  }
}

function activity_user(data) {
  const u = users.get(data.user);
  u.el.setAttribute("style", "opacity:100%;");
  clearTimeout(u.timeout);
  u.timeout = setTimeout(() => {
    u.el.setAttribute("style", "opacity:0%;");
  }, 3000);
}

function handleUsersList(data) {
  while (usersList.firstChild) {
    usersList.removeChild(usersList.firstChild);
  }

  data.users.sort();
  users.clear();

  for (const user of data.users) {
    const li = document.createElement("li");
    li.textContent = `${user.name}`;
    const img = document.createElement("img");
    img.src = "/static/pen.png";
    img.className = "user-typing-icon";
    img.setAttribute("style", "opacity: 0%;");
    li.appendChild(img);
    if (user.isOnline === true) {
      li.setAttribute("style", "color: green;");
    } else {
      li.setAttribute("style", "color: red;");
    }
    usersList.appendChild(li);
    users.set(user.name, {
      el: img,
      timeout: null,
      isOnline: user.isOnline === true,
    });
  }

  return;
}

function clearInputs(event) {
  input.value = "";
  fileInput.value = "";
}

function isAtBottom() {
  let block = document.getElementById("scroller");
  return block.scrollHeight - block.scrollTop - block.clientHeight < 20;
}

function scrollDown() {
  let block = document.getElementById("scroller");
  block.scrollTop = block.scrollHeight;
}

// function scrollcheck() {
//   let block = document.getElementById("scroller");
//   const h = block.clientHeight;
//   // debugger
//   if (block.scrollTop >= block.scrollHeight - h) {
//     block.scrollTop = block.scrollHeight;
//   }
// }
