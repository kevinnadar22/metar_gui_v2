// Global custom alert function
function showCustomAlert(message) {
    console.log('showCustomAlert called with:', message); // Debug log
    
    try {
        // Create alert container if it doesn't exist
        let alertContainer = document.getElementById('customAlertContainer');
        if (!alertContainer) {
            alertContainer = document.createElement('div');
            alertContainer.id = 'customAlertContainer';
            alertContainer.className = 'fixed bottom-4 right-4 z-50';
            document.body.appendChild(alertContainer);
        }

        // Create alert element
        const alert = document.createElement('div');
        alert.className = 'bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4 shadow-lg max-w-md';
        alert.innerHTML = `
            <span class="block sm:inline mr-8">${message}</span>
            <span class="absolute top-0 bottom-0 right-0 px-4 py-3">
                <svg class="fill-current h-6 w-6 text-red-500" role="button" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                    <title>Close</title>
                    <path d="M14.348 14.849a1.2 1.2 0 0 1-1.697 0L10 11.819l-2.651 3.029a1.2 1.2 0 1 1-1.697-1.697l2.758-3.15-2.759-3.152a1.2 1.2 0 1 1 1.697-1.697L10 8.183l2.651-3.031a1.2 1.2 0 1 1 1.697 1.697l-2.758 3.152 2.758 3.15a1.2 1.2 0 0 1 0 1.698z"/>
                </svg>
            </span>
        `;

        // Add to container
        alertContainer.appendChild(alert);

        // Add click handler to close button
        const closeButton = alert.querySelector('svg');
        closeButton.addEventListener('click', () => {
            alert.remove();
        });

        // Auto remove after 8 seconds (longer for validation errors)
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 8000);
        
        console.log('Custom alert created successfully');
    } catch (error) {
        console.error('Error creating custom alert:', error);
        // Fallback to browser alert
        alert(message);
    }
}

function populateTableFromCSV(csvText, tableElement) {
    // Parse CSV into rows
    const rows = csvText.trim().split("\n").map(row => row.split(","));

    // Clear old content
    tableElement.innerHTML = "";

    // Header
    const thead = tableElement.createTHead();
    const headerRow = thead.insertRow();
    rows[0].forEach(headerText => {
        const th = document.createElement("th");
        th.textContent = headerText.trim();
        th.className = "px-4 py-2 bg-gray-100 text-left font-semibold";
        headerRow.appendChild(th);
    });

    // Body
    const tbody = tableElement.createTBody();
    rows.slice(1).forEach(row => {
        const tr = tbody.insertRow();
        row.forEach(cellText => {
            const td = tr.insertCell();
            td.textContent = cellText.trim();
            td.className = "px-4 py-2 border";
        });
    });
}


