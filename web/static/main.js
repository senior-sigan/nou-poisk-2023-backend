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
  li.textContent = `FROM: ${data.from} > ${data.text}`;
  messages.appendChild(li);
}

function send(event) {
  const txt = input.value.trim();
  if (txt.length > 0) {
    ws.send(input.value);
  }  
  input.value = "";
  event.preventDefault();
}
