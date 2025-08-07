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

                    // Set download button href
                    const downloadCsvBtn = document.getElementById('downloadCsvBtn');
                    downloadCsvBtn.href = downloadUrl;

                    // Function to populate a table from CSV data
                    const populateTableFromCSV = (csvText, tableElement) => {
                        // Parse CSV and populate table
                        const rows = csvText.split('\n');
                        const headers = rows[0].split(',');

                        // Create table container with scroll
                        const tableContainer = document.createElement('div');
                        tableContainer.className = 'overflow-auto max-h-[500px] border border-gray-200 rounded-lg';

                        // Clear only tbody content, preserve thead
                        const tbody = tableElement.querySelector('tbody') || document.createElement('tbody');
                        tbody.innerHTML = '';

                        // Create and update thead if it doesn't exist
                        let thead = tableElement.querySelector('thead');
                        if (!thead) {
                            thead = document.createElement('thead');
                            thead.className = 'bg-gray-100 sticky top-0 z-10';
                        }

                        // Update header content
                        const headerRow = document.createElement('tr');
                        headers.forEach(header => {
                            const th = document.createElement('th');
                            // Replace underscores with spaces and capitalize each word
                            th.textContent = header.replace(/_/g, ' ')
                                .replace(/\w\S*/g, txt => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase());
                            th.className = 'px-6 py-3 text-left text-xs font-medium text-gray-800 uppercase tracking-wider';
                            headerRow.appendChild(th);
                        });
                        thead.innerHTML = '';
                        thead.appendChild(headerRow);

                        // Ensure thead is in table
                        if (!tableElement.contains(thead)) {
                            tableElement.appendChild(thead);
                        }

                        // Create table body rows
                        for (let i = 1; i < rows.length; i++) {
                            if (rows[i].trim() === '') continue;

                            const rowData = rows[i].split(',');
                            const tr = document.createElement('tr');
                            tr.className = 'transition-colors duration-150 ease-in-out';

                            rowData.forEach((cell, index) => {
                                const td = document.createElement('td');
                                td.textContent = cell;
                                td.className = 'px-6 py-4 text-sm border-b border-gray-200';
                                tr.appendChild(td);
                            });
                            tbody.appendChild(tr);
                        }

                        // Ensure tbody is in table
                        if (!tableElement.contains(tbody)) {
                            tableElement.appendChild(tbody);
                        }

                        // Add border and other styling to the table
                        tableElement.className = 'min-w-full divide-y divide-gray-200 table-fixed';

                        // Wrap table in scrollable container if not already wrapped
                        const parent = tableElement.parentElement;
                        if (!parent.classList.contains('overflow-auto')) {
                            // Remove table from current parent
                            if (parent) {
                                parent.removeChild(tableElement);
                            }

                            // Add table to container and container to original parent
                            tableContainer.appendChild(tableElement);
                            if (parent) {
                                parent.appendChild(tableContainer);
                            } else {
                                reportSection.appendChild(tableContainer);
                            }
                        }
                    };

                    // Fetch and populate the comparison table
                    fetch(downloadUrl)
                        .then(response => {
                            if (!response.ok) {
                                throw new Error('Failed to download comparison CSV');
                            }
                            return response.text();
                        })
                        .then(csvText => {
                            populateTableFromCSV(csvText, comparisonTable);
                            
                            // Now fetch and populate the detailed comparison table
                            return fetch(detailedDownloadUrl);
                        })
                        .then(response => {
                            if (!response.ok) {
                                throw new Error('Failed to download detailed comparison CSV');
                            }
                            return response.text();
                        })
                        .then(csvText => {
                            // Get the detailed comparison table
                            const detailedComparisonTable = document.getElementById('detailedComparisonTable');
                            populateTableFromCSV(csvText, detailedComparisonTable);
                            
                            // Show report section after both tables are populated
                            reportSection.style.display = 'block';
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
const upperAirFetchBtn = document.getElementById('upperAirFetchBtn');
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
upperAirFetchBtn.addEventListener('click', function () {
    const date = upperAirDatePicker.value;
    const hour = upperAirHourSelect.value;
    const station = upperAirStationInput.value;
    if (!date || !hour || !/^\d{5}$/.test(station)) {
        if (typeof showCustomAlert === 'function') {
            showCustomAlert('Please select date, hour, and enter a valid 5-digit station ID.');
        } else {
            alert('Please select date, hour, and enter a valid 5-digit station ID.');
        }
        return;
    }
    upperAirPreviewSection.classList.remove('hidden');
    upperAirLoadingIndicator.classList.remove('hidden');
    upperAirPreviewContent.textContent = '';
    const dateTime = `${date} ${hour}:00:00`;
    fetch(`/api/get_upper_air?datetime=${encodeURIComponent(dateTime)}&station_id=${station}`)
        .then(async response => {
            upperAirLoadingIndicator.classList.add('hidden');
            if (!response.ok) {
                // Try to parse error JSON
                let errorMsg = 'Failed to fetch upper air data';
                try {
                    const err = await response.json();
                    errorMsg = err.error || errorMsg;
                } catch (e) {}
                throw new Error(errorMsg);
            }
            const text = await response.text();
            // If the response looks like HTML, show a friendly error
            if (text.trim().toLowerCase().startsWith('<!doctype html') || text.trim().toLowerCase().startsWith('<html')) {
                throw new Error('No data available for the selected date/time/station.');
            }
            upperAirPreviewContent.textContent = text;
        })
        .catch(error => {
            upperAirPreviewSection.classList.add('hidden');
            if (typeof showCustomAlert === 'function') {
                showCustomAlert('Error fetching upper air data: ' + error.message);
            } else {
                alert('Error fetching upper air data: ' + error.message);
            }
        });
});

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
            // Show results section
            upperAirReportSection.style.display = 'block';

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
            if (data.file_path) {
                fetch(`/api/download/upper_air_csv?file_path=${encodeURIComponent(data.file_path)}`)
                    .then(response => {
                        if (!response.ok) throw new Error('Failed to download verification CSV');
                        return response.text();
                    })
                    .then(csvText => {
                        populateUpperAirVerificationTable(csvText);
                    })
                    .catch(error => {
                        showCustomAlert('Failed to load verification data. Please try again.');
                    });

                // Set download button
                const downloadBtn = document.querySelector('#upperAirReportSection #downloadCsvBtn');
                if (downloadBtn) {
                    downloadBtn.href = `/api/download/upper_air_csv?file_path=${encodeURIComponent(data.file_path)}`;
                }
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
            
            isResetMode = false;
            return;
        }
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
const adwrnFinalReportContainer = document.getElementById('adwrn-final-report-container');
const adwrnFinalReportTable = document.getElementById('adwrn-final-report-table');
const adwrnAccuracy = document.getElementById('adwrn-accuracy');
const adwrnReportLoadingSection = document.getElementById('adwrn-reportLoadingSection');

function renderCsvToTable(csvText, tableElement) {
    const lines = csvText.trim().split(/\r?\n/);
    if (lines.length === 0) return;
    // Remove any trailing blank lines
    while (lines.length && lines[lines.length-1].trim() === '') lines.pop();
    // Extract header and rows
    const header = lines[0].split(',');
    const rows = lines.slice(1).map(line => line.split(','));
    // Render header
    const thead = tableElement.querySelector('thead');
    thead.innerHTML = '';
    const headerRow = document.createElement('tr');
    header.forEach(h => {
        const th = document.createElement('th');
        th.textContent = h.trim();
        th.className = 'px-6 py-3 text-left text-xs font-medium text-gray-800 uppercase tracking-wider';
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    // Render body
    const tbody = tableElement.querySelector('tbody');
    tbody.innerHTML = '';
    rows.forEach(row => {
        if (row.length !== header.length) return;
        const tr = document.createElement('tr');
        row.forEach(cell => {
            const td = document.createElement('td');
            td.textContent = cell.trim();
            td.className = 'px-6 py-4 text-sm border-b border-gray-200';
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
}

function renderAerodromeWarningTable(csvText, tableElement, detailedAccuracy = {}) {
    const lines = csvText.trim().split(/\r?\n/);
    if (lines.length === 0) return;
    
    // Remove any trailing blank lines
    while (lines.length && lines[lines.length-1].trim() === '') lines.pop();
    
    // Extract header and rows
    const header = lines[0].split(',');
    const rows = lines.slice(1).map(line => line.split(','));
    
    // Debug: Print table structure
    console.log("Table element:", tableElement);
    console.log("Table thead:", tableElement.querySelector('thead'));
    console.log("Table tbody:", tableElement.querySelector('tbody'));
    
    // Ensure thead is visible and has content
    const thead = tableElement.querySelector('thead');
    if (thead) {
        console.log("Thead found, ensuring it's visible");
        thead.style.display = 'table-header-group';
        const headerRow = thead.querySelector('tr');
        if (headerRow) {
            console.log("Header row found with", headerRow.children.length, "columns");
            Array.from(headerRow.children).forEach((th, index) => {
                console.log(`Header ${index + 1}:`, th.textContent);
            });
        } else {
            // If no header row exists, create one
            console.log("No header row found, creating one");
            const newHeaderRow = document.createElement('tr');
            const headers = [
                'क्र. सं. / Sr.No.',
                'तत्त्व / Elements',
                'विमान क्षेत्र चेतावनियों की सं. / Warning no 1 Warning no 2................ Warning no. (Issue date/Issue Time UTC)',
                'रेंज के अंतगर्द आने वाले (पारस) मामलों की प्रतिशतता अथवा सही होने की प्रतिशतता / % of cases within range or occurrence (% correct)',
                'वास्तविक मौसम समयावधि के साथ जिसके लिये चेतावनी जारी नहीं की गयी थी / Actual weather with duration for which no warning was issued'
            ];
            
            headers.forEach(headerText => {
                const th = document.createElement('th');
                th.innerHTML = headerText;
                newHeaderRow.appendChild(th);
            });
            thead.appendChild(newHeaderRow);
            console.log("Created new header row with", headers.length, "columns");
        }
    }
    
    // Define the standard aerodrome warning elements
    const warningElements = [
        { srNo: "1.", element: "उष्णकटिबंधीय चक्रवात / Tropical cyclone" },
        { srNo: "2.", element: "गर्जन सुनामी / Thunderstorms" },
        { srNo: "3.", element: "ओला / Hail" },
        { srNo: "4.", element: "बर्फ / Snow" },
        { srNo: "5.", element: "हिमवर्षा / Freezing precipitation" },
        { srNo: "6.", element: "पाला या शीत / Hoar Frost or rime" },
        { srNo: "7.", element: "धूल भरी आँधी / Dust storm" },
        { srNo: "8.", element: "रेतीली आँधी / Sandstorm" },
        { srNo: "9.", element: "उठती रेत या धूल / Rising sand or dust" },
        { srNo: "10.", element: "प्रबल सतही पवन तथा झोंके / Strong surface wind and gusts<br><strong>गति / Speed</strong>" },
        { srNo: "", element: "<strong>दिशा परिवर्तन / Direction change</strong>" },
        { srNo: "11.", element: "बवंडर / Squall<br>दिशा / Direction<br>गति / Speed" },
        { srNo: "12.", element: "पाला / Frost" },
        { srNo: "13.", element: "ज्वालामुखीय राख / Volcanic ash" },
        { srNo: "14.", element: "सुनामी / Tsunami" }
    ];
    
    // Render body
    const tbody = tableElement.querySelector('tbody');
    tbody.innerHTML = '';
    
    // Process the CSV data to extract relevant information
    const thunderstormWarnings = [];
    const windWarnings = [];
    let thunderstormAccuracy = "-";
    let windAccuracy = "-";
    
    // Parse the CSV data more carefully
    rows.forEach(row => {
        if (row.length >= 4) {
            const element = row[1]?.trim() || "";
            const issueTime = row[2]?.trim() || "";
            const accuracy = row[3]?.trim() || "";
            
            // Check for thunderstorm warnings
            if (element.toLowerCase().includes("thunderstorm") || element.toLowerCase().includes("गर्जन") || element.toLowerCase().includes("ts")) {
                if (issueTime && issueTime !== "-" && issueTime !== "0") {
                    thunderstormWarnings.push(issueTime);
                }
                if (accuracy && accuracy !== "-" && accuracy !== "0") {
                    // Convert accuracy to percentage
                    const accuracyNum = parseFloat(accuracy);
                    if (!isNaN(accuracyNum)) {
                        thunderstormAccuracy = accuracyNum === 1 ? "100%" : `${Math.round(accuracyNum * 100)}%`;
                    } else {
                        thunderstormAccuracy = accuracy; // Keep as is if it's already a percentage
                    }
                }
            } 
            // Check for wind/gust warnings
            else if (element.toLowerCase().includes("wind") || element.toLowerCase().includes("gust") || element.toLowerCase().includes("पवन") || element.toLowerCase().includes("surface")) {
                if (issueTime && issueTime !== "-" && issueTime !== "0") {
                    windWarnings.push(issueTime);
                }
                if (accuracy && accuracy !== "-" && accuracy !== "0") {
                    // Convert accuracy to percentage
                    const accuracyNum = parseFloat(accuracy);
                    if (!isNaN(accuracyNum)) {
                        windAccuracy = accuracyNum === 1 ? "100%" : `${Math.round(accuracyNum * 100)}%`;
                    } else {
                        windAccuracy = accuracy; // Keep as is if it's already a percentage
                    }
                }
            }
        }
    });
    
    // If we have the Accuracy_Percentage column (column 5), use it instead
    if (header.length >= 5 && header[4]?.includes("Accuracy")) {
        rows.forEach(row => {
            if (row.length >= 5) {
                const element = row[1]?.trim() || "";
                const issueTime = row[2]?.trim() || "";
                const accuracyPercentage = row[4]?.trim() || "";
                
                // Check for thunderstorm warnings
                if (element.toLowerCase().includes("thunderstorm") || element.toLowerCase().includes("गर्जन") || element.toLowerCase().includes("ts")) {
                    if (issueTime && issueTime !== "-" && issueTime !== "0") {
                        thunderstormWarnings.push(issueTime);
                    }
                    if (accuracyPercentage && accuracyPercentage !== "-" && accuracyPercentage !== "0%") {
                        thunderstormAccuracy = accuracyPercentage;
                    }
                } 
                // Check for wind/gust warnings
                else if (element.toLowerCase().includes("wind") || element.toLowerCase().includes("gust") || element.toLowerCase().includes("पवन") || element.toLowerCase().includes("surface")) {
                    if (issueTime && issueTime !== "-" && issueTime !== "0") {
                        windWarnings.push(issueTime);
                    }
                    if (accuracyPercentage && accuracyPercentage !== "-" && accuracyPercentage !== "0%") {
                        windAccuracy = accuracyPercentage;
                    }
                }
            }
        });
    }
    
    // Calculate actual percentages from the data
    let thunderstormCount = 0;
    let thunderstormCorrect = 0;
    let windCount = 0;
    let windCorrect = 0;
    
    rows.forEach(row => {
        if (row.length >= 4) {
            const element = row[1]?.trim() || "";
            const accuracy = row[3]?.trim() || "";
            
            // Count thunderstorm warnings
            if (element.toLowerCase().includes("thunderstorm") || element.toLowerCase().includes("गर्जन") || element.toLowerCase().includes("ts")) {
                thunderstormCount++;
                if (accuracy === "1" || accuracy === "true") {
                    thunderstormCorrect++;
                }
            } 
            // Count wind/gust warnings
            else if (element.toLowerCase().includes("wind") || element.toLowerCase().includes("gust") || element.toLowerCase().includes("पवन") || element.toLowerCase().includes("surface")) {
                windCount++;
                if (accuracy === "1" || accuracy === "true") {
                    windCorrect++;
                }
            }
        }
    });
    
    // Use detailed accuracy from API if available, otherwise calculate from data
    console.log("Using detailed accuracy:", detailedAccuracy);
    
    if (detailedAccuracy.thunderstorm !== undefined) {
        thunderstormAccuracy = `${detailedAccuracy.thunderstorm}%`;
        console.log("Setting thunderstorm accuracy to:", thunderstormAccuracy);
    } else if (thunderstormCount > 0) {
        const thunderstormPercent = Math.round((thunderstormCorrect / thunderstormCount) * 100);
        thunderstormAccuracy = `${thunderstormPercent}%`;
        console.log("Calculated thunderstorm accuracy:", thunderstormAccuracy);
    }
    
    if (detailedAccuracy.wind !== undefined) {
        windAccuracy = `${detailedAccuracy.wind}%`;
        console.log("Setting wind accuracy to:", windAccuracy);
    } else if (windCount > 0) {
        const windPercent = Math.round((windCorrect / windCount) * 100);
        windAccuracy = `${windPercent}%`;
        console.log("Calculated wind accuracy:", windAccuracy);
    }
    
    // Populate the table with standard format
    warningElements.forEach((item, index) => {
        const tr = document.createElement('tr');
        
        // Sr.No.
        const td1 = document.createElement('td');
        td1.textContent = item.srNo;
        tr.appendChild(td1);
        
        // Elements
        const td2 = document.createElement('td');
        td2.innerHTML = item.element;
        tr.appendChild(td2);
        
        // Warning numbers and times
        const td3 = document.createElement('td');
        if (index === 1) { // Thunderstorms
            td3.textContent = thunderstormWarnings.length > 0 ? thunderstormWarnings.join(',') : "-";
        } else if (index === 9) { // Wind speed
            td3.textContent = windWarnings.length > 0 ? windWarnings.join(',') : "-";
            td3.style.whiteSpace = "pre-wrap";
            td3.style.fontSize = "10px";
        } else {
            td3.textContent = "-";
        }
        tr.appendChild(td3);
        
        // Accuracy percentage
        const td4 = document.createElement('td');
        if (index === 1) { // Thunderstorms
            td4.textContent = thunderstormAccuracy;
        } else if (index === 9) { // Wind speed
            td4.textContent = windAccuracy;
        } else {
            td4.textContent = "-";
        }
        tr.appendChild(td4);
        
        // Actual weather without warnings
        const td5 = document.createElement('td');
        td5.textContent = "-";
        tr.appendChild(td5);
        
        tbody.appendChild(tr);
    });
}

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

if (adwrnVerifyBtn && adwrnFinalReportContainer && adwrnFinalReportTable && adwrnAccuracy && adwrnReportLoadingSection) {
    adwrnVerifyBtn.addEventListener('click', function() {
        console.log('Verify button clicked'); // Debug log
        
        adwrnFinalReportContainer.style.display = 'none';
        adwrnAccuracy.style.display = 'none';
        adwrnAccuracy.textContent = '';
        // Don't clear thead - let the renderAerodromeWarningTable function handle it
        adwrnFinalReportTable.querySelector('tbody').innerHTML = '';
        

        
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
                    // Show only station information if available (hide accuracy)
                    if (data.station_info) {
                        adwrnAccuracy.textContent = data.station_info;
                        adwrnAccuracy.style.display = 'block';
                    } else {
                        adwrnAccuracy.style.display = 'none';
                    }
                    
                    // Pass detailed accuracy data to the table rendering function
                    const detailedAccuracy = data.detailed_accuracy || {};
                    console.log("Detailed accuracy from API:", detailedAccuracy);
                    renderAerodromeWarningTable(data.report, adwrnFinalReportTable, detailedAccuracy);
                    adwrnFinalReportContainer.style.display = 'block';
                    
                    // Show the report section with download buttons
                    const adwrnReportSection = document.getElementById('adwrn-reportSection');
                    if (adwrnReportSection) {
                        adwrnReportSection.style.display = 'block';
                    }
                    
                    // Debug: Check if table headers are visible
                    console.log("Table element:", adwrnFinalReportTable);
                    console.log("Table thead:", adwrnFinalReportTable.querySelector('thead'));
                    console.log("Table headers:", adwrnFinalReportTable.querySelectorAll('th'));
                    console.log("Container display style:", adwrnFinalReportContainer.style.display);
                    

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

// Add event listener for the download button
document.addEventListener('DOMContentLoaded', function() {
    // Add event listener for the aerodrome warnings table download button
    const tableDownloadBtn = document.getElementById('adwrn-downloadTableBtn');
    if (tableDownloadBtn) {
        tableDownloadBtn.addEventListener('click', downloadAerodromeWarningsTable);
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