// Initialize date pickers and file upload functionality
document.addEventListener('DOMContentLoaded', function () {
    // ===== INITIALIZATION FUNCTIONS =====

    

    // Initialize date-only pickers
    function initializeDatePickers() {
        flatpickr(".date-only-picker", {
            enableTime: false,
            dateFormat: "Y-m-d",
            static: true
        });
    }

    // Populate time selects (hours and minutes)
    function populateTimeSelects() {
        // Populate hour selects
        const hourSelects = document.querySelectorAll('.hour-select');
        hourSelects.forEach(select => {
            for (let i = 0; i < 24; i++) {
                const option = document.createElement('option');
                option.value = i;
                option.textContent = i.toString().padStart(2, '0');
                select.appendChild(option);
            }
        });

        // Populate minute selects
        const minuteSelects = document.querySelectorAll('.minute-select');
        minuteSelects.forEach(select => {
            for (let i = 0; i < 60; i++) {
                const option = document.createElement('option');
                option.value = i;
                option.textContent = i.toString().padStart(2, '0');
                select.appendChild(option);
            }
        });
    }

    // ===== ELEMENT REFERENCES =====

    // UI Elements
    const fileInputs = document.querySelectorAll('input[type="file"]');
    const datePickerSection = document.querySelector('.date-picker-section');
    const obsFileInput = document.querySelector('.obs-file-input');
    const obsUploadArea = obsFileInput.closest('.upload-area');
    const hrLine = document.querySelector('.upload-box hr');
    const toggleBtn = document.getElementById('toggleInputBtn');
    const obsUploadBox = obsUploadArea.closest('.upload-box');
    const closeButtons = document.querySelectorAll('.close-btn');
    const dateInputs = document.querySelectorAll('.date-only-picker, .hour-select, .minute-select');
    const stationInput = document.getElementById('station-input');
    const stationExamples = document.querySelectorAll('.station-example');
    const uploadAreas = document.querySelectorAll('.upload-area');
    const compareBtn = document.getElementById('compareBtn');
    const comparisonTable = document.getElementById('comparisonTable');
    const reportSection = document.getElementById('reportSection');
    const reportLoadingSection = document.getElementById('reportLoadingSection');
    const reportPopup = document.getElementById('reportPopup');
    const closeReportPopup = document.getElementById('closeReportPopup');

    // Upper Air Verification Modal
    const closeUpperAirModal = document.getElementById('closeUpperAirModal');
    const upperAirVerificationModal = document.getElementById('upperAirVerificationModal');

    // Display Graph Modal
    const displayGraphBtn = document.getElementById('DisplayGraphBtn');
    const closeDisplayGraphModal = document.getElementById('closeDisplayGraphModal');
    const displayGraphModal = document.getElementById('displayGraphModal');

    // Initialize Upper Air Verification Modal
    if (closeUpperAirModal && upperAirVerificationModal) {
        closeUpperAirModal.addEventListener('click', function() {
            upperAirVerificationModal.classList.add('hidden');
        });
        
        // Close modal when clicking outside
        upperAirVerificationModal.addEventListener('click', function(e) {
            if (e.target === upperAirVerificationModal) {
                upperAirVerificationModal.classList.add('hidden');
            }
        });
        
        // Close modal with Escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && !upperAirVerificationModal.classList.contains('hidden')) {
                upperAirVerificationModal.classList.add('hidden');
            }
        });
    }

    // Initialize Display Graph Modal
    if (displayGraphBtn && closeDisplayGraphModal && displayGraphModal) {
        console.log('Display Graph Modal elements found, setting up event listeners');
        
        displayGraphBtn.addEventListener('click', function() {
            console.log('DisplayGraphBtn clicked, showing modal');
            displayGraphModal.classList.remove('hidden');
        });
        
        closeDisplayGraphModal.addEventListener('click', function() {
            console.log('Close Display Graph Modal clicked, hiding modal');
            displayGraphModal.classList.add('hidden');
        });
        
        // Close modal when clicking outside
        displayGraphModal.addEventListener('click', function(e) {
            if (e.target === displayGraphModal) {
                console.log('Clicked outside modal, hiding modal');
                displayGraphModal.classList.add('hidden');
            }
        });
        
        // Close modal with Escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && !displayGraphModal.classList.contains('hidden')) {
                console.log('Escape key pressed, hiding modal');
                displayGraphModal.classList.add('hidden');
            }
        });
    } else {
        console.error('Display Graph Modal elements not found:', {
            displayGraphBtn: !!displayGraphBtn,
            closeDisplayGraphModal: !!closeDisplayGraphModal,
            displayGraphModal: !!displayGraphModal
        });
    }

    // Aerodrome Warning ICAO autofill
    const adwrnStationInput = document.getElementById('adwrn-station-input');
    if (adwrnStationInput) {
        // Only target station-example buttons inside the Aerodrome Warning section
        const adwrnSection = adwrnStationInput.closest('.upload-box');
        if (adwrnSection) {
            adwrnSection.querySelectorAll('.station-example').forEach(btn => {
                btn.addEventListener('click', function (e) {
                    e.preventDefault();
                    adwrnStationInput.value = this.getAttribute('data-code');
                    adwrnStationInput.dispatchEvent(new Event('input'));
                });
            });
        }
    }

    // ===== UTILITY FUNCTIONS =====

    // Format date for API
    function formatDate(date, hour, minute) {
        const d = new Date(date);
        return `${d.getFullYear()}${String(d.getMonth() + 1).padStart(2, '0')}${String(d.getDate()).padStart(2, '0')}${String(hour).padStart(2, '0')}${String(minute).padStart(2, '0')}`;
    }

    // Validate ICAO code
    function isValidICAO(code) {
        return /^[A-Z]{4}$/.test(code);
    }

    // Switch to default state (both options visible)
    function switchToDefaultState() {
        // Show both date picker and file upload
        datePickerSection.style.display = 'block';
        obsUploadArea.style.display = 'flex';
        hrLine.style.display = 'block';

        // Hide the toggle button
        toggleBtn.style.display = 'none';

        // Remove active classes
        obsUploadBox.classList.remove('file-upload-active');
        obsUploadBox.classList.remove('date-picker-active');

        // Clear any inputs
        const filePreview = obsUploadBox.querySelector('.file-preview');
        if (filePreview.style.display === 'block') {
            obsFileInput.value = '';
            filePreview.style.display = 'none';
        }
        // add hidden class to metar preview
        const metarPreview = document.querySelector('.metar-preview');
        metarPreview.classList.add('hidden');
    }

    // Check if all fields are filled and fetch METAR data
    function checkAllFieldsAndFetch() {
        const startDate = document.querySelectorAll('.date-picker-section .date-time-picker-container')[0];
        const endDate = document.querySelectorAll('.date-picker-section .date-time-picker-container')[1];
        const stationCode = stationInput.value;

        const startDateValue = startDate.querySelector('.date-only-picker').value;
        const startHour = startDate.querySelector('.hour-select').value;
        const startMinute = startDate.querySelector('.minute-select').value;

        const endDateValue = endDate.querySelector('.date-only-picker').value;
        const endHour = endDate.querySelector('.hour-select').value;
        const endMinute = endDate.querySelector('.minute-select').value;

        if (startDateValue && startHour !== '' && startMinute !== '' &&
            endDateValue && endHour !== '' && endMinute !== '' &&
            isValidICAO(stationCode)) {

            const startDateTime = formatDate(startDateValue, startHour, startMinute);
            const endDateTime = formatDate(endDateValue, endHour, endMinute);

            // Get preview elements
            const metarPreview = document.querySelector('.metar-preview');
            const previewContent = metarPreview.querySelector('.preview-content');
            const loadingIndicator = metarPreview.querySelector('.loading-indicator');

            // Show preview section and loading indicator
            metarPreview.classList.remove('hidden');
            loadingIndicator.classList.remove('hidden');
            previewContent.textContent = '';

            // Make API request
            fetch(`/api/get_metar?start_date=${startDateTime}&end_date=${endDateTime}&icao=${stationCode}`)
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(err => {
                            throw new Error(err.error || 'Failed to fetch METAR data');
                        });
                    }
                    return response.text();
                })
                .then(data => {
                    // Hide loading indicator and show data
                    loadingIndicator.classList.add('hidden');
                    previewContent.textContent = data;
                })
                .catch(error => {
                    // Hide preview section on error
                    metarPreview.classList.add('hidden');
                    console.error('Error fetching METAR data:', error);
                });
        }
    }

    // Helper functions for loading section
    function showLoadingSection() {
        reportLoadingSection.style.display = 'flex';

    }

    function hideLoadingSection() {
        reportLoadingSection.style.display = 'none';
    }

    // ===== EVENT HANDLERS =====

    // Drag and drop handlers
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight() {
        this.classList.add('border-blue-500');
        this.classList.add('bg-blue-50');
    }

    function unhighlight() {
        this.classList.remove('border-blue-500');
        this.classList.remove('bg-blue-50');
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        const fileInput = this.querySelector('input[type="file"]');

        if (files.length) {
            fileInput.files = files;
            // Trigger change event
            const event = new Event('change', { 'bubbles': true });
            fileInput.dispatchEvent(event);
        }
    }

    // ===== INITIALIZE UI =====
    initializeDatePickers();
    populateTimeSelects();

    // ===== EVENT LISTENERS =====

    // Toggle button functionality - resets to default state
    toggleBtn.addEventListener('click', function() {
        switchToDefaultState();
    });

    // File input change handler
    fileInputs.forEach(input => {
        input.addEventListener('change', function (e) {
            const file = e.target.files[0];
            console.log('File selected:', file);
            if (!file) return;

            const uploadBox = this.closest('.upload-box');
            if (!uploadBox) return;
            const previewElement = uploadBox.querySelector('.file-preview');
            const previewContent = previewElement.querySelector('.preview-content');
            const loadingIndicator = previewElement.querySelector('.loading-indicator');

            const fileNameContainer = uploadBox.querySelector('.file-name-container');
            const fileNameSpan = fileNameContainer.querySelector('span');

            // Show the file name
            fileNameSpan.textContent = file.name;

            // file name should be in the format DDMMYYYY.txt
            if (input.id === 'forecast-file-input') {
                if (!file.name.match(/^[0-9]{2}[0-9]{2}[0-9]{4}\.txt$/)) {
                    showCustomAlert('Please upload a file named with day,month and year (like 01012024.txt). The first two digits are the day and two digit for month (01-12) and the next four digits are the year.');
                    return;
                }
            }

        // For upper air observation CSV
        if (input.id === 'upperAirObsFileInput') {
            if (!file.name.toLowerCase().endsWith('.csv')) {
                showCustomAlert('Please upload a CSV file for upper air observation.');
                return;
            }
        }

        // For upper air forecast PDF
        if (input.id === 'upperAirForecastFileInput') {
            if (!file.name.toLowerCase().endsWith('.pdf')) {
                showCustomAlert('Please upload a PDF file for upper air forecast.');
                return;
            }
        }

        fileNameSpan.textContent = file.name;
        previewElement.classList.remove('hidden');
        loadingIndicator.classList.remove('hidden');
        previewContent.textContent = '';

         if (input.id === 'upperAirObsFileInput') {
            // Preview first 10 lines of CSV
            const reader = new FileReader();
            reader.onload = function (e) {
                const lines = e.target.result.split('\n');
                previewContent.textContent = lines.slice(0, 10).join('\n');
                loadingIndicator.classList.add('hidden');
            };
            reader.onerror = function () {
                loadingIndicator.classList.add('hidden');
                previewContent.textContent = 'Error reading file';
            };
            reader.readAsText(file);
        } else if (input.id === 'upperAirForecastFileInput') {
            // For PDF, just show a message
            loadingIndicator.classList.add('hidden');
            previewContent.innerHTML = '<p class="text-gray-600">PDF uploaded successfully. Upper winds data will be extracted for verification.</p>';
        } else {
            // For other files (e.g., .txt), preview the whole file
            const reader = new FileReader();
            reader.onload = function (e) {
                previewContent.textContent = e.target.result;
                loadingIndicator.classList.add('hidden');
            };
            reader.onerror = function () {
                loadingIndicator.classList.add('hidden');
                previewContent.textContent = 'Error reading file';
            };
            reader.readAsText(file);
        }

        });
    });

    // Close button functionality for file previews
    closeButtons.forEach(button => {
        button.addEventListener('click', function () {
            const previewElement = this.closest('.file-preview');
            const uploadBox = this.closest('.upload-box');
            const fileInput = uploadBox.querySelector('input[type="file"]');

            // Hide the preview
            previewElement.classList.add('hidden');

            // Reset the file input
            fileInput.value = '';

            // Reset preview content and loading state
            const previewContent = previewElement.querySelector('.preview-content');
            const loadingIndicator = previewElement.querySelector('.loading-indicator');
            previewContent.textContent = '';
            loadingIndicator.classList.add('hidden');

            // If this is the observation file input, show date picker again and hr line
            if (fileInput.classList.contains('obs-file-input')) {
                datePickerSection.style.display = 'block';
                hrLine.style.display = 'block';
                uploadBox.classList.remove('file-upload-active');
            }
        });
    });

    // Date picker inputs should hide file upload when used
    dateInputs.forEach(input => {
        input.addEventListener('change', function () {
            // Check if any date/time field has a value
            const hasDateTimeValue = Array.from(dateInputs).some(input =>
                input.value && input.value !== '');

            if (hasDateTimeValue) {
                // Hide file upload area for observation completely
                obsUploadArea.style.display = 'none';
                // Also hide the horizontal line
                hrLine.style.display = 'none';

                // Show toggle button with appropriate text
                toggleBtn.style.display = 'inline';
                obsUploadBox.classList.add('date-picker-active');

                // Check if all fields are filled and make API request
                checkAllFieldsAndFetch();
            } else {
                // Show file upload area for observation
                obsUploadArea.style.display = 'flex';
                // Show the horizontal line
                hrLine.style.display = 'block';

                // Hide toggle button
                obsUploadBox.classList.remove('date-picker-active');
            }
        });
    });

    // Station input handling - force uppercase and limit to 4 characters
    stationInput.addEventListener('input', function (e) {
        this.value = this.value.toUpperCase();
        if (this.value.length > 4) {
            this.value = this.value.slice(0, 4);
        }
    });

    // Handle example station clicks
    stationExamples.forEach(button => {
        button.addEventListener('click', function () {
            const code = this.getAttribute('data-code');
            stationInput.value = code;
            // Trigger input event to ensure any listeners are notified
            stationInput.dispatchEvent(new Event('input'));
        });
    });

    // Setup drag and drop for upload areas
    uploadAreas.forEach(area => {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            area.addEventListener(eventName, preventDefaults, false);
        });

        // Highlight drop area when file is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            area.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            area.addEventListener(eventName, unhighlight, false);
        });

        // Handle dropped files
        area.addEventListener('drop', handleDrop, false);
    });

    // event handler for compareBtn
    compareBtn.addEventListener('click', function () {
        const startDate = document.querySelectorAll('.date-picker-section .date-time-picker-container')[0];
        const endDate = document.querySelectorAll('.date-picker-section .date-time-picker-container')[1];
        const stationCode = stationInput.value;

        const startDateValue = startDate.querySelector('.date-only-picker').value;
        const startHour = startDate.querySelector('.hour-select').value;
        const startMinute = startDate.querySelector('.minute-select').value;

        const endDateValue = endDate.querySelector('.date-only-picker').value;
        const endHour = endDate.querySelector('.hour-select').value;
        const endMinute = endDate.querySelector('.minute-select').value;

        // get forecast file
        const forecastFile = document.querySelector('.forecast-file-input').files[0];
        // get observation file
        const observationFile = document.querySelector('.obs-file-input').files[0];

        // if icao is null
        if (!isValidICAO(stationCode)) {
            showCustomAlert('Please enter a valid ICAO code.');
            return;
        }

        // check if forecast file is present and it should be in the format DDMMYYYY.txt
    //    if (!file.name.match(/^\d{2}\d{2}\d{4}\.txt$/)) {
    //         showCustomAlert('Please upload a valid forecast file in the format DDMMYYYY.txt.');
    //         return;
    //     }

        if (
            (
                (startDateValue && startHour !== '' && startMinute !== '' &&
                    endDateValue && endHour !== '' && endMinute !== '' &&
                    isValidICAO(stationCode))
                || observationFile
            ) && forecastFile
        ) {

            // if obs file, then start and end date time is none, else get the date time, and have obs file as none
            const startDateTime = observationFile ? '' : formatDate(startDateValue, startHour, startMinute);
            const endDateTime = observationFile ? '' : formatDate(endDateValue, endHour, endMinute);

            // Create FormData object for multipart/form-data request
            const formData = new FormData();
            formData.append('start_date', startDateTime);
            formData.append('end_date', endDateTime);
            formData.append('icao', stationCode);
            formData.append('forecast_file', forecastFile);
            formData.append('observation_file', observationFile);

            // Make API request to process METAR data
            showLoadingSection(); // Show loading before fetch
            fetch('/api/process_metar', {
                method: 'POST',
                body: formData
            })
                .then(response => {
                    if (!response.ok) {
                        hideLoadingSection(); // Hide loading on error
                        return response.json().then(err => {
                            throw new Error(err.error || 'Failed to process METAR data');
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    hideLoadingSection(); // Hide loading on success
                    console.log('METAR data processed successfully:', data);

                    // Get the encoded paths for the CSV files
                    const comparisonEncodedPath = data.file_paths.comparison_csv;
                    const detailedComparisonEncodedPath = data.file_paths.merged_csv;
                    const downloadUrl = `/api/download/comparison_csv?file_path=${comparisonEncodedPath}`;
                    const detailedDownloadUrl = `/api/download/merged_csv?file_path=${detailedComparisonEncodedPath}`;

                    const metadata = data.metadata;
                    const metarReportTitle = document.getElementById('metarReportTitle');

                    document.getElementById("downloadCsvBtn").href = 
    `/api/download/comparison_csv?file_path=${data.file_paths.comparison_csv}`;

 document.getElementById('upperAirForecastFileInput').addEventListener('change', async function (e) {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = async function () {
          const typedarray = new Uint8Array(this.result);

          const pdf = await pdfjsLib.getDocument({ data: typedarray }).promise;
          let fullText = '';

          for (let i = 1; i <= pdf.numPages; i++) {
            const page = await pdf.getPage(i);
            const textContent = await page.getTextContent();
            const pageText = textContent.items.map(item => item.str).join(' ');
            fullText += pageText + '\n';
          }

          // Extract "UPPER WINDS" block
          const upperWindsBlock = fullText.match(/UPPER WINDS([\s\S]+?)WEATHER/i);
          if (!upperWindsBlock) return alert("No 'Upper Winds' data found.");

          const cleanedText = upperWindsBlock[1].replace(/[\=]/g, '').trim();
          const dataArray = cleanedText.split(/\s+/);

          // Convert into rows of 3 (Altitude, Dir/Speed, Temp)
          const table = document.getElementById("windTable");
          const tbody = table.querySelector("tbody");
          tbody.innerHTML = "";
          for (let i = 0; i < dataArray.length; i += 6) {
            const row = document.createElement("tr");
            for (let j = 0; j < 6; j++) {
              const cell = document.createElement("td");
              cell.textContent = dataArray[i + j] || "";
              row.appendChild(cell);
            }
            tbody.appendChild(row);
          }

          table.style.display = "table";
        };

        reader.readAsArrayBuffer(file);
      });

                    let update_string = `VERIFICATION RESULT OF TAKE-OFF FORECAST <br> ${metadata.icao}`
                    if (metadata.start_time && metadata.end_time) {
                        update_string += ` <br> ${metadata.start_time} TO ${metadata.end_time}`;
                    }
                    metarReportTitle.innerHTML = update_string;

                    // Fetch CSV and extract warning percentages
                    fetch(downloadUrl)
                        .then(response => {
                            if (!response.ok) {
                                throw new Error('Failed to download comparison CSV');
                            }
                            return response.text();
                        })
                        .then(csvText => {

                             const lines = csvText.split("\n");
                            const cleanedCsv = lines.slice(1).join("\n");
                            // Get the detailed comparison table
                            const detailedComparisonTable = document.getElementById('comparisonTable');
                            populateTableFromCSV(cleanedCsv, detailedComparisonTable);
                            
                            // Show report section after both tables are populated
                            const reportPopup = document.getElementById('reportPopup');
                            const reportSection = document.getElementById('reportSection');
                            reportSection.style.display = 'block';
                            reportPopup.classList.remove('hidden');
                            reportPopup.classList.add('flex');
                        })
                        .catch(error => {
                            hideLoadingSection(); // Hide loading on error
                            console.error('Error downloading CSV data:', error);
                            showCustomAlert('Failed to load comparison data. Please try again.');
                        });
                })
                .catch(error => {
                    hideLoadingSection(); // Hide loading on error
                    console.error('Error processing METAR data:', error);
                    showCustomAlert('Error processing METAR data. Please try again.');
                });
        } else {

            // Show validation error message
            showCustomAlert('Please fill in all required fields and upload a forecast file.');
        }
    });

    // Close popup functionality
    closeReportPopup.addEventListener('click', function() {
        reportPopup.classList.add('hidden');
        reportPopup.classList.remove('flex');
    });
    
    // Close popup when clicking outside the modal content
    reportPopup.addEventListener('click', function(e) {
        if (e.target === reportPopup) {
            reportPopup.classList.add('hidden');
            reportPopup.classList.remove('flex');
        }
    });
    
    // Close popup with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && !reportPopup.classList.contains('hidden')) {
            reportPopup.classList.add('hidden');
            reportPopup.classList.remove('flex');
        }
    });
    document.getElementById("DisplayGraphBtn").addEventListener("click", () => {
    // Open the chart in a new browser tab
    window.open("/api/accuracy_chart?metric=Overall", "_blank");
});

});


