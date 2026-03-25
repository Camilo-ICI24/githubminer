/**
 * script.js
 * 
 * Lógica interna para cargar los JSON generados por main_miner.py
 * y dibujar gráficos de barras con Chart.js mostrando las palabras
 * más populares en métodos de Python y Java.
 * 
 * Funcionalidad:
 * - Fetch de mas_usados_py.json y mas_usados_java.json
 * - Crear gráfico dinámico según Top N definido por el usuario
 * - Actualizar automáticamente cada 2 segundos
 */

let chartPy = null; // Gráfico para Python
let chartJava = null; // Gráfico para Java

/**
 * Obtiene los datos almacenados en los archivos JSON y actualiza ambos gráficos.
 * Se llama automáticamente cada 2 segundos.
 */
async function obtenerDatos() {
    try {
        const topN = parseInt(document.getElementById("topN").value);

        // Obtiene ambas listas de manera simultánea
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

/**
 * Actualiza el gráfico correspondiente (Python o Java) con los datos nuevos.
 * 
 * @param {Array} data - Array de tuplas [palabra, frecuencia].
 * @param {number} topN - Cantidad de palabras a mostrar.
 * @param {string} tipo - "py" para Python, "java" para Java.
 */
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

/**
 * Crea un gráfico visual de barras con Chart.js.
 * 
 * @param {string} id - ID del lienzo (canvas) donde se dibujará el gráfico.
 * @param {Array} labels - Etiquetas de las barras.
 * @param {Array} valores - Valores de cada barra.
 * @param {string} titulo - Título del dataset.
 * @param {string} color - Color de las barras en formato RGBA.
 * @returns {Chart} Instancia del gráfico creado.
 */
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

// Actualización cada dos segundos
setInterval(obtenerDatos, 2000);
obtenerDatos();