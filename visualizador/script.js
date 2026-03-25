let chartPy = null;
let chartJava = null;

async function obtenerDatos() {
    try {
        const topN = parseInt(document.getElementById("topN").value);

        const [resPy, resJava] = await Promise.all([
            fetch("mas_usados_py.json?cache=" + Date.now()),
            fetch("mas_usados_java.json?cache=" + Date.now())
        ]);

        const dataPy = await resPy.json();
        const dataJava = await resJava.json();

        actualizarGrafico(dataPy, topN, "py");
        actualizarGrafico(dataJava, topN, "java");

    } catch (error) {
        console.log("Esperando datos...");
    }
}

function actualizarGrafico(data, topN, tipo) {
    const top = data.slice(0, topN);

    const labels = top.map(x => x[0]);
    const valores = top.map(x => x[1]);

    if (tipo === "py") {
        if (!chartPy) {
            chartPy = crearGrafico("graficoPy", labels, valores, "Frecuencia", "rgba(59, 130, 246, 0.7)");
        } else {
            chartPy.data.labels = labels;
            chartPy.data.datasets[0].data = valores;
            chartPy.update();
        }
    }

    if (tipo === "java") {
        if (!chartJava) {
            chartJava = crearGrafico("graficoJava", labels, valores, "Frecuencia", "rgba(249, 115, 22, 0.7)");
        } else {
            chartJava.data.labels = labels;
            chartJava.data.datasets[0].data = valores;
            chartJava.update();
        }
    }
}

function crearGrafico(id, labels, valores, titulo, color) {
    const ctx = document.getElementById(id).getContext("2d");

    return new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: titulo,
                data: valores,
                backgroundColor: color
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: "white" }
                }
            },
            scales: {
                x: {
                    ticks: { color: "white" }
                },
                y: {
                    beginAtZero: true,
                    ticks: { color: "white" }
                }
            }
        }
    });
}

setInterval(obtenerDatos, 2000);
obtenerDatos();