// Add this JavaScript code to your existing app.js file

// Upper Air specific variables (add to existing element references section)
// 
// Element references
const upperAirStationInput = document.getElementById('upperAirStationInput');
const upperAirStationExamples = document.querySelectorAll('.upper-air-station-example');
const upperAirObsFileInput = document.getElementById('upperAirObsFileInput');
const upperAirObsUploadArea = document.getElementById('upperAirObsUploadArea');
const upperAirObsFilePreview = document.getElementById('upperAirObsFilePreview');
const upperAirDatePickerSection = document.getElementById('upperAirDatePickerSection');
const upperAirDatePicker = document.getElementById('upperAirDatePicker');
const upperAirHourSelect = document.getElementById('upperAirHourSelect');
// const upperAirFetchBtn = document.getElementById('upperAirFetchBtn');
const upperAirPreviewSection = document.getElementById('upperAirPreviewSection');
const upperAirPreviewContent = document.getElementById('upperAirPreviewContent');
const upperAirLoadingIndicator = document.getElementById('upperAirLoadingIndicator');
const upperAirForecastFileInput = document.getElementById('upperAirForecastFileInput');
const upperAirForecastUploadArea = document.getElementById('upperAirForecastUploadArea');
const upperAirForecastFilePreview = document.getElementById('upperAirForecastFilePreview');
const upperAirVerifyBtn = document.getElementById('upperAirVerifyBtn');
const upperAirReportSection = document.getElementById('upperAirReportSection');


