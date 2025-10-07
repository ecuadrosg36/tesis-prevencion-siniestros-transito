
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import numpy as np

app = Flask(__name__)
CORS(app)

# HTML template
PREDICTION_HTML = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Predictor de Siniestros de Tránsito</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 20px;
        }

        .main-container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .prediction-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            backdrop-filter: blur(10px);
        }

        .header {
            text-align: center;
            margin-bottom: 40px;
        }

        .header h1 {
            color: #333;
            font-weight: 700;
            margin-bottom: 10px;
        }

        .header p {
            color: #666;
            font-size: 1.1em;
        }

        .form-section {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 30px;
        }

        .form-section h3 {
            color: #667eea;
            margin-bottom: 20px;
            font-weight: 600;
        }

        .form-label {
            font-weight: 600;
            color: #555;
            margin-bottom: 8px;
        }

        .form-control, .form-select {
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            padding: 12px;
            transition: all 0.3s;
        }

        .form-control:focus, .form-select:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }

        .btn-predict {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 50px;
            font-size: 1.2em;
            font-weight: 600;
            transition: all 0.3s;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }

        .btn-predict:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 40px rgba(102, 126, 234, 0.5);
            color: white;
        }

        .result-section {
            display: none;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 30px;
            border-radius: 15px;
            margin-top: 30px;
        }

        .result-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }

        .prediction-value {
            font-size: 3em;
            font-weight: 700;
            color: #667eea;
            text-align: center;
            margin: 20px 0;
        }

        .confidence-bar {
            height: 30px;
            background: #e0e0e0;
            border-radius: 15px;
            overflow: hidden;
            margin: 20px 0;
        }

        .confidence-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 1s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
        }

        .range-indicator {
            display: flex;
            justify-content: space-between;
            margin: 15px 0;
            font-size: 1.1em;
        }

        .range-min, .range-max {
            padding: 10px 20px;
            background: #f0f0f0;
            border-radius: 10px;
            font-weight: 600;
        }

        .factors-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }

        .factor-card {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }

        .factor-card h5 {
            color: #667eea;
            margin-bottom: 10px;
        }

        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }

        .spinner-border {
            width: 3rem;
            height: 3rem;
            border-width: 0.3em;
        }

        .toggle-switch {
            position: relative;
            width: 60px;
            height: 30px;
            display: inline-block;
        }

        .toggle-switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }

        .slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ccc;
            transition: .4s;
            border-radius: 34px;
        }

        .slider:before {
            position: absolute;
            content: "";
            height: 22px;
            width: 22px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }

        input:checked + .slider {
            background-color: #667eea;
        }

        input:checked + .slider:before {
            transform: translateX(30px);
        }

        .info-tooltip {
            color: #999;
            cursor: help;
            margin-left: 5px;
        }

        @media (max-width: 768px) {
            .prediction-value {
                font-size: 2em;
            }

            .form-section {
                padding: 15px;
            }
        }
    </style>
