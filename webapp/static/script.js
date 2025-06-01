function startProcess() {
  fetch("/start", { method: "POST" }).then(() => monitorProgress());
}

function monitorProgress() {
  const interval = setInterval(() => {
    fetch("/status")
      .then((res) => res.json())
      .then((data) => {
        document.getElementById("step").innerText = data.step;
        document.getElementById("progress").value = data.progress;

        if (data.done) {
          clearInterval(interval);
          loadResults();
        }
      });
  }, 1000);
}

function loadResults() {
  fetch("/api/results")
    .then((res) => res.json())
    .then((data) => {
      const container = document.getElementById("result");
      container.innerHTML = "<h2>📰 Головні новини</h2>";
      data.forEach((news) => {
        container.innerHTML += `
                    <div style="border:1px solid #ccc; padding:10px; margin:10px">
                        <h3>${news.Title}</h3>
                        <p><b>Дата:</b> ${news.Date}</p>
                        <p><b>Тема:</b> ${news.Category || news.Theme}</p>
                        <p><b>Анотація:</b> ${news.Summary}</p>
                    </div>
                `;
      });
    });
}

startBtn.addEventListener("click", () => {
  const selectedSites = Array.from(
    document.getElementById("news-sites").selectedOptions
  ).map((opt) => opt.value);
  const telegramChecked = document.getElementById("toggle-telegram").checked;
  const selectedTelegram = telegramChecked
    ? Array.from(
        document.getElementById("telegram-channels").selectedOptions
      ).map((opt) => opt.value)
    : [];

  if (selectedSites.length < 2) {
    alert("Оберіть щонайменше 2 джерела новинних сайтів.");
    return;
  }

  startBtn.disabled = true;
  progressContainer.style.display = "block";
  progressBar.style.width = "0%";
  statusText.textContent = "Запуск...";

  const eventSource = new EventSource("/progress");

  eventSource.onmessage = function (event) {
    const data = JSON.parse(event.data);
    progressBar.style.width = data.progress + "%";
    statusText.textContent = data.message;

    if (data.progress >= 100) {
      statusText.textContent = "Обробка завершена!";
      eventSource.close();
      setTimeout(() => {
        window.location.href = "/news";
      }, 1000);
    }
  };

  eventSource.onerror = function () {
    statusText.textContent = "Помилка отримання даних з сервера.";
    eventSource.close();
    startBtn.disabled = false;
  };

  fetch("/start", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      sources: selectedSites,
      telegram_channels: selectedTelegram,
    }),
  }).catch(() => {
    statusText.textContent = "Не вдалося запустити обробку.";
    startBtn.disabled = false;
    eventSource.close();
  });
});