// Populate hour select
for (let i = 0; i < 24; i++) {
    const option = document.createElement('option');
    option.value = i.toString().padStart(2, '0');
    option.textContent = i.toString().padStart(2, '0');
    upperAirHourSelect.appendChild(option);
}

// Date picker
flatpickr(upperAirDatePicker, {
    enableTime: false,
    dateFormat: "Y-m-d",
    static: true
});

upperAirStationExamples.forEach(btn => {
    btn.addEventListener('click', function () {
        upperAirStationInput.value = this.getAttribute('data-code');
    });
});

// Observation file upload
upperAirObsFileInput.addEventListener('change', function () {
    const file = this.files[0];
    if (!file) return;
    if (!file.name.endsWith('.csv')) {
        showCustomAlert('Please upload a CSV file for upper air observation.');
        return;
    }
    upperAirObsFilePreview.querySelector('.file-name-container span').textContent = file.name;
    upperAirObsFilePreview.classList.remove('hidden');
    const previewContent = upperAirObsFilePreview.querySelector('.preview-content');
    const loadingIndicator = upperAirObsFilePreview.querySelector('.loading-indicator');
    loadingIndicator.classList.remove('hidden');
    previewContent.textContent = '';
    const reader = new FileReader();
    reader.onload = function (e) {
        const lines = e.target.result.split('\n');
        previewContent.textContent = lines.slice(0, 10).join('\n');
        loadingIndicator.classList.add('hidden');
    };
    reader.onerror = function () {
        loadingIndicator.classList.add('hidden');
        previewContent.textContent = 'Error reading file';
    };
    reader.readAsText(file);
    // Hide date picker section
    upperAirDatePickerSection.style.display = 'none';
});

// Close button for obs preview
upperAirObsFilePreview.querySelector('.close-btn').addEventListener('click', function () {
    upperAirObsFilePreview.classList.add('hidden');
    upperAirObsFileInput.value = '';
    upperAirDatePickerSection.style.display = 'block';
});

// Forecast file upload
upperAirForecastFileInput.addEventListener('change', function () {
    const file = this.files[0];
    if (!file) return;
    if (!file.name.endsWith('.pdf')) {
        showCustomAlert('Please upload a PDF file for upper air forecast.');
        return;
    }
    upperAirForecastFilePreview.querySelector('.file-name-container span').textContent = file.name;
    upperAirForecastFilePreview.classList.remove('hidden');
    const previewContent = upperAirForecastFilePreview.querySelector('.preview-content');
    const loadingIndicator = upperAirForecastFilePreview.querySelector('.loading-indicator');
    loadingIndicator.classList.remove('hidden');
    previewContent.textContent = '';
    if (file.type === 'application/pdf') {
        loadingIndicator.classList.add('hidden');
        previewContent.innerHTML = '<p class="text-gray-600">PDF uploaded successfully. Upper winds data will be extracted for verification.</p>';
    } else {
        loadingIndicator.classList.add('hidden');
        previewContent.textContent = 'Please upload a PDF file.';
    }
});

 document.getElementById('upperAirForecastFileInput').addEventListener('change', async function (e) {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = async function () {
          const typedarray = new Uint8Array(this.result);

          const pdf = await pdfjsLib.getDocument({ data: typedarray }).promise;
          let fullText = '';

          for (let i = 1; i <= pdf.numPages; i++) {
            const page = await pdf.getPage(i);
            const textContent = await page.getTextContent();
            const pageText = textContent.items.map(item => item.str).join(' ');
            fullText += pageText + '\n';
          }

          // Extract "UPPER WINDS" block
          const upperWindsBlock = fullText.match(/UPPER WINDS([\s\S]+?)WEATHER/i);
          if (!upperWindsBlock) return alert("No 'Upper Winds' data found.");

          const cleanedText = upperWindsBlock[1].replace(/[\=]/g, '').trim();
          const dataArray = cleanedText.split(/\s+/);

          // Convert into rows of 3 (Altitude, Dir/Speed, Temp)
          const table = document.getElementById("windTable");
          const tbody = table.querySelector("tbody");
          tbody.innerHTML = "";
          for (let i = 0; i < dataArray.length; i += 6) {
            const row = document.createElement("tr");
            for (let j = 0; j < 6; j++) {
              const cell = document.createElement("td");
              cell.textContent = dataArray[i + j] || "";
              row.appendChild(cell);
            }
            tbody.appendChild(row);
          }

          table.style.display = "table";
        };

        reader.readAsArrayBuffer(file);
      });