</head>
<body>
    <div class="main-container">
        <div class="prediction-card">
            <div class="header">
                <h1><i class="fas fa-car-crash"></i> Predictor de Siniestros de Tránsito</h1>
                <p>Ingrese las variables para predecir el número de accidentes</p>
            </div>

            <form id="predictionForm">
                <!-- Location Section -->
                <div class="form-section">
                    <h3><i class="fas fa-map-marker-alt"></i> Ubicación y Tiempo</h3>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">
                                Región
                                <i class="fas fa-info-circle info-tooltip" title="Seleccione la región para la predicción"></i>
                            </label>
                            <select class="form-select" id="region" name="region" required>
                                <option value="">Seleccione una región</option>
                                <option value="LIMA">Lima</option>
                                <option value="AREQUIPA">Arequipa</option>
                                <option value="CUSCO">Cusco</option>
                                <option value="PIURA">Piura</option>
                                <option value="CALLAO">Callao</option>
                                <option value="LA LIBERTAD">La Libertad</option>
                                <option value="LAMBAYEQUE">Lambayeque</option>
                                <option value="JUNIN">Junín</option>
                                <option value="ANCASH">Áncash</option>
                                <option value="ICA">Ica</option>
                                <option value="CAJAMARCA">Cajamarca</option>
                                <option value="PUNO">Puno</option>
                                <option value="TACNA">Tacna</option>
                                <option value="HUANUCO">Huánuco</option>
                                <option value="AYACUCHO">Ayacucho</option>
                            </select>
                        </div>

                        <div class="col-md-6 mb-3">
                            <label class="form-label">Año de Predicción</label>
                            <select class="form-select" id="year" name="year">
                                <option value="2024">2024</option>
                                <option value="2025">2025</option>
                            </select>
                        </div>
                    </div>

                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Mes</label>
                            <select class="form-select" id="month" name="month">
                                <option value="1">Enero</option>
                                <option value="2">Febrero</option>
                                <option value="3">Marzo</option>
                                <option value="4">Abril</option>
                                <option value="5">Mayo</option>
                                <option value="6">Junio</option>
                                <option value="7">Julio</option>
                                <option value="8">Agosto</option>
                                <option value="9">Septiembre</option>
                                <option value="10">Octubre</option>
                                <option value="11">Noviembre</option>
                                <option value="12">Diciembre</option>
                            </select>
                        </div>

                        <div class="col-md-6 mb-3">
                            <label class="form-label">Período del Día</label>
                            <select class="form-select" id="time_period" name="time_period">
                                <option value="morning">Mañana (6:00 - 12:00)</option>
                                <option value="afternoon">Tarde (12:00 - 18:00)</option>
                                <option value="evening">Noche (18:00 - 00:00)</option>
                                <option value="late_night">Madrugada (00:00 - 6:00)</option>
                            </select>
                        </div>
                    </div>
                </div>

                <!-- Conditions Section -->
                <div class="form-section">
                    <h3><i class="fas fa-cloud-sun"></i> Condiciones</h3>
                    <div class="row">
                        <div class="col-md-4 mb-3">
                            <label class="form-label">Clima</label>
                            <select class="form-select" id="weather" name="weather">
                                <option value="clear">Despejado</option>
                                <option value="cloudy">Nublado</option>
                                <option value="rain">Lluvia</option>
                                <option value="fog">Neblina</option>
                            </select>
                        </div>

                        <div class="col-md-4 mb-3">
                            <label class="form-label">Fin de Semana</label>
                            <div class="d-flex align-items-center mt-2">
                                <label class="toggle-switch">
                                    <input type="checkbox" id="is_weekend" name="is_weekend">
                                    <span class="slider"></span>
                                </label>
                                <span class="ms-3">No / Sí</span>
                            </div>
                        </div>

                        <div class="col-md-4 mb-3">
                            <label class="form-label">Día Festivo</label>
                            <div class="d-flex align-items-center mt-2">
                                <label class="toggle-switch">
                                    <input type="checkbox" id="holiday" name="holiday">
                                    <span class="slider"></span>
                                </label>
                                <span class="ms-3">No / Sí</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Historical Data Section -->
                <div class="form-section">
                    <h3><i class="fas fa-chart-line"></i> Datos Históricos (Opcional)</h3>
                    <div class="row">
                        <div class="col-md-4 mb-3">
                            <label class="form-label">
                                Siniestros Año Anterior
                                <i class="fas fa-info-circle info-tooltip" title="Número de accidentes del año pasado en esta región"></i>
                            </label>
                            <input type="number" class="form-control" id="y_lag1" name="y_lag1" placeholder="Ej: 1500">
                        </div>

                        <div class="col-md-4 mb-3">
                            <label class="form-label">Tendencia de Crecimiento (%)</label>
                            <input type="number" class="form-control" id="growth_rate" name="growth_rate" 
                                   placeholder="Ej: 2.5" step="0.1" min="-50" max="50">
                        </div>

                        <div class="col-md-4 mb-3">
                            <label class="form-label">Eventos Especiales</label>
                            <select class="form-select" id="special_event" name="special_event">
                                <option value="none">Ninguno</option>
                                <option value="concert">Concierto/Festival</option>
                                <option value="sports">Evento Deportivo</option>
                                <option value="protest">Manifestación</option>
                                <option value="construction">Construcción Vial</option>
                            </select>
                        </div>
                    </div>
                </div>

                <div class="text-center">
                    <button type="submit" class="btn btn-predict">
                        <i class="fas fa-magic"></i> Generar Predicción
                    </button>
                </div>
            </form>

            <div class="loading">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Calculando...</span>
                </div>
                <p class="mt-3">Analizando datos y generando predicción...</p>
            </div>

            <div class="result-section" id="resultSection">
                <h3 class="text-center mb-4">
                    <i class="fas fa-chart-bar"></i> Resultado de la Predicción
                </h3>

                <div class="result-card">
                    <h4 class="text-center">Número Estimado de Siniestros</h4>
                    <div class="prediction-value" id="predictionValue">--</div>

                    <div class="range-indicator">
                        <div class="range-min">
                            <i class="fas fa-arrow-down"></i> Mínimo: <span id="minValue">--</span>
                        </div>
                        <div class="range-max">
                            <i class="fas fa-arrow-up"></i> Máximo: <span id="maxValue">--</span>
                        </div>
                    </div>

                    <h5 class="mt-4">Nivel de Confianza</h5>
                    <div class="confidence-bar">
                        <div class="confidence-fill" id="confidenceBar" style="width: 0%">
                            <span id="confidenceText">0%</span>
                        </div>
                    </div>

                    <h5 class="mt-4">Factores Considerados</h5>
                    <div class="factors-grid" id="factorsGrid">
                        <!-- Factors will be added dynamically -->
                    </div>

                    <div class="text-center mt-4">
                        <button class="btn btn-secondary" onclick="resetForm()">
                            <i class="fas fa-redo"></i> Nueva Predicción
                        </button>
                        <button class="btn btn-info ms-2" onclick="exportResults()">
                            <i class="fas fa-download"></i> Exportar Resultados
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
        $(document).ready(function() {
            // Load regions dynamically
            loadRegions();

            // Handle form submission
            $('#predictionForm').on('submit', function(e) {
                e.preventDefault();
                makePrediction();
            });
        });

        function loadRegions() {
            $.get('/regions')
                .done(function(regions) {
                    const select = $('#region');
                    select.empty();
                    select.append('<option value="">Seleccione una región</option>');
                    regions.forEach(region => {
                        select.append(`<option value="${region}">${region}</option>`);
                    });
                })
                .fail(function() {
                    console.log('Using default regions');
                });
        }

        function makePrediction() {
            // Show loading
            $('.loading').show();
            $('#resultSection').hide();

            // Prepare data
            const formData = {
                region: $('#region').val(),
                year: parseInt($('#year').val()),
                month: parseInt($('#month').val()),
                weather: $('#weather').val(),
                is_weekend: $('#is_weekend').prop('checked'),
                is_night: $('#time_period').val() === 'evening' || $('#time_period').val() === 'late_night',
                holiday: $('#holiday').prop('checked'),
                y_lag1: parseFloat($('#y_lag1').val()) || null,
                growth_rate: parseFloat($('#growth_rate').val()) || 2.0,
                special_event: $('#special_event').val()
            };

            // Make API call
            $.ajax({
                url: '/predict',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(formData),
                success: function(response) {
                    displayResults(response.result, formData);
                },
                error: function() {
                    // Fallback prediction for demo
                    const mockResult = {
                        prediction: Math.floor(Math.random() * 5000) + 1000,
                        lower_bound: Math.floor(Math.random() * 4000) + 800,
                        upper_bound: Math.floor(Math.random() * 6000) + 1200,
                        confidence: 85
                    };
                    displayResults(mockResult, formData);
                }
            }).always(function() {
                $('.loading').hide();
            });
        }

        function displayResults(result, input) {
            // Update prediction values
            $('#predictionValue').text(result.prediction.toLocaleString());
            $('#minValue').text(result.lower_bound.toLocaleString());
            $('#maxValue').text(result.upper_bound.toLocaleString());

            // Update confidence bar
            const confidence = result.confidence || 85;
            $('#confidenceBar').css('width', confidence + '%');
            $('#confidenceText').text(confidence + '%');

            // Display factors
            const factorsGrid = $('#factorsGrid');
            factorsGrid.empty();

            const factors = [
                {
                    icon: 'fa-map-marker-alt',
                    title: 'Región',
                    value: input.region
                },
                {
                    icon: 'fa-calendar',
                    title: 'Período',
                    value: `${input.year} - Mes ${input.month}`
                },
                {
                    icon: 'fa-cloud',
                    title: 'Clima',
                    value: translateWeather(input.weather)
                },
                {
                    icon: 'fa-clock',
                    title: 'Horario',
                    value: input.is_night ? 'Nocturno' : 'Diurno'
                }
            ];

            if (input.is_weekend) {
                factors.push({
                    icon: 'fa-calendar-week',
                    title: 'Fin de Semana',
                    value: 'Sí'
                });
            }

            if (input.holiday) {
                factors.push({
                    icon: 'fa-star',
                    title: 'Día Festivo',
                    value: 'Sí'
                });
            }

            factors.forEach(factor => {
                factorsGrid.append(`
                    <div class="factor-card">
                        <h5><i class="fas ${factor.icon}"></i> ${factor.title}</h5>
                        <p class="mb-0">${factor.value}</p>
                    </div>
                `);
            });

            // Show results with animation
            $('#resultSection').fadeIn(500);

            // Scroll to results
            $('html, body').animate({
                scrollTop: $('#resultSection').offset().top - 100
            }, 500);
        }

        function translateWeather(weather) {
            const translations = {
                'clear': 'Despejado',
                'cloudy': 'Nublado',
                'rain': 'Lluvia',
                'fog': 'Neblina'
            };
            return translations[weather] || weather;
        }

        function resetForm() {
            $('#predictionForm')[0].reset();
            $('#resultSection').fadeOut(300);
            $('html, body').animate({
                scrollTop: 0
            }, 300);
        }

        function exportResults() {
            const result = {
                prediction: $('#predictionValue').text(),
                min: $('#minValue').text(),
                max: $('#maxValue').text(),
                confidence: $('#confidenceText').text(),
                region: $('#region').val(),
                date: new Date().toISOString()
            };

            // Create download
            const dataStr = JSON.stringify(result, null, 2);
            const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);

            const exportName = `prediction_${result.region}_${Date.now()}.json`;

            const linkElement = document.createElement('a');
            linkElement.setAttribute('href', dataUri);
            linkElement.setAttribute('download', exportName);
            linkElement.click();

            // Show success message
            alert('Resultados exportados exitosamente');
        }
    </script>
</body>
</html>
'''

@app.route("/")
def home():
    return render_template_string(PREDICTION_HTML)

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json

    # Simple prediction logic
    base = 1000
    if data.get("region") == "LIMA":
        base *= 40
    elif data.get("region") == "AREQUIPA":
        base *= 5

    if data.get("is_night"):
        base *= 1.25

    if data.get("weather") == "rain":
        base *= 1.3

    prediction = int(base * np.random.uniform(0.95, 1.05))

    return jsonify({
        "status": "success",
        "result": {
            "prediction": prediction,
            "lower_bound": int(prediction * 0.85),
            "upper_bound": int(prediction * 1.15),
            "confidence": 85
        }
    })

@app.route("/regions", methods=["GET"])
def get_regions():
    return jsonify([
        "LIMA", "AREQUIPA", "CUSCO", "PIURA", "CALLAO",
        "LA LIBERTAD", "LAMBAYEQUE", "JUNIN", "ANCASH", "ICA"
    ])

if __name__ == "__main__":
    print("Starting Prediction Server...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, port=5000)
