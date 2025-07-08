// Initialize date pickers and file upload functionality
document.addEventListener('DOMContentLoaded', function () {
    // ===== INITIALIZATION FUNCTIONS =====

    // Custom alert function
    function showCustomAlert(message) {
        // Create alert container if it doesn't exist
        let alertContainer = document.getElementById('customAlertContainer');
        if (!alertContainer) {
            alertContainer = document.createElement('div');
            alertContainer.id = 'customAlertContainer';
            alertContainer.className = 'fixed top-4 right-4 z-50';
            document.body.appendChild(alertContainer);
        }

        // Create alert element
        const alert = document.createElement('div');
        alert.className = 'bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4 shadow-lg';
        alert.innerHTML = `
            <span class="block sm:inline mr-8">${message}</span>
            <span class="absolute top-0 bottom-0 right-0 px-4 py-3">
                <svg class="fill-current h-6 w-6 text-red-500" role="button" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                    <title>Close</title>
                    <path d="M14.348 14.849a1.2 1.2 0 0 1-1.697 0L10 11.819l-2.651 3.029a1.2 1.2 0 1 1-1.697-1.697l2.758-3.15-2.759-3.152a1.2 1.2 0 1 1 1.697-1.697L10 8.183l2.651-3.031a1.2 1.2 0 1 1 1.697 1.697l-2.758 3.152 2.758 3.15a1.2 1.2 0 0 1 0 1.698z"/>
                </svg>
            </span>
        `;

        // Update container position to bottom right
        alertContainer.className = 'fixed bottom-4 right-4 z-50';
        
        // Add to container
        alertContainer.appendChild(alert);

        // Add click handler to close button
        const closeButton = alert.querySelector('svg');
        closeButton.addEventListener('click', () => {
            alert.remove();
        });

        // Auto remove after 5 seconds
        setTimeout(() => {
            alert.remove();
        }, 5000);
    }

    

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
    toggleBtn.addEventListener('click', switchToDefaultState);

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
            if (!file.name.match(/^\d{2}\d{2}\d{4}\.txt$/)) {
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


            // Show the file preview area and loading indicator
            previewElement.classList.remove('hidden');
            loadingIndicator.classList.remove('hidden');
            previewContent.textContent = '';

            // Read the file content
            const reader = new FileReader();
            reader.onload = function (e) {
                // Get the first few lines (around 10 lines)
                const content = e.target.result;
                const lines = content.split('\n');
                const previewLines = lines.slice(0, 10).join('\n');

                // Hide loading indicator and show content
                loadingIndicator.classList.add('hidden');
                previewContent.textContent = previewLines;
            };

            reader.onerror = function () {
                loadingIndicator.classList.add('hidden');
                previewContent.textContent = 'Error reading file';
            };

            reader.readAsText(file);

            // If this is the observation file input, hide date picker and hr line
            if (input.classList.contains('obs-file-input') && file) {
                datePickerSection.style.display = 'none';
                hrLine.style.display = 'none';
                obsUploadBox.classList.add('file-upload-active');
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

// Initialize upper air date pickers
// flatpickr('.upper-air-date-only-picker', {
//     enableTime: false,
//     dateFormat: "Y-m-d",
//     static: true
// });

// // Populate hour and minute selects for upper air
// document.querySelectorAll('.upper-air-hour-select').forEach(select => {
//     for (let i = 0; i < 24; i++) {
//         const option = document.createElement('option');
//         option.value = i.toString().padStart(2, '0');
//         option.textContent = i.toString().padStart(2, '0');
//         select.appendChild(option);
//     }
// });
// document.querySelectorAll('.upper-air-minute-select').forEach(select => {
//     for (let i = 0; i < 60; i++) {
//         const option = document.createElement('option');
//         option.value = i.toString().padStart(2, '0');
//         option.textContent = i.toString().padStart(2, '0');
//         select.appendChild(option);
//     }
// });

// // Fetch and preview upper air data for selected range
// function fetchUpperAirMetarPreview() {
//     // Get start/end date/time and station code from the upper air section
//     const startDateContainer = document.querySelectorAll('#upperAirDateRangeSection .date-time-picker-container')[0];
//     const endDateContainer = document.querySelectorAll('#upperAirDateRangeSection .date-time-picker-container')[1];
//     const stationCode = document.getElementById('upperAirStationInput').value;

//     const startDateValue = startDateContainer.querySelector('.upper-air-date-only-picker').value;
//     const startHour = startDateContainer.querySelector('.upper-air-hour-select').value;
//     const startMinute = startDateContainer.querySelector('.upper-air-minute-select').value;

//     const endDateValue = endDateContainer.querySelector('.upper-air-date-only-picker').value;
//     const endHour = endDateContainer.querySelector('.upper-air-hour-select').value;
//     const endMinute = endDateContainer.querySelector('.upper-air-minute-select').value;

//     // Format date for API (reuse your formatDate function if available)
//     function formatDate(date, hour, minute) {
//         const d = new Date(date);
//         return `${d.getFullYear()}${String(d.getMonth() + 1).padStart(2, '0')}${String(d.getDate()).padStart(2, '0')}${String(hour).padStart(2, '0')}${String(minute).padStart(2, '0')}`;
//     }

//     if (
//         startDateValue && startHour !== '' && startMinute !== '' &&
//         endDateValue && endHour !== '' && endMinute !== '' &&
//         stationCode
//     ) {
//         const startDateTime = formatDate(startDateValue, startHour, startMinute);
//         const endDateTime = formatDate(endDateValue, endHour, endMinute);

//         // Get preview elements for upper air section
//         const upperAirPreview = document.querySelector('#upperAirDateRangeSection .upper-air-preview');
//         const previewContent = upperAirPreview.querySelector('.preview-content');
//         const loadingIndicator = upperAirPreview.querySelector('.loading-indicator');

//         // Show preview section and loading indicator
//         upperAirPreview.classList.remove('hidden');
//         loadingIndicator.classList.remove('hidden');
//         previewContent.textContent = '';

//         // Make API request (same endpoint as METAR)
//         fetch(`/api/get_metar?start_date=${startDateTime}&end_date=${endDateTime}&icao=${stationCode}`)
//             .then(response => {
//                 if (!response.ok) {
//                     return response.json().then(err => {
//                         throw new Error(err.error || 'Failed to fetch METAR data');
//                     });
//                 }
//                 return response.text();
//             })
//             .then(data => {
//                 // Hide loading indicator and show data
//                 loadingIndicator.classList.add('hidden');
//                 previewContent.textContent = data;
//             })
//             .catch(error => {
//                 // Hide preview section on error
//                 upperAirPreview.classList.add('hidden');
//                 console.error('Error fetching METAR data:', error);
//             });
//     }
// }

// document.getElementById('upperAirFetchRangeBtn')?.addEventListener('click', fetchUpperAirRangePreview);
// Example station buttons

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

            // Set accuracy values
            document.getElementById('tempAccuracy').textContent = data.temp_accuracy !== undefined ? `${data.temp_accuracy}%` : '--';
            document.getElementById('windAccuracy').textContent = data.wind_accuracy !== undefined ? `${data.wind_accuracy}%` : '--';
            document.getElementById('windDirAccuracy').textContent = data.wind_dir_accuracy !== undefined ? `${data.wind_dir_accuracy}%` : '--';

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


// Setup drag and drop for both areas
setupDragAndDrop('upperAirObsUploadArea', 'upperAirObsFileInput', 'csv');
setupDragAndDrop('upperAirForecastUploadArea', 'upperAirForecastFileInput', 'pdf');