// Close button for forecast preview
upperAirForecastFilePreview.querySelector('.close-btn').addEventListener('click', function () {
    upperAirForecastFilePreview.classList.add('hidden');
    upperAirForecastFileInput.value = '';
});

// Fetch observation data from Wyoming
// upperAirFetchBtn.addEventListener('click', function () {
//     const date = upperAirDatePicker.value;
//     const hour = upperAirHourSelect.value;
//     const station = upperAirStationInput.value;
//     if (!date || !hour || !/^\d{5}$/.test(station)) {
//         if (typeof showCustomAlert === 'function') {
//             showCustomAlert('Please select date, hour, and enter a valid 5-digit station ID.');
//         } else {
//             alert('Please select date, hour, and enter a valid 5-digit station ID.');
//         }
//         return;
//     }
//     upperAirPreviewSection.classList.remove('hidden');
//     upperAirLoadingIndicator.classList.remove('hidden');
//     upperAirPreviewContent.textContent = '';
//     const dateTime = `${date} ${hour}:00:00`;
//     fetch(`/api/get_upper_air?datetime=${encodeURIComponent(dateTime)}&station_id=${station}`)
//         .then(async response => {
//             upperAirLoadingIndicator.classList.add('hidden');
//             if (!response.ok) {
//                 // Try to parse error JSON
//                 let errorMsg = 'Failed to fetch upper air data';
//                 try {
//                     const err = await response.json();
//                     errorMsg = err.error || errorMsg;
//                 } catch (e) {}
//                 throw new Error(errorMsg);
//             }
//             const text = await response.text();
//             // If the response looks like HTML, show a friendly error
//             if (text.trim().toLowerCase().startsWith('<!doctype html') || text.trim().toLowerCase().startsWith('<html')) {
//                 throw new Error('No data available for the selected date/time/station.');
//             }
//             upperAirPreviewContent.textContent = text;
//         })
//         .catch(error => {
//             upperAirPreviewSection.classList.add('hidden');
//             if (typeof showCustomAlert === 'function') {
//                 showCustomAlert('Error fetching upper air data: ' + error.message);
//             } else {
//                 alert('Error fetching upper air data: ' + error.message);
//             }
//         });
// });

// Verification (submit)
// Replace your current upperAirVerifyBtn click handler with this:
upperAirVerifyBtn.addEventListener('click', function () {
    const station = upperAirStationInput.value;
    const forecastFile = upperAirForecastFileInput.files[0];
    const obsFile = upperAirObsFileInput.files[0];
    const date = upperAirDatePicker.value;
    const hour = upperAirHourSelect.value;
    // const tempValue = document.getElementById('upperAirTempInput').value; // <-- get temp

    if (!/^\d{5}$/.test(station)) {
        alert('Please enter a valid 5-digit station ID.');
        return;
    }
    if (!forecastFile || forecastFile.type !== 'application/pdf') {
        alert('Please upload a valid PDF forecast file.');
        return;
    }
    if (!obsFile && (!date || !hour)) {
        alert('Please either upload an observation CSV or select date/time to fetch data.');
        return;
    }

    const formData = new FormData();
    formData.append('station_id', station);
    formData.append('forecast_file', forecastFile);
    if (obsFile) {
        formData.append('observation_file', obsFile);
    } else {
        const dateTime = `${date} ${hour}:00:00`;
        formData.append('datetime', dateTime);
    }
    // if (tempValue !== '') {
    //     formData.append('reference_temp', tempValue); // <-- send temp to backend
    // }

    // Show loading, hide report
    upperAirReportSection.style.display = 'none';

    fetch('/api/process_upper_air', {
        method: 'POST',
        body: formData
    })
        .then(response => {
            if (!response.ok) return response.json().then(err => { throw new Error(err.error || 'Failed to process upper air data'); });
            return response.json();
        })
        .then(data => {
            // Show popup modal instead of results section
            const modal = document.getElementById('upperAirVerificationModal');
            modal.classList.remove('hidden');

            // Set metadata
            const metaData = data.metadata;
            const metadata_start_time = metaData.start_time;
            const metadata_end_time = metaData.end_time;
            const metadata_station_id = metaData.station_id;
            const metadata_icao = metaData.icao;
            document.getElementById('upperAirReportTitle').innerHTML = `UPPER AIR FORECAST VERIFICATION RESULTS FOR ${metadata_station_id} (${metadata_icao}) <br> FROM ${metadata_start_time} TO ${metadata_end_time}`;

            // Set accuracy values
            document.getElementById('tempAccuracy').textContent = data.temp_accuracy !== undefined ? `${data.temp_accuracy}%` : '--';
            document.getElementById('windAccuracy').textContent = data.wind_accuracy !== undefined ? `${data.wind_accuracy}%` : '--';
            document.getElementById('windDirAccuracy').textContent = data.wind_dir_accuracy !== undefined ? `${data.wind_dir_accuracy}%` : '--';
            document.getElementById('weatherAccuracy').textContent = data.weather_accuracy !== undefined ? `${data.weather_accuracy}%` : '--';

            // Fetch and populate the verification table
//             if (data.file_path) {
//                 fetch(`/api/download/upper_air_csv?file_path=${encodeURIComponent(data.file_path)}`)
//                     .then(response => {
//                         if (!response.ok) throw new Error('Failed to download verification CSV');
//                         return response.text();
//                     })
//                     .then(csvText => {
//                         populateUpperAirVerificationTable(csvText);
//                     })
//                     .catch(error => {
//                         showCustomAlert('Failed to load verification data. Please try again.');
//                     });

//                 // Set download button
//                 const downloadBtn = document.querySelector('#upperAirReportSection #downloadCsvBtn');
// if (downloadBtn && data.file_path.endsWith('.xlsx')) {
//     downloadBtn.href = `/api/download/upper_air_csv?file_path=${encodeURIComponent(data.file_path)}`;
//     downloadBtn.textContent = "Download XLSX Report";
// }

//             }

    const tableBody = document.getElementById('upperAirTableBody');
    tableBody.innerHTML = ''; // Clear previous data

    data.data.forEach((row, index) => {
        console.log('Processing row:', row);
        const rowKey = `${row.date}_${row.validity}`;
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td class="border px-2 py-1">${row.date}</td>
            <td class="border px-2 py-1">${row.validity}</td>
            <td class="border px-2 py-1">${row.fl}</td>
            <td class="border px-2 py-1">${row.forecast_wind_dir}</td>
            <td class="border px-2 py-1">${row.forecast_speed}</td>
            <td class="border px-2 py-1">${row.forecast_temp}</td>
            <td class="border px-2 py-1">${row.actual_wind_dir}</td>
            <td class="border px-2 py-1">${row.actual_speed}</td>
            <td class="border px-2 py-1">${row.actual_temp}</td>
            <td class="border px-2 py-1">${row.wind_dir_acc}</td>
            <td class="border px-2 py-1">${row.speed_acc}</td>
            <td class="border px-2 py-1">${row.temp_acc}</td>
        `;
        tableBody.appendChild(tr);

         const nextRow = data.data[index + 1];
    const nextKey = nextRow ? `${nextRow.date}_${nextRow.validity}` : null;

    if (rowKey !== nextKey) {
        const weatherTr = document.createElement('tr');
        const forecast = row.weather_forecast || 'N/A';
        const realised = Array.isArray(row.weather_matched) ? row.weather_matched.join(" / ") : 'None';
        const accuracy = row.weather_acc || 'N/A';
        weatherTr.innerHTML = `
            <td class="border px-2 py-1">${row.date}</td>
            <td class="border px-2 py-1">${row.validity}</td>
            <td class="border px-2 py-1 font-bold text-blue-600">Significant Weather</td>
            <td class="border px-2 py-1" colspan="3">${forecast}</td>
            <td class="border px-2 py-1" colspan="3">${realised}</td>
            <td class="border px-2 py-1 font-semibold" colspan="3">${accuracy}</td>
        `;
        tableBody.appendChild(weatherTr);
    }
    });

    // Set download button
    const downloadBtn = document.querySelector('#upperAirVerificationModal #downloadCsvBtn');
    if (downloadBtn && data.file_path && data.file_path.endsWith('.xlsx')) {
        downloadBtn.href = `/api/download/upper_air_csv?file_path=${encodeURIComponent(data.file_path)}`;
        // downloadBtn.textContent = "Download XLSX Report";
        downloadBtn.style.display = 'inline-block';
    }
        })
        .catch(error => {
            alert('Error processing upper air data: ' + error.message);
        });
});

// Helper function to populate the verification table
function populateUpperAirVerificationTable(csvText) {
    const table = document.getElementById('verificationTable');
    if (!table) return;
    const rows = csvText.trim().split('\n');
    const headers = rows[0].split(',');

    // Clear thead and tbody
    const thead = table.querySelector('thead');
    const tbody = table.querySelector('tbody');
    if (thead) thead.innerHTML = '';
    if (tbody) tbody.innerHTML = '';

    // Populate header
    const headerRow = document.createElement('tr');
    headers.forEach(header => {
        const th = document.createElement('th');
        th.textContent = header.replace(/_/g, ' ');
        th.className = 'px-6 py-3 text-left text-xs font-medium text-gray-800 uppercase tracking-wider';
        headerRow.appendChild(th);
    });
    if (thead) thead.appendChild(headerRow);

    // Populate body
    for (let i = 1; i < rows.length; i++) {
        if (rows[i].trim() === '') continue;
        const rowData = rows[i].split(',');
        const tr = document.createElement('tr');
        tr.className = 'transition-colors duration-150 ease-in-out';
        rowData.forEach(cell => {
            const td = document.createElement('td');
            td.textContent = cell;
            td.className = 'px-6 py-4 text-sm border-b border-gray-200';
            tr.appendChild(td);
        });
        if (tbody) tbody.appendChild(tr);
    }
}

function setupDragAndDrop(uploadAreaId, fileInputId, fileType) {
    const uploadArea = document.getElementById(uploadAreaId);
    const fileInput = document.getElementById(fileInputId);

    if (!uploadArea || !fileInput) return;

    // Highlight on drag over
    uploadArea.addEventListener('dragover', function (e) {
        e.preventDefault();
        uploadArea.classList.add('border-blue-500', 'bg-blue-50');
    });

    uploadArea.addEventListener('dragleave', function (e) {
        e.preventDefault();
        uploadArea.classList.remove('border-blue-500', 'bg-blue-50');
    });

    uploadArea.addEventListener('drop', function (e) {
        e.preventDefault();
        uploadArea.classList.remove('border-blue-500', 'bg-blue-50');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            // Validate file type
            if (fileType === 'csv' && !file.name.toLowerCase().endsWith('.csv')) {
                showCustomAlert('Please upload a CSV file for upper air observation.');
                return;
            }
            if (fileType === 'pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
                showCustomAlert('Please upload a PDF file for upper air forecast.');
                return;
            }
            // Set the file to the input and trigger change event
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            fileInput.files = dataTransfer.files;
            fileInput.dispatchEvent(new Event('change'));
        }
    });

    // Optional: clicking the area opens the file dialog
    uploadArea.addEventListener('click', function () {
        fileInput.click();
    });
}


//Nav Bar
const showDisplay = (index) => {
            const displays = document.querySelectorAll('.display')
            const button = document.querySelectorAll('.tab-button')

            displays.forEach((display,i)=>{
                display.classList.toggle('active', i === index)
            })

            button.forEach((btn,i)=>{
                btn.classList.toggle('active', i===index)
            })
        }



// Setup drag and drop for both areas
setupDragAndDrop('upperAirObsUploadArea', 'upperAirObsFileInput', 'csv');
setupDragAndDrop('upperAirForecastUploadArea', 'upperAirForecastFileInput', 'pdf');

// === Aerodrome Warning AJAX Fetch & Verify ===
const adwrnForm = document.getElementById('adwrn-form');
const adwrnMessage = document.getElementById('adwrn-message');
const adwrnMetarPreview = document.getElementById('adwrn-metar-preview');
const adwrnFetchBtn = document.getElementById('adwrn-fetch-btn');
if (adwrnForm && adwrnMessage && adwrnMetarPreview && adwrnFetchBtn) {
    let isResetMode = false;
    
    // Add click event listener to the fetch button
    adwrnFetchBtn.addEventListener('click', function(e) {
        e.preventDefault();
        // Trigger form submission
        adwrnForm.dispatchEvent(new Event('submit'));
    });
    
    adwrnForm.addEventListener('submit', function(e) {
        e.preventDefault();
        if (isResetMode) {
            // Reset all date/time fields
            adwrnForm.querySelectorAll('.date-only-picker').forEach(input => input.value = '');
            adwrnForm.querySelectorAll('.hour-select').forEach(select => select.selectedIndex = 0);
            adwrnForm.querySelectorAll('.minute-select').forEach(select => select.selectedIndex = 0);
            adwrnMetarPreview.style.display = 'none';
            adwrnMetarPreview.textContent = '';
            adwrnMessage.textContent = '';
            adwrnFetchBtn.textContent = 'Fetch';
            adwrnFetchBtn.classList.remove('bg-gray-500');
            adwrnFetchBtn.classList.add('bg-blue-600','hover:bg-blue-700');
            
            // Show upload area and remove disabled state
            const uploadArea = document.querySelector('.adwrn-obs-file-input').closest('.upload-area');
            uploadArea.classList.remove('opacity-50', 'pointer-events-none');
            uploadArea.querySelector('input[type="file"]').disabled = false;
            
            // Hide error message
            const errorDiv = document.getElementById('adwrn-fetch-error');
            if (errorDiv) errorDiv.classList.add('hidden');
            
            isResetMode = false;
            return;
        }
        
        // Validation: Check required fields
        console.log('Validating aerodrome fetch fields...');
        const stationCode = document.getElementById('adwrn-station-input').value.trim();
        const startDate = adwrnForm.querySelector('input[name="start_date"]').value.trim();
        const endDate = adwrnForm.querySelector('input[name="end_date"]').value.trim();
        const errorDiv = document.getElementById('adwrn-fetch-error');
        const errorMessage = document.getElementById('adwrn-error-message');
        
        console.log('Station code:', stationCode);
        console.log('Start date:', startDate);
        console.log('End date:', endDate);
        
        let validationErrors = [];
        
        if (!stationCode) {
            validationErrors.push("Station code (ICAO INDEX)");
        }
        if (!startDate) {
            validationErrors.push("Start date");
        }
        if (!endDate) {
            validationErrors.push("End date");
        }
        
        if (validationErrors.length > 0) {
            console.log('Validation errors found:', validationErrors);
            const errorText = `Please fill in the following required fields: ${validationErrors.join(', ')}.`;
            if (errorMessage) errorMessage.textContent = errorText;
            if (errorDiv) errorDiv.classList.remove('hidden');
            console.log('Error message shown');
            return; // Stop execution here
        }
        
        console.log('Validation passed');
        // Hide error message if validation passes
        if (errorDiv) errorDiv.classList.add('hidden');
        
        adwrnMessage.textContent = '';
        adwrnMetarPreview.style.display = 'none';
        adwrnMetarPreview.textContent = '';
        
        // Show loading indicator
        const loadingIndicator = document.getElementById('fetch-loading-indicator');
        loadingIndicator.classList.remove('hidden');
        adwrnFetchBtn.disabled = true;
        adwrnFetchBtn.classList.add('opacity-50', 'cursor-not-allowed');
        
        const formData = new FormData(adwrnForm);
        fetch('/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Hide loading indicator
            loadingIndicator.classList.add('hidden');
            adwrnFetchBtn.disabled = false;
            adwrnFetchBtn.classList.remove('opacity-50', 'cursor-not-allowed');
            
            adwrnMessage.innerHTML = `<span class='text-green-700'>${data.message}</span>`;
            if (data.metar_preview) {
                adwrnMetarPreview.textContent = data.metar_preview;
                adwrnMetarPreview.style.display = 'block';
                adwrnFetchBtn.textContent = 'Reset';
                adwrnFetchBtn.classList.remove('bg-blue-600','hover:bg-blue-700');
                adwrnFetchBtn.classList.add('bg-gray-500');
                
                // Disable and fade out the upload area
                const uploadArea = document.querySelector('.adwrn-obs-file-input').closest('.upload-area');
                uploadArea.classList.add('opacity-50', 'pointer-events-none');
                uploadArea.querySelector('input[type="file"]').disabled = true;
                
                isResetMode = true;
            }
        })
        .catch(error => {
            // Hide loading indicator
            loadingIndicator.classList.add('hidden');
            adwrnFetchBtn.disabled = false;
            adwrnFetchBtn.classList.remove('opacity-50', 'cursor-not-allowed');
            
            adwrnMessage.innerHTML = `<span class='text-red-700'>Error: ${error.message}</span>`;
        });
    });
}

// === ADWRN Forecast File Upload & Preview ===
document.querySelectorAll('.adwrn-forecast-file-input').forEach(input => {
    input.addEventListener('change', function() {
        const file = this.files[0];
        const uploadBox = this.closest('.upload-box');
        const previewElement = uploadBox.querySelector('.file-preview');
        const previewContent = previewElement.querySelector('.preview-content');
        const loadingIndicator = previewElement.querySelector('.loading-indicator');
        const fileNameContainer = uploadBox.querySelector('.file-name-container');
        const fileNameSpan = fileNameContainer.querySelector('span');

        if (!file) return;
        fileNameSpan.textContent = file.name;
        previewElement.classList.remove('hidden');
        loadingIndicator.classList.remove('hidden');
        previewContent.textContent = '';

        // Prepare FormData and send to backend
        const formData = new FormData();
        formData.append('file', file);
        fetch('/api/upload_ad_warning', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            loadingIndicator.classList.add('hidden');
            if (data.preview) {
                previewContent.textContent = data.preview;
            } else if (data.error) {
                previewContent.textContent = 'Error: ' + data.error;
            } else {
                previewContent.textContent = 'No preview available.';
            }
        })
        .catch(err => {
            loadingIndicator.classList.add('hidden');
            previewContent.textContent = 'Error uploading file.';
        });
    });
});

// === ADWRN Final Warning Report Verification ===
const adwrnVerifyBtn = document.getElementById('adwrn-verifyBtn');
const adwrnReportLoadingSection = document.getElementById('adwrn-reportLoadingSection');






// Function to download Excel report with station name, validity period, and accuracy
function downloadExcel() {
    console.log('Download button clicked');
    
    const stationInput = document.getElementById('adwrn-station-input');
    const startDateInput = document.querySelector('input[name="start_date"]');
    const endDateInput = document.querySelector('input[name="end_date"]');
    const accuracyElement = document.getElementById('adwrn-accuracy');
    
    // Get station name
    const stationName = stationInput ? stationInput.value.toUpperCase() : 'UNKNOWN';
    
    // Get validity period - check if user uploaded a file or used date pickers
    let validityPeriod = 'unknown_period';
    const datePickerSection = document.querySelector('.date-picker-section');
    const isDatePickerDisabled = datePickerSection && datePickerSection.classList.contains('opacity-50');
    
    if (!isDatePickerDisabled && startDateInput && endDateInput) {
        const startDate = startDateInput.value;
        const endDate = endDateInput.value;
        if (startDate && endDate) {
            validityPeriod = `${startDate}_to_${endDate}`;
        }
    } else {
        // User uploaded a file, use current date as validity period
        const today = new Date().toISOString().split('T')[0];
        validityPeriod = `${today}_file_upload`;
    }
    
    // Get accuracy percentage
    let accuracyPercent = '0';
    if (accuracyElement && accuracyElement.textContent) {
        const accuracyMatch = accuracyElement.textContent.match(/(\d+(?:\.\d+)?)%/);
        if (accuracyMatch) {
            accuracyPercent = accuracyMatch[1];
        }
    }
    
    // Create filename
    const filename = `${stationName}_Aerodrome_Warning_${validityPeriod}_${accuracyPercent}%_accuracy.csv`;
    console.log('Attempting to download:', filename);
    
    // Show loading state
    const downloadBtn = document.querySelector('#adwrn-download-container button, #adwrn-download-report-btn');
    if (downloadBtn) {
        const originalText = downloadBtn.innerHTML;
        downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Downloading...';
        downloadBtn.disabled = true;
        
        // Reset button after 3 seconds regardless of outcome
        setTimeout(() => {
            downloadBtn.innerHTML = originalText;
            downloadBtn.disabled = false;
        }, 3000);
    }
    
    // Fetch the CSV data and trigger download
    fetch('/api/download/adwrn_report')
        .then(response => {
            console.log('Download response status:', response.status);
            if (!response.ok) {
                return response.json().then(errData => {
                    throw new Error(errData.error || 'Failed to download report');
                });
            }
            return response.blob();
        })
        .then(blob => {
            console.log('Download blob received, size:', blob.size);
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.style.display = 'none';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            console.log('Download completed successfully');
        })
        .catch(error => {
            console.error('Download error:', error);
            showCustomAlert('Error downloading report: ' + error.message);
        });
}

if (adwrnVerifyBtn && adwrnReportLoadingSection) {
    adwrnVerifyBtn.addEventListener('click', function() {
        console.log('Verify button clicked'); // Debug log
        
        // Hide any existing modals or containers
        const modal = document.getElementById('adwrnResultsModal');
        if (modal) modal.style.display = 'none';
        
        adwrnReportLoadingSection.style.display = 'flex';
        fetch('/api/adwrn_verify', { method: 'POST' })
            .then(response => {
                console.log('Response status:', response.status); // Debug log
                return response.json();
            })
            .then(data => {
                console.log('Response data:', data); // Debug log
                adwrnReportLoadingSection.style.display = 'none';
                if (data.success) {
                    // Extract accuracy percentages from the data
                    const detailedAccuracy = data.detailed_accuracy || {};
                    console.log("Detailed accuracy from API:", detailedAccuracy);
                    
                    // Update modal content with accuracy percentages
                    const thunderstormPercent = document.getElementById('adwrn-thunderstorm-percent');
                    const gustPercent = document.getElementById('adwrn-gust-percent');
                    const stationInfo = document.getElementById('adwrn-modal-station-info');
                    const stationInfoText = stationInfo.querySelector('p');
                    
                    if (thunderstormPercent) {
                        const thunderstormValue = detailedAccuracy.thunderstorm;
                        thunderstormPercent.textContent = thunderstormValue !== undefined ? `${thunderstormValue}%` : '--%';
                    }
                    if (gustPercent) {
                        const windValue = detailedAccuracy.wind;
                        gustPercent.textContent = windValue !== undefined ? `${windValue}%` : '--%';
                    }
                    
                    // Show station info if available
                    if (data.station_info && stationInfo && stationInfoText) {
                        stationInfoText.textContent = data.station_info;
                        stationInfo.style.display = 'block';
                    } else if (stationInfo) {
                        stationInfo.style.display = 'none';
                    }
                    
                                         // Set up download button functionality
                     const modalDownloadBtn = document.getElementById('adwrn-modal-download-btn');
                     if (modalDownloadBtn) {
                         modalDownloadBtn.onclick = function(e) {
                             e.preventDefault();
                             downloadAerodromeWarningsTable();
                         };
                     }
                     
                     // Set up view graph button functionality
                     const viewGraphBtn = document.getElementById('adwrn-view-graph-btn');
                     if (viewGraphBtn) {
                         viewGraphBtn.onclick = function(e) {
                             e.preventDefault();
                             
                             // Prevent multiple clicks
                             if (viewGraphBtn.disabled) return;
                             
                             // Show loading state
                             const originalText = viewGraphBtn.textContent;
                             viewGraphBtn.textContent = 'Generating Chart...';
                             viewGraphBtn.disabled = true;
                             
                             // Open combined chart in a new tab via Flask route
                             window.open('/bar_chart', '_blank');
                             
                             // Reset button state after a short delay
                             setTimeout(() => {
                                 viewGraphBtn.textContent = originalText;
                                 viewGraphBtn.disabled = false;
                             }, 2000);
                         };
                     }
                    
                    // Show the modal
                    if (modal) {
                        modal.style.display = 'flex';
                    }
                    
                } else {
                    console.log('Validation failed:', data); // Debug log
                    // Handle validation errors with more specific messaging
                    if (data.validation_failed) {
                        let errorMessage = data.error;
                        
                        // Add more context for station code mismatch
                        if (data.error && data.error.includes('Station code mismatch')) {
                            errorMessage = `${data.error}\n\nPlease ensure both files are for the same station.`;
                        }
                        
                        // Add more context for date range issues
                        if (data.error && data.error.includes('No METAR data falls within the valid warning period')) {
                            errorMessage = `${data.error}\n\nPlease check that the METAR data covers the warning period and that the warning file contains a valid issue date.`;
                        }
                        
                        console.log('Showing validation error:', errorMessage); // Debug log
                        showCustomAlert(errorMessage);
                    } else {
                        console.log('Showing general error:', data.error); // Debug log
                        showCustomAlert(data.error || 'Verification failed.');
                    }
                }
            })
            .catch(err => {
                console.log('Fetch error:', err); // Debug log
                adwrnReportLoadingSection.style.display = 'none';
                showCustomAlert('Error: ' + err.message);
            });
    });
}

// Add event listeners for the modal
document.addEventListener('DOMContentLoaded', function() {
    // Add event listener for the modal close button
    const closeModalBtn = document.getElementById('adwrn-close-modal');
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', function() {
            const modal = document.getElementById('adwrnResultsModal');
            if (modal) {
                modal.style.display = 'none';
            }
        });
    }
    
    // Close modal when clicking outside of it
    const modal = document.getElementById('adwrnResultsModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    }
});



// Function to download aerodrome warnings table
function downloadAerodromeWarningsTable() {
    console.log('Aerodrome warnings table download button clicked');
    
    const stationInput = document.getElementById('adwrn-station-input');
    const startDateInput = document.querySelector('input[name="start_date"]');
    const endDateInput = document.querySelector('input[name="end_date"]');
    
    // Get station name
    const stationName = stationInput ? stationInput.value.toUpperCase() : 'UNKNOWN';
    
    // Get validity period - check if user uploaded a file or used date pickers
    let validityPeriod = 'unknown_period';
    const datePickerSection = document.querySelector('.date-picker-section');
    const isDatePickerDisabled = datePickerSection && datePickerSection.classList.contains('opacity-50');
    
    if (!isDatePickerDisabled && startDateInput && endDateInput) {
        const startDate = startDateInput.value;
        const endDate = endDateInput.value;
        if (startDate && endDate) {
            validityPeriod = `${startDate}_to_${endDate}`;
        }
    } else {
        // User uploaded a file, use current date as validity period
        const today = new Date().toISOString().split('T')[0];
        validityPeriod = `${today}_file_upload`;
    }
    
    // Create filename
    const filename = `${stationName}_Aerodrome_Warnings_Table_${validityPeriod}.xlsx`;
    console.log('Attempting to download aerodrome warnings table:', filename);
    
    // Show loading state
    const tableDownloadBtn = document.getElementById('adwrn-downloadTableBtn');
    if (tableDownloadBtn) {
        const originalText = tableDownloadBtn.innerHTML;
        tableDownloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Downloading...';
        tableDownloadBtn.disabled = true;
        
        // Reset button after 3 seconds regardless of outcome
        setTimeout(() => {
            tableDownloadBtn.innerHTML = originalText;
            tableDownloadBtn.disabled = false;
        }, 3000);
    }
    
    // Fetch the table data and trigger download
    fetch('/api/download/adwrn_table')
        .then(response => {
            console.log('Table download response status:', response.status);
            if (!response.ok) {
                return response.json().then(errData => {
                    throw new Error(errData.error || 'Failed to download aerodrome warnings table');
                });
            }
            return response.blob();
        })
        .then(blob => {
            console.log('Table download blob received, size:', blob.size);
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.style.display = 'none';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            console.log('Aerodrome warnings table download completed successfully');
        })
        .catch(error => {
            console.error('Table download error:', error);
            showCustomAlert('Error downloading aerodrome warnings table: ' + error.message);
        });
}



// File input change handler for aerodrome warning observation file
document.querySelector('.adwrn-obs-file-input').addEventListener('change', function(e) {
    const file = this.files[0];
    if (!file) return;

    // Disable date picker section and fetch button
    const datePickerSection = document.querySelector('.date-picker-section');
    const fetchBtn = document.getElementById('adwrn-fetch-btn');
    
    datePickerSection.classList.add('opacity-50', 'pointer-events-none');
    fetchBtn.disabled = true;
    fetchBtn.classList.add('opacity-50', 'cursor-not-allowed');

    // Clear any existing date/time values
    document.querySelectorAll('.date-only-picker').forEach(input => input.value = '');
    document.querySelectorAll('.hour-select').forEach(select => select.selectedIndex = 0);
    document.querySelectorAll('.minute-select').forEach(select => select.selectedIndex = 0);

    const uploadBox = this.closest('.upload-box');
    const previewElement = uploadBox.querySelector('.file-preview');
    const previewContent = previewElement.querySelector('.preview-content');
    const loadingIndicator = previewElement.querySelector('.loading-indicator');
    const fileNameContainer = uploadBox.querySelector('.file-name-container');
    const fileNameSpan = fileNameContainer.querySelector('span');

    fileNameSpan.textContent = file.name;
    previewElement.classList.remove('hidden');
    loadingIndicator.classList.remove('hidden');
    previewContent.textContent = '';

    const reader = new FileReader();
    reader.onload = function(e) {
        previewContent.textContent = e.target.result;
        loadingIndicator.classList.add('hidden');
    };
    reader.onerror = function() {
        loadingIndicator.classList.add('hidden');
        previewContent.textContent = 'Error reading file';
    };
    reader.readAsText(file);
});

// Add close button handler to re-enable fetch functionality
document.querySelector('.adwrn-obs-file-input').closest('.upload-box').querySelector('.close-btn').addEventListener('click', function() {
    const datePickerSection = document.querySelector('.date-picker-section');
    const fetchBtn = document.getElementById('adwrn-fetch-btn');
    
    // Re-enable date picker section and fetch button
    datePickerSection.classList.remove('opacity-50', 'pointer-events-none');
    fetchBtn.disabled = false;
    fetchBtn.classList.remove('opacity-50', 'cursor-not-allowed');
});