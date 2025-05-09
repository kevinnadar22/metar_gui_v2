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
            if (!file) return;

            const uploadBox = this.closest('.upload-box');
            const previewElement = uploadBox.querySelector('.file-preview');
            const previewContent = previewElement.querySelector('.preview-content');
            const loadingIndicator = previewElement.querySelector('.loading-indicator');

            const fileNameContainer = uploadBox.querySelector('.file-name-container');
            const fileNameSpan = fileNameContainer.querySelector('span');

            // Show the file name
            fileNameSpan.textContent = file.name;

            // file name should be in the format MMYYYY.txt
            if (!file.name.match(/^\d{2}\d{4}\.txt$/)) {
                showCustomAlert('Please upload a file named with month and year (like 012024.txt). The first two digits are the month (01-12) and the next four digits are the year.');
                return;
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

        // check if forecast file is present and it should be in the format MMYYYY.txt
        if (!forecastFile || !forecastFile.name.match(/^\d{2}\d{4}\.txt$/)) {
            showCustomAlert('Please upload a valid forecast file in the format MMYYYY.txt.');
            return;
        }

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