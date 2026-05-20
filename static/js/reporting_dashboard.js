/**
 * Gráficos y calendario del dashboard de reporting (Integrante 4).
 */
(function () {
  function readJsonScript(id) {
    const el = document.getElementById(id);
    if (!el) return null;
    try {
      return JSON.parse(el.textContent);
    } catch (e) {
      console.error(e);
      return null;
    }
  }

  function initCharts() {
    const semana = readJsonScript('reporting-data-semana');
    const porMes = readJsonScript('reporting-data-mes');
    const salas = readJsonScript('reporting-data-salas');

    if (semana && window.Chart) {
      const ctx = document.getElementById('chartSemanal');
      if (ctx) {
        new Chart(ctx, {
          type: 'bar',
          data: {
            labels: semana.labels,
            datasets: [
              {
                label: 'Reservas',
                data: semana.data,
                backgroundColor: 'rgba(13, 110, 253, 0.55)',
                borderColor: 'rgba(13, 110, 253, 1)',
                borderWidth: 1,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
              y: { beginAtZero: true, ticks: { precision: 0 } },
            },
          },
        });
      }
    }

    if (porMes && window.Chart) {
      const ctx2 = document.getElementById('chartMensual');
      if (ctx2) {
        new Chart(ctx2, {
          type: 'line',
          data: {
            labels: porMes.labels,
            datasets: [
              {
                label: 'Reservas',
                data: porMes.data,
                fill: true,
                tension: 0.25,
                borderColor: 'rgba(25, 135, 84, 1)',
                backgroundColor: 'rgba(25, 135, 84, 0.15)',
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
              y: { beginAtZero: true, ticks: { precision: 0 } },
            },
          },
        });
      }
    }

    if (salas && window.Plotly) {
      const el = document.getElementById('plotSalas');
      if (el && Array.isArray(salas) && salas.length) {
        const nombres = salas.map((s) => s.nombre);
        const totales = salas.map((s) => s.total);
        Plotly.newPlot(
          el,
          [
            {
              type: 'bar',
              orientation: 'h',
              x: totales,
              y: nombres,
              marker: { color: '#6610f2' },
            },
          ],
          {
            margin: { l: 160, t: 24, r: 24, b: 48 },
            xaxis: { title: 'Reservas', dtick: 1 },
            yaxis: { automargin: true },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
          },
          { responsive: true, displayModeBar: false }
        );
      } else if (el) {
        el.innerHTML =
          '<p class="text-muted mb-0">No hay reservas por sala en este rango.</p>';
      }
    }
  }

  function initCalendar() {
    const calEl = document.getElementById('calendar');
    if (!calEl || !window.FullCalendar) return;

    const baseUrl = window.REPORTING_CALENDAR_EVENTS_URL;

    const calendar = new FullCalendar.Calendar(calEl, {
      initialView: 'dayGridMonth',
      locale: 'es',
      height: 'auto',
      headerToolbar: {
        left: 'prev,next today',
        center: 'title',
        right: 'dayGridMonth,timeGridWeek,listWeek',
      },
      events: function (info, successCallback, failureCallback) {
        const u = new URL(baseUrl, window.location.origin);
        u.searchParams.set('start', info.startStr);
        u.searchParams.set('end', info.endStr);
        fetch(u.toString(), {
          credentials: 'same-origin',
          headers: { 'X-Requested-With': 'XMLHttpRequest' },
        })
          .then((r) => r.json())
          .then(successCallback)
          .catch(failureCallback);
      },
    });
    calendar.render();
  }

  document.addEventListener('DOMContentLoaded', function () {
    initCharts();
    initCalendar();
  });
})();
