(function () {
  const container = document.getElementById("missions_list");
  if (!container) return;

  const missions = [];

  function renderMissions() {
    container.innerHTML = "";
    missions.forEach(mission => {
      const div = document.createElement("div");
      div.className = "mission-row";
      div.innerHTML = `
        <b>ID:</b> ${mission.id} |
        <b>Drone:</b> ${mission.drone_id || "не назначен"} |
        <b>Status:</b> ${mission.authorized ? "Разрешена" : "Отозвана"} |
        <button data-action="authorize" data-id="${mission.id}">Авторизовать</button>
        <button data-action="revoke" data-id="${mission.id}">Отозвать</button>
      `;
      container.appendChild(div);

      div.querySelectorAll("button").forEach(btn => {
        btn.addEventListener("click", () => {
          const action = btn.dataset.action;
          if (action === "authorize") {
            mission.authorized = true;
          } else if (action === "revoke") {
            mission.authorized = false;
          }
          WebUI.map.renderMissions?.();
          renderMissions();
        });
      });
    });
  }

  // API для добавления миссии
  window.WebUI.missions = {
    addMission: mission => {
      missions.push(Object.assign({ authorized: true }, mission));
      renderMissions();
      WebUI.map.addMission(mission);
    },
    getMissions: () => missions
  };

  renderMissions();
})();