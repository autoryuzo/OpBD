(function () {
  const container = document.getElementById("zones_list");
  if (!container) return;

  const zones = [];

  function renderZones() {
    container.innerHTML = "";
    zones.forEach(zone => {
      const div = document.createElement("div");
      div.className = "zone-row";
      div.innerHTML = `
        <b>${zone.name}</b> (${zone.type}) |
        <button data-action="delete" data-id="${zone.id}">Удалить</button>
      `;
      container.appendChild(div);

      div.querySelector("button").addEventListener("click", () => {
        const idx = zones.findIndex(z => z.id === zone.id);
        if (idx !== -1) {
          zones.splice(idx, 1);
          renderZones();
          WebUI.map.getZones().splice(idx, 1);
          WebUI.map.renderZones?.();
        }
      });
    });
  }

  // API для добавления зон
  window.WebUI.zones = {
    addZone: zone => {
      zones.push(zone);
      renderZones();
      WebUI.map.addZone(zone);
    },
    getZones: () => zones
  };

  renderZones();
})();