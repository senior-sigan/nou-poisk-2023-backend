// мы будем запрашивать разрешение на доступ только к аудио 
const constraints = { audio: true, video: false };
const record = document.getElementById('start_recording')
record.addEventListener("keypress", (event) => {
    if (event.key === "Enter") {
      startRecord(event);
    }
});

let stream = null;

navigator.mediaDevices.getUserMedia(constraints)
    .then((_stream) => { stream = _stream })
    // если возникла ошибка, значит, либо пользователь отказал в доступе, 
    // либо запрашиваемое медиа-устройство не обнаружено 
    .catch((err) => { console.error(`Not allowed or not found: ${err}`) });

let chunks = [];
let mediaRecorder = null;
let audioBlod = null;

async function startRecord() { 
    // проверяем поддержку 
    if (!navigator.mediaDevices && !navigator.mediaDevices.getUserMedia) { 
        return console.warn('Not supported'); 
    }
    // если запись не запущена 
    if (!mediaRecorder) { 
        try { 
            // получаем поток аудио-данных 
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: true 
            }) ;
            // создаем экземпляр `MediaRecorder`, передавая ему поток в качестве аргумента 
            mediaRecorder = new MediaRecorder(stream) ;
            // запускаем запись 
            mediaRecorder.start() ;
            console.log('Record starting...')
            // по окончанию записи и наличии данных добавляем эти данные в соответствующий массив 
            mediaRecorder.ondataavailable = (e) => { 
                chunks.push(e.data) 
            } ;
        } catch (e) { 
            console.error(e);
        };
    }else{
        //если запись запущена, останавливаем её
        mediaRecorder.onstop = mediaRecorderStop ;
        console.log('Recording finish')
        mediaRecorder.stop();
    };
}

function mediaRecorderStop() { 
    // если имеется предыдущая (новая) запись 
    if (audio_box.children[0]?.localName === 'audio') { 
        // удаляем ее 
        audio_box.children[0].remove();
    }

    // создаем объект `Blob` с помощью соответствующего конструктора, 
    // передавая ему `blobParts` в виде массива и настройки с типом создаваемого объекта 
    // о том, что такое `Blob` и для чего он может использоваться
    // очень хорошо написано здесь: https://learn.javascript.ru/blob 
    audioBlod = new Blob(chunks, { type: 'audio/mp3'});
    // метод `createObjectURL()` может использоваться для создания временных ссылок на файлы 
    // данный метод "берет" `Blob` и создает уникальный `URL` для него в формате `blob:/` 
    const src = URL.createObjectURL(audioBlod);
     
    // создаем элемент `audio` 
    const audioEl = document.createElement('audio');
    audioEl.src = src;
    audioEl.controls = true;
    console.log(audioEl)
    audio_box.append(audioEl);

    // выполняем очистку 
    mediaRecorder = null;
    chunks = [];
}