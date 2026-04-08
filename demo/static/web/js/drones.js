(function () {
  const container = document.getElementById("drones_list");
  if (!container) return;

  const drones = [];

  function renderDrones() {
    container.innerHTML = "";
    drones.forEach(drone => {
      const div = document.createElement("div");
      div.className = "drone-row";
      div.innerHTML = `
        <b>ID:</b> ${drone.id} |
        <b>Status:</b> ${drone.status || "Неактивен"} |
        <button data-action="authorize_flight" data-id="${drone.id}">Авторизовать вылет</button>
      `;
      container.appendChild(div);

      div.querySelector("button").addEventListener("click", () => {
        drone.status = "Вылет разрешен";
        renderDrones();
      });
    });
  }

  // API для добавления дронов
  window.WebUI.drones = {
    addDrone: drone => {
      drones.push(Object.assign({ status: "Неактивен" }, drone));
      renderDrones();
      WebUI.map.addDrone(drone);
    },
    getDrones: () => drones
  };

  renderDrones();
})();