// Main Application JavaScript
class LogClassifierApp {
    constructor() {
        this.apiBaseUrl = '';  // Base URL for direct endpoints
        this.apiV1BaseUrl = '/api/v1';  // Base URL for v1 API endpoints
        this.currentFile = null;
        this.isProcessingFile = false; // Flag to prevent double processing
        this.isValidating = false; // Flag to prevent concurrent validation
        this.isClassifying = false; // Flag to prevent concurrent classification
        this.lastValidationTime = 0; // Track last validation to prevent duplicates
        this.lastClassificationTime = 0; // Track last classification
        this.eventListenersAdded = false; // Prevent duplicate event listeners
        this.lastFileInputTime = 0; // Track file input change events
        this.charts = {};
        this.lastClassificationResults = null; // Store latest classification results for dashboard
        this.classificationAbortController = null; // For canceling requests
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkApiStatus();
        this.loadDashboard();
        this.setupTabNavigation();
    }

    // Event Listeners Setup
    setupEventListeners() {
        if (this.eventListenersAdded) {
            return;
        }
        this.eventListenersAdded = true;
        
        // File Upload
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const removeFile = document.getElementById('removeFile');

        // Drag and Drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            console.log('Files dropped:', files.length);
            if (files.length > 0 && !this.isProcessingFile) {
                console.log('Processing dropped file:', files[0].name);
                this.handleFileSelect(files[0]);
            }
        });

        uploadArea.addEventListener('click', (e) => {
            console.log('Upload area clicked, opening file dialog');
            if (!this.isProcessingFile) {
                // Simple approach - just use the original file input
                fileInput.value = ''; // Clear previous selection
                fileInput.click();
            }
        });

        // Add the file input change listener normally
        fileInput.addEventListener('change', (e) => {
            console.log('File input changed, files:', e.target.files.length);
            if (e.target.files.length > 0 && !this.isProcessingFile) {
                console.log('Processing file from input change:', e.target.files[0].name);
                this.handleFileSelect(e.target.files[0]);
            }
        });

        removeFile.addEventListener('click', (e) => {
            e.stopPropagation();
            this.removeFile();
        });

        // Buttons
        document.getElementById('classifyBtn').addEventListener('click', () => {
            this.classifyLogs();
        });

        document.getElementById('cancelBtn').addEventListener('click', () => {
            this.cancelClassification();
        });

        document.getElementById('validateBtn').addEventListener('click', () => {
            this.validateFile();
        });

        document.getElementById('downloadBtn').addEventListener('click', () => {
            this.downloadResults();
        });

        document.getElementById('viewDetailsBtn').addEventListener('click', () => {
            this.viewResultDetails();
        });

        document.getElementById('refreshDashboard').addEventListener('click', () => {
            this.loadDashboard();
        });

        // API Test buttons
        document.querySelectorAll('.test-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const endpoint = e.target.getAttribute('data-endpoint');
                this.testApiEndpoint(endpoint);
            });
        });
    }

    // Tab Navigation
    setupTabNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');
        const tabContents = document.querySelectorAll('.tab-content');

        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetTab = link.getAttribute('data-tab');

                // Update active nav link
                navLinks.forEach(l => l.classList.remove('active'));
                link.classList.add('active');

                // Update active tab content
                tabContents.forEach(tab => tab.classList.remove('active'));
                document.getElementById(`${targetTab}-tab`).classList.add('active');

                // Load dashboard data when switching to dashboard
                if (targetTab === 'dashboard') {
                    this.loadDashboard();
                }
            });
        });
    }

    // File Handling
    handleFileSelect(file) {
        // Prevent double processing
        if (this.isProcessingFile) {
            return;
        }
        
        this.isProcessingFile = true;
        
        if (!this.validateFileType(file)) {
            this.showToast('error', 'Invalid File Type', 'Please select a CSV file.');
            this.isProcessingFile = false;
            return;
        }

        if (!this.validateFileSize(file)) {
            this.showToast('error', 'File Too Large', 'File size must be less than 10MB.');
            this.isProcessingFile = false;
            return;
        }

        this.currentFile = file;
        this.showFileInfo(file);
        this.enableButtons();
        
        // Auto-validate file (now with debounce protection)
        this.validateFile();
        
        // Reset the flag after a short delay
        setTimeout(() => {
            this.isProcessingFile = false;
        }, 100); // Reduced from 500ms to 100ms
    }

    validateFileType(file) {
        return file.type === 'text/csv' || file.name.endsWith('.csv');
    }

    validateFileSize(file) {
        return file.size <= 10 * 1024 * 1024; // 10MB
    }

    showFileInfo(file) {
        const fileInfo = document.getElementById('fileInfo');
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');
        const uploadArea = document.getElementById('uploadArea');

        fileName.textContent = file.name;
        fileSize.textContent = this.formatFileSize(file.size);
        
        uploadArea.style.display = 'none';
        fileInfo.style.display = 'block';
        fileInfo.classList.add('fade-in');
    }

    removeFile() {
        this.currentFile = null;
        const fileInfo = document.getElementById('fileInfo');
        const uploadArea = document.getElementById('uploadArea');
        const validationStatus = document.getElementById('validationStatus');

        fileInfo.style.display = 'none';
        uploadArea.style.display = 'block';
        validationStatus.innerHTML = '';
        
        this.disableButtons();
        document.getElementById('fileInput').value = '';
    }

    enableButtons() {
        document.getElementById('classifyBtn').disabled = false;
        document.getElementById('validateBtn').disabled = false;
    }

    disableButtons() {
        document.getElementById('classifyBtn').disabled = true;
        document.getElementById('validateBtn').disabled = true;
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // API Functions
    async checkApiStatus() {
        try {
            const response = await fetch(`${this.apiV1BaseUrl}/health/`);
            const data = await response.json();
            
            const statusIndicator = document.getElementById('apiStatus');
            if (response.ok) {
                statusIndicator.className = 'status-indicator online';
                statusIndicator.innerHTML = '<i class="fas fa-circle"></i><span>Online</span>';
            } else {
                throw new Error('API not responding');
            }
        } catch (error) {
            const statusIndicator = document.getElementById('apiStatus');
            statusIndicator.className = 'status-indicator offline';
            statusIndicator.innerHTML = '<i class="fas fa-circle"></i><span>Offline</span>';
        }
    }

    async validateFile() {
        // More aggressive duplicate prevention
        if (this.isValidating) {
            console.log('Validation already in progress - ignoring duplicate call');
            return;
        }
        
        const now = Date.now();
        if (now - this.lastValidationTime < 2000) { // Increased to 2 seconds
            console.log('Validation call ignored - too recent (debounced)', now - this.lastValidationTime, 'ms ago');
            return;
        }
        
        this.isValidating = true;
        this.lastValidationTime = now;
        
        console.log('validateFile called - proceeding with validation');
        
        if (!this.currentFile) {
            console.log('No file to validate');
            this.isValidating = false;
            return;
        }

        const formData = new FormData();
        formData.append('file', this.currentFile);

        try {
            const response = await fetch(`${this.apiV1BaseUrl}/validate/`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            const validationStatus = document.getElementById('validationStatus');

            if (response.ok) {
                validationStatus.className = 'validation-status success';
                validationStatus.innerHTML = `
                    <i class="fas fa-check-circle"></i>
                    <div>
                        <strong>File is valid!</strong><br>
                        ${data.message || 'Ready for classification'}
                        ${data.total_records ? `<br>Records: ${data.total_records}` : ''}
                    </div>
                `;
            } else {
                validationStatus.className = 'validation-status error';
                validationStatus.innerHTML = `
                    <i class="fas fa-exclamation-circle"></i>
                    <div>
                        <strong>Validation failed:</strong><br>
                        ${data.detail || 'Unknown error'}
                    </div>
                `;
            }
        } catch (error) {
            console.error('Validation error:', error);
            this.showToast('error', 'Validation Error', 'Failed to validate file.');
        } finally {
            // Always reset the validation flag
            this.isValidating = false;
            console.log('Validation flag reset');
        }
    }

    async classifyLogs() {
        // Prevent duplicate classification requests
        if (this.isClassifying) {
            console.log('Classification already in progress - ignoring duplicate request');
            return;
        }
        
        const now = Date.now();
        if (now - this.lastClassificationTime < 3000) { // 3 second debounce
            console.log('Classification request ignored - too recent (debounced)');
            return;
        }
        
        this.isClassifying = true;
        this.lastClassificationTime = now;
        
        console.log('=== CLASSIFY LOGS STARTED ===');
        console.log('classifyLogs called, currentFile:', this.currentFile ? this.currentFile.name : 'null');
        console.log('currentFile type:', typeof this.currentFile);
        console.log('currentFile instanceof File:', this.currentFile instanceof File);
        
        if (!this.currentFile) {
            console.error('No file selected');
            this.showToast('error', 'No File Selected', 'Please select a file first.');
            this.isClassifying = false;
            return;
        }

        const method = document.querySelector('input[name="method"]:checked').value;
        console.log('Selected method:', method);
        
        const formData = new FormData();
        formData.append('file', this.currentFile);
        console.log('FormData created with file:', this.currentFile.name);
        console.log('FormData file size:', this.currentFile.size);
        console.log('FormData file type:', this.currentFile.type);
        
        // Debug: Log FormData contents
        for (let [key, value] of formData.entries()) {
            console.log('FormData entry:', key, value);
        }

        // Show progress section and setup cancellation
        this.showProgress();
        this.updateProgress(20, 'Starting classification...');
        
        // Show cancel button and hide classify button
        document.getElementById('classifyBtn').style.display = 'none';
        document.getElementById('cancelBtn').style.display = 'inline-block';
        
        // Create abort controller for cancellation
        this.classificationAbortController = new AbortController();

        try {
            this.updateProgress(40, 'Uploading file...');
            
            console.log('Making API request to:', `${this.apiV1BaseUrl}/classify/`);
            console.log('Request details:', {
                method: 'POST',
                body: formData,
                headers: 'none (letting browser set multipart boundary)'
            });
            
            const response = await fetch(`${this.apiV1BaseUrl}/classify/`, {
                method: 'POST',
                body: formData,
                signal: this.classificationAbortController.signal
            });

            console.log('API response status:', response.status);
            console.log('API response headers:', Object.fromEntries(response.headers.entries()));
            
            this.updateProgress(80, 'Processing results...');

            if (response.ok) {
                const data = await response.json();
                console.log('API response data:', data);
                console.log('classified_logs array:', data.classified_logs);
                
                this.updateProgress(100, 'Classification complete!');
                
                setTimeout(() => {
                    this.showResults(data);
                    this.showToast('success', 'Classification Complete!', 'Your logs have been successfully classified.');
                    // Update dashboard with new statistics
                    this.loadDashboard();
                }, 500);
            } else {
                const errorText = await response.text();
                console.error('API error response (raw):', errorText);
                
                let errorData;
                try {
                    errorData = JSON.parse(errorText);
                } catch (e) {
                    errorData = { detail: errorText };
                }
                
                console.error('API error response (parsed):', errorData);
                throw new Error(errorData.detail || 'Classification failed');
            }
        } catch (error) {
            console.error('Classification error:', error);
            if (error.name === 'AbortError') {
                this.showToast('info', 'Classification Cancelled', 'The classification process was cancelled.');
            } else {
                this.showToast('error', 'Classification Failed', error.message);
            }
            this.hideProgress();
        } finally {
            // Always reset the classification flag and hide cancel button
            this.isClassifying = false;
            this.classificationAbortController = null;
            document.getElementById('classifyBtn').style.display = 'inline-block';
            document.getElementById('cancelBtn').style.display = 'none';
            console.log('Classification flag reset');
        }
    }

    cancelClassification() {
        if (this.classificationAbortController) {
            console.log('Cancelling classification request...');
            this.classificationAbortController.abort();
            this.showToast('info', 'Cancelling...', 'Classification is being cancelled.');
            
            // Also cancel the backend task
            this.cancelBackendClassification();
        }
    }

    async cancelBackendClassification() {
        try {
            const response = await fetch(`${this.apiV1BaseUrl}/classify/cancel/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const result = await response.json();
                console.log('Backend classification cancelled:', result.message);
                this.showToast('warning', 'Cancelled', result.message);
            } else {
                console.error('Failed to cancel backend classification');
                this.showToast('error', 'Cancel Error', 'Failed to cancel classification on server');
            }
        } catch (error) {
            console.error('Error cancelling backend classification:', error);
            // Don't show error toast for cancelled requests (AbortError)
            if (error.name !== 'AbortError') {
                this.showToast('error', 'Cancel Error', 'Error cancelling classification');
            }
        }
    }

    async downloadResults() {
        if (!this.currentFile) return;

        const formData = new FormData();
        formData.append('file', this.currentFile);

        try {
            const response = await fetch(`${this.apiBaseUrl}/classify/download/`, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `classified_${this.currentFile.name}`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                this.showToast('success', 'Download Started', 'Your classified results are downloading.');
            } else {
                throw new Error('Download failed');
            }
        } catch (error) {
            console.error('Download error:', error);
            this.showToast('error', 'Download Failed', 'Failed to download results.');
        }
    }

    async viewResultDetails() {
        if (!this.currentFile) {
            this.showToast('warning', 'No Data', 'Please classify logs first to view details.');
            return;
        }

        try {
            // Get the classified results
            const formData = new FormData();
            formData.append('file', this.currentFile);
            
            const response = await fetch(`${this.apiBaseUrl}/classify/download/`, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const csvText = await response.text();
                this.showResultsModal(csvText);
            } else {
                throw new Error('Failed to fetch results');
            }
        } catch (error) {
            console.error('View details error:', error);
            this.showToast('error', 'View Failed', 'Failed to load result details.');
        }
    }

    showResultsModal(csvText) {
        // Parse CSV text to show in a modal
        const lines = csvText.split('\n').filter(line => line.trim());
        const headers = lines[0].split(',').map(h => h.replace(/"/g, ''));
        const rows = lines.slice(1).map(line => {
            // Simple CSV parsing (handles quoted fields)
            const cols = [];
            let current = '';
            let inQuotes = false;
            
            for (let i = 0; i < line.length; i++) {
                const char = line[i];
                if (char === '"') {
                    inQuotes = !inQuotes;
                } else if (char === ',' && !inQuotes) {
                    cols.push(current.trim());
                    current = '';
                } else {
                    current += char;
                }
            }
            cols.push(current.trim());
            return cols;
        });

        // Create modal HTML
        const modalHtml = `
            <div class="modal-overlay" id="resultsModal">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3><i class="fas fa-table"></i> Classification Results</h3>
                        <button class="modal-close" onclick="document.getElementById('resultsModal').remove()">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="modal-body">
                        <div class="table-container">
                            <table class="results-table">
                                <thead>
                                    <tr>
                                        ${headers.map(h => `<th>${h}</th>`).join('')}
                                    </tr>
                                </thead>
                                <tbody>
                                    ${rows.map(row => `
                                        <tr>
                                            ${row.map(cell => `<td>${cell.replace(/"/g, '')}</td>`).join('')}
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                        <div class="modal-footer">
                            <button class="btn btn-primary" onclick="document.getElementById('resultsModal').remove()">
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        this.showToast('success', 'Results Loaded', `Showing ${rows.length} classified log entries.`);
    }

    // Progress Handling
    showProgress() {
        const progressSection = document.getElementById('progressSection');
        const resultsSection = document.getElementById('resultsSection');
        
        resultsSection.style.display = 'none';
        progressSection.style.display = 'block';
        progressSection.classList.add('slide-up');

        // Initialize progress at 0
        this.updateProgress(0, 'Initializing...');
    }

    updateProgress(percent, message) {
        const progressFill = document.getElementById('progressFill');
        const progressPercent = document.getElementById('progressPercent');
        const progressDetails = document.getElementById('progressDetails');
        
        if (progressFill) progressFill.style.width = `${percent}%`;
        if (progressPercent) progressPercent.textContent = `${percent}%`;
        if (progressDetails) progressDetails.textContent = message;
    }

    simulateProgress() {
        const progressFill = document.getElementById('progressFill');
        const progressPercent = document.getElementById('progressPercent');
        const progressDetails = document.getElementById('progressDetails');
        
        let progress = 0;
        const steps = [
            'Validating file format...',
            'Loading classification models...',
            'Processing log entries...',
            'Applying classification rules...',
            'Generating results...',
            'Finalizing output...'
        ];
        
        const interval = setInterval(() => {
            progress += Math.random() * 15 + 5;
            if (progress > 100) progress = 100;
            
            progressFill.style.width = `${progress}%`;
            progressPercent.textContent = `${Math.round(progress)}%`;
            
            const stepIndex = Math.floor((progress / 100) * steps.length);
            if (stepIndex < steps.length) {
                progressDetails.textContent = steps[stepIndex];
            }
            
            if (progress >= 100) {
                clearInterval(interval);
                setTimeout(() => {
                    this.hideProgress();
                }, 500);
            }
        }, 200);
    }

    hideProgress() {
        const progressSection = document.getElementById('progressSection');
        progressSection.style.display = 'none';
    }

    // Results Display
    showResults(data) {
        try {
            console.log('showResults called with data:', data);
            console.log('Data type:', typeof data);
            console.log('Data structure:', JSON.stringify(data, null, 2));
            console.log('classified_logs:', data.classified_logs);
            console.log('classified_logs type:', typeof data.classified_logs);
            console.log('classified_logs length:', Array.isArray(data.classified_logs) ? data.classified_logs.length : 'not an array');
            
            // Store classification results for dashboard
            this.lastClassificationResults = data;
            
            const resultsSection = document.getElementById('resultsSection');
            const resultsSummary = document.getElementById('resultsSummary');
            
            console.log('resultsSection element:', resultsSection);
            console.log('resultsSummary element:', resultsSummary);
            
            if (!resultsSection) {
                console.error('resultsSection element not found!');
                return;
            }
            
            if (!resultsSummary) {
                console.error('resultsSummary element not found!');
                return;
            }
            
            this.hideProgress();
            
            // Create summary
            console.log('Creating results summary...');
            const summary = this.createResultsSummary(data);
            resultsSummary.innerHTML = summary;
            console.log('Summary created and set');
            
            // Display classified logs table
            console.log('About to call displayClassifiedLogs with:', data.classified_logs || []);
            this.displayClassifiedLogs(data.classified_logs || []);
            
            // Show results section with emphasis
            resultsSection.style.display = 'block';
            resultsSection.classList.add('slide-up');
            console.log('Results section displayed');
            
            // Scroll to results section for better visibility
            setTimeout(() => {
                resultsSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 300);
            
            // Create chart
            console.log('Creating results chart...');
            this.createResultsChart(data.classification_stats);
            console.log('Chart created');
            
            console.log('Results section should now be visible'); // Debug log
        } catch (error) {
            console.error('Error in showResults:', error);
            console.error('Error stack:', error.stack);
        }
    }

    // Classified Logs Table Management
    displayClassifiedLogs(classifiedLogs) {
        try {
            console.log('displayClassifiedLogs called with:', classifiedLogs);
            console.log('classifiedLogs type:', typeof classifiedLogs);
            console.log('classifiedLogs is array:', Array.isArray(classifiedLogs));
            console.log('classifiedLogs length:', classifiedLogs ? classifiedLogs.length : 'null/undefined');
            
            if (!classifiedLogs || classifiedLogs.length === 0) {
                console.log('No classified logs to display - exiting early');
                return;
            }
            
            console.log('First log sample:', classifiedLogs[0]);
            
            // Store logs for filtering and pagination
            this.allClassifiedLogs = classifiedLogs;
            this.filteredLogs = [...classifiedLogs];
            this.currentPage = 1;
            this.logsPerPage = 50;
            
            // Show the classified logs section
            const logsSection = document.getElementById('classifiedLogsSection');
            console.log('classifiedLogsSection element:', logsSection);
            
            if (logsSection) {
                logsSection.style.display = 'block';
                console.log('classifiedLogsSection display set to block');
            } else {
                console.error('classifiedLogsSection element not found!');
                return;
            }
            
            // Populate filter dropdown with unique labels
            console.log('Populating label filter...');
            this.populateLabelFilter(classifiedLogs);
            
            // Set up search and filter event listeners
            console.log('Setting up table event listeners...');
            this.setupTableEventListeners();
            
            // Render the table
            console.log('About to render logs table');
            this.renderLogsTable();
            console.log('Logs table rendered');
        } catch (error) {
            console.error('Error in displayClassifiedLogs:', error);
            console.error('Error stack:', error.stack);
        }
    }
    
    populateLabelFilter(logs) {
        const labelFilter = document.getElementById('labelFilter');
        const uniqueLabels = [...new Set(logs.map(log => log.target_label))].sort();
        
        // Clear existing options except "All Categories"
        labelFilter.innerHTML = '<option value="">All Categories</option>';
        
        // Add unique labels
        uniqueLabels.forEach(label => {
            const option = document.createElement('option');
            option.value = label;
            option.textContent = label;
            labelFilter.appendChild(option);
        });
    }
    
    setupTableEventListeners() {
        const searchInput = document.getElementById('logSearchInput');
        const labelFilter = document.getElementById('labelFilter');
        
        // Search functionality
        let searchTimeout;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.filterLogs();
            }, 300);
        });
        
        // Filter functionality
        labelFilter.addEventListener('change', () => {
            this.filterLogs();
        });
    }
    
    filterLogs() {
        const searchTerm = document.getElementById('logSearchInput').value.toLowerCase();
        const selectedLabel = document.getElementById('labelFilter').value;
        
        this.filteredLogs = this.allClassifiedLogs.filter(log => {
            const matchesSearch = !searchTerm || 
                log.source.toLowerCase().includes(searchTerm) ||
                log.log_message.toLowerCase().includes(searchTerm) ||
                log.target_label.toLowerCase().includes(searchTerm);
                
            const matchesLabel = !selectedLabel || log.target_label === selectedLabel;
            
            return matchesSearch && matchesLabel;
        });
        
        this.currentPage = 1;
        this.renderLogsTable();
    }
    
    renderLogsTable() {
        const tableBody = document.getElementById('classifiedLogsTableBody');
        const startIndex = (this.currentPage - 1) * this.logsPerPage;
        const endIndex = startIndex + this.logsPerPage;
        const pageData = this.filteredLogs.slice(startIndex, endIndex);
        
        // Clear existing content
        tableBody.innerHTML = '';
        
        // Render rows
        pageData.forEach((log, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="source-cell">${this.escapeHtml(log.source)}</td>
                <td class="message-cell">${this.escapeHtml(log.log_message)}</td>
                <td class="label-cell">
                    <span class="classification-badge ${this.getBadgeClass(log.target_label)}">
                        ${this.escapeHtml(log.target_label)}
                    </span>
                </td>
            `;
            tableBody.appendChild(row);
        });
        
        // Update pagination
        this.updatePagination();
    }
    
    updatePagination() {
        const totalPages = Math.ceil(this.filteredLogs.length / this.logsPerPage);
        const paginationDiv = document.getElementById('tablePagination');
        
        if (totalPages <= 1) {
            paginationDiv.style.display = 'none';
            return;
        }
        
        paginationDiv.style.display = 'flex';
        
        const startRecord = ((this.currentPage - 1) * this.logsPerPage) + 1;
        const endRecord = Math.min(this.currentPage * this.logsPerPage, this.filteredLogs.length);
        
        paginationDiv.innerHTML = `
            <button class="pagination-btn" ${this.currentPage === 1 ? 'disabled' : ''} 
                    onclick="window.logClassifierApp.goToPage(${this.currentPage - 1})">
                <i class="fas fa-chevron-left"></i> Previous
            </button>
            <span class="pagination-info">
                Showing ${startRecord}-${endRecord} of ${this.filteredLogs.length} logs
            </span>
            <button class="pagination-btn" ${this.currentPage === totalPages ? 'disabled' : ''} 
                    onclick="window.logClassifierApp.goToPage(${this.currentPage + 1})">
                Next <i class="fas fa-chevron-right"></i>
            </button>
        `;
    }
    
    goToPage(page) {
        const totalPages = Math.ceil(this.filteredLogs.length / this.logsPerPage);
        if (page >= 1 && page <= totalPages) {
            this.currentPage = page;
            this.renderLogsTable();
        }
    }
    
    getBadgeClass(label) {
        const lower = label.toLowerCase();
        if (lower.includes('security') || lower.includes('alert')) return 'badge-security';
        if (lower.includes('user') || lower.includes('login')) return 'badge-user';
        if (lower.includes('workflow') || lower.includes('error')) return 'badge-workflow';
        if (lower.includes('system') || lower.includes('notification')) return 'badge-system';
        return 'badge-default';
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    createResultsSummary(data) {
        // API response structure: data.total_logs, data.processing_time_seconds, data.classification_stats
        try {
            const classificationStats = data.classification_stats || {};
            const processingTimeMs = Math.round((data.processing_time_seconds || 0) * 1000);
            const totalLogs = data.total_logs || 0;
            const labelCounts = classificationStats.label_counts || {};
            const categoriesCount = Object.keys(labelCounts).length;
            
            return `
                <div class="summary-item">
                    <h4>${totalLogs}</h4>
                    <p>Total Logs</p>
                </div>
                <div class="summary-item">
                    <h4>${processingTimeMs}ms</h4>
                    <p>Processing Time</p>
                </div>
                <div class="summary-item">
                    <h4>${categoriesCount}</h4>
                    <p>Categories Found</p>
                </div>
                <div class="summary-item">
                    <h4>Auto</h4>
                    <p>Method Used</p>
                </div>
            `;
        } catch (error) {
            console.error('Error creating results summary:', error);
            return `
                <div class="summary-item">
                    <h4>Error</h4>
                    <p>Unable to display results</p>
                </div>
            `;
        }
    }

    createResultsChart(statistics) {
        const ctx = document.getElementById('resultsChart');
        
        if (this.charts.results) {
            this.charts.results.destroy();
        }
        
        try {
            const labelCounts = statistics.label_counts || {};
            const labels = Object.keys(labelCounts);
            const values = Object.values(labelCounts);
            
            // Only create chart if we have data
            if (labels.length === 0) {
                ctx.getContext('2d').clearRect(0, 0, ctx.width, ctx.height);
                return;
            }
            
            this.charts.results = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: values,
                        backgroundColor: [
                            '#ef4444',
                            '#2563eb',
                            '#f59e0b',
                            '#10b981',
                            '#64748b'
                        ]
                    }]
                },
                plugins: [{
                    id: 'datalabels',
                    afterDatasetsDraw: function(chart) {
                        const ctx = chart.ctx;
                        chart.data.datasets.forEach((dataset, datasetIndex) => {
                            const meta = chart.getDatasetMeta(datasetIndex);
                            const total = dataset.data.reduce((sum, value) => sum + value, 0);
                            
                            meta.data.forEach((element, index) => {
                                const value = dataset.data[index];
                                const percentage = (value / total) * 100;
                                
                                // Only show numbers on slices that are at least 5% of the pie
                                // and have a value > 0
                                if (value > 0 && percentage >= 5) {
                                    ctx.fillStyle = '#ffffff';
                                    ctx.font = 'bold 14px Arial';
                                    ctx.textAlign = 'center';
                                    ctx.textBaseline = 'middle';
                                    
                                    const position = element.tooltipPosition();
                                    ctx.fillText(value, position.x, position.y);
                                }
                            });
                        });
                    }
                }],
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 10,
                                usePointStyle: true,
                                font: {
                                    size: 12
                                }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.parsed || 0;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return `${label}: ${value} (${percentage}%)`;
                                }
                            }
                        }
                    },
                    layout: {
                        padding: {
                            top: 10,
                            bottom: 10
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Error creating results chart:', error);
        }
    }

    // Dashboard
    async loadDashboard() {
        try {
            // Use performance stats endpoint for better dashboard data
            const response = await fetch(`${this.apiV1BaseUrl}/performance/stats/`);
            const data = await response.json();
            
            if (response.ok) {
                this.updateDashboardStats(data);
            }
        } catch (error) {
            console.error('Dashboard load error:', error);
            // Fallback to health endpoint if performance stats fails
            try {
                const fallbackResponse = await fetch(`${this.apiV1BaseUrl}/health/`);
                const fallbackData = await fallbackResponse.json();
                if (fallbackResponse.ok) {
                    this.updateDashboardStats(fallbackData);
                }
            } catch (fallbackError) {
                console.error('Dashboard fallback error:', fallbackError);
            }
        }
    }

    updateDashboardStats(data) {
        console.log('Updating dashboard with data:', data);
        
        // Handle both performance stats and health endpoint data structures
        const perfData = data.performance || {};
        const cacheData = data.cache || data.cache_stats || {};
        const statsData = data.statistics || {};
        const perfStats = perfData.performance_stats || {};
        const functionStats = perfStats.function_stats || {};
        
        // Calculate total processed from function call counts
        let totalProcessed = 0;
        let totalProcessingTime = 0;
        let callCount = 0;
        
        // Sum up classification calls
        if (functionStats.classify_logs_endpoint) {
            totalProcessed = functionStats.classify_logs_endpoint.call_count || 0;
            totalProcessingTime = functionStats.classify_logs_endpoint.avg_time || 0;
        }
        
        // Calculate cache hit rate from cache data
        let cacheHitRate = 0;
        if (cacheData.memory_cache) {
            const utilization = cacheData.memory_cache.utilization || 0;
            cacheHitRate = Math.min(utilization * 10, 100); // Rough approximation
        }
        
        // Update stat cards
        document.getElementById('totalProcessed').textContent = 
            totalProcessed || statsData.total_processed || '0';
        document.getElementById('avgProcessingTime').textContent = 
            `${Math.round((totalProcessingTime * 1000) || statsData.avg_processing_time || 0)}ms`;
        document.getElementById('cacheHitRate').textContent = 
            `${Math.round(cacheHitRate)}%`;
        
        // Fix system status - get from health data or performance monitoring status
        let systemStatus = 'Unknown';
        if (data.status === 'healthy') {
            systemStatus = 'Healthy';
        } else if (perfData.monitoring_active !== undefined) {
            systemStatus = perfData.monitoring_active ? 'Monitoring' : 'Active';
        } else if (data.components) {
            // Check if all components are healthy
            const componentStatuses = Object.values(data.components);
            systemStatus = componentStatuses.every(status => status === 'healthy' || status === 'available') ? 'Healthy' : 'Issues';
        }
        
        document.getElementById('systemStatus').textContent = systemStatus;
        
        // Create charts if data available
        if (perfData || statsData || data.statistics) {
            this.createDashboardCharts(data);
        }
    }

    createDashboardCharts(data) {
        // Extract real performance data
        const perfData = data.performance || {};
        const perfStats = perfData.performance_stats || {};
        const functionStats = perfStats.function_stats || {};
        
        // Performance chart with meaningful real data
        const perfCtx = document.getElementById('performanceChart');
        if (this.charts.performance) {
            this.charts.performance.destroy();
        }
        
        // Create performance metrics chart focusing on current session data
        const perfTimes = [];
        const perfLabels = [];
        const perfColors = [];
        const borderColors = [];
        
        if (functionStats.classify_logs_endpoint) {
            const stats = functionStats.classify_logs_endpoint;
            const avgTime = (stats.avg_time * 1000) || 0; // Convert to ms
            const minTime = (stats.min_time * 1000) || 0;
            const maxTime = (stats.max_time * 1000) || 0;
            const callCount = stats.call_count || 0;
            
            // Show current session metrics - what's actually happening now
            if (callCount > 0) {
                perfLabels.push('Requests Processed');
                perfTimes.push(callCount);
                perfColors.push('#3b82f6'); // Blue
                borderColors.push('#2563eb');
            }
            
            if (avgTime > 0) {
                perfLabels.push('Avg Response (ms)');
                perfTimes.push(avgTime);
                perfColors.push('#10b981'); // Green
                borderColors.push('#059669');
            }
            
            // Calculate efficiency metrics
            if (callCount > 0 && stats.total_time > 0) {
                const throughput = callCount / stats.total_time; // requests per second
                perfLabels.push('Throughput (req/sec)');
                perfTimes.push(Math.round(throughput * 100) / 100); // Round to 2 decimals
                perfColors.push('#f59e0b'); // Orange
                borderColors.push('#d97706');
            }
            
            // Show current system efficiency based on success rate
            if (callCount > 0) {
                const errorCount = stats.error_count || 0;
                const successRate = Math.round(((callCount - errorCount) / callCount) * 100);
                perfLabels.push('Success Rate (%)');
                perfTimes.push(successRate);
                perfColors.push('#8b5cf6'); // Purple
                borderColors.push('#7c3aed');
            }
            
        } else {
            // No data available
            perfLabels.push('No Activity Yet');
            perfTimes.push(0);
            perfColors.push('#e5e7eb'); // Light gray
            borderColors.push('#d1d5db');
        }
        
        this.charts.performance = new Chart(perfCtx, {
            type: 'bar',
            data: {
                labels: perfLabels,
                datasets: [{
                    label: 'Current Session Metrics',
                    data: perfTimes,
                    backgroundColor: perfColors,
                    borderColor: borderColors,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Value (context varies by metric)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            afterLabel: function(context) {
                                if (context.label.includes('Requests')) {
                                    return 'Number of files classified';
                                } else if (context.label.includes('Response')) {
                                    return 'Average processing time';
                                } else if (context.label.includes('Throughput')) {
                                    return 'Classifications per second';
                                } else if (context.label.includes('Success Rate')) {
                                    return 'Percentage of successful requests';
                                }
                                return 'Current session data';
                            }
                        }
                    }
                }
            }
        });
        
        // Historical Performance Chart - showing accumulated metrics over time
        const histCtx = document.getElementById('historicalChart');
        if (this.charts.historical) {
            this.charts.historical.destroy();
        }
        
        // Create historical metrics from all function stats
        const histLabels = [];
        const histTimes = [];
        const histColors = [];
        const histBorderColors = [];
        
        if (functionStats && Object.keys(functionStats).length > 0) {
            Object.entries(functionStats).forEach(([funcName, stats]) => {
                if (stats.call_count > 0) {
                    // Add meaningful function names and their historical averages
                    let displayName = funcName;
                    switch(funcName) {
                        case 'classify_logs_endpoint':
                            displayName = 'Main Classification';
                            break;
                        case 'classify_with_bert':
                            displayName = 'BERT Model';
                            break;
                        case 'classify_with_regex':
                            displayName = 'Regex Processor';
                            break;
                        case 'classify_with_llm':
                            displayName = 'LLM Processor';
                            break;
                        case 'get_bert_embeddings':
                            displayName = 'BERT Embeddings';
                            break;
                        case 'load_models':
                            displayName = 'Model Loading';
                            break;
                        default:
                            displayName = funcName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                    }
                    
                    histLabels.push(displayName);
                    histTimes.push((stats.avg_time * 1000) || 0); // Convert to ms
                    
                    // Color code by performance level
                    const avgTimeMs = (stats.avg_time * 1000) || 0;
                    if (avgTimeMs < 50) {
                        histColors.push('#10b981'); // Green - fast
                        histBorderColors.push('#059669');
                    } else if (avgTimeMs < 200) {
                        histColors.push('#f59e0b'); // Orange - medium
                        histBorderColors.push('#d97706');
                    } else {
                        histColors.push('#ef4444'); // Red - slow
                        histBorderColors.push('#dc2626');
                    }
                }
            });
        }
        
        if (histLabels.length === 0) {
            histLabels.push('No Historical Data');
            histTimes.push(0);
            histColors.push('#e5e7eb');
            histBorderColors.push('#d1d5db');
        }
        
        this.charts.historical = new Chart(histCtx, {
            type: 'bar',
            data: {
                labels: histLabels,
                datasets: [{
                    label: 'Historical Average Response Time (ms)',
                    data: histTimes,
                    backgroundColor: histColors,
                    borderColor: histBorderColors,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Response Time (ms)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            afterLabel: function(context) {
                                const functionStats = perfStats.function_stats || {};
                                const funcData = Object.values(functionStats).find(stat => 
                                    ((stat.avg_time * 1000) || 0).toFixed(1) == context.parsed.y.toFixed(1)
                                );
                                
                                if (funcData) {
                                    return [
                                        `Total calls: ${funcData.call_count}`,
                                        `Min time: ${((funcData.min_time * 1000) || 0).toFixed(1)}ms`,
                                        `Max time: ${((funcData.max_time * 1000) || 0).toFixed(1)}ms`,
                                        `Errors: ${funcData.error_count || 0}`
                                    ];
                                }
                                return 'Historical performance data';
                            }
                        }
                    }
                }
            }
        });
        
        // Distribution chart with real classification data
        const distCtx = document.getElementById('distributionChart');
        if (this.charts.distribution) {
            this.charts.distribution.destroy();
        }
        
        // Get real classification distribution data
        let distributionData = {};
        let labels = [];
        let values = [];
        let colors = [];
        
        if (this.lastClassificationResults && this.lastClassificationResults.classified_logs) {
            // Count each classification category using the correct field name
            this.lastClassificationResults.classified_logs.forEach(log => {
                const category = log.target_label || log.classification || 'Unclassified';
                distributionData[category] = (distributionData[category] || 0) + 1;
            });
            
            console.log('Distribution data:', distributionData);
            
            // Simple, robust color assignment - one unique color per category
            const uniqueColors = [
                '#e74c3c', '#3498db', '#f39c12', '#2ecc71', '#9b59b6',
                '#e67e22', '#1abc9c', '#34495e', '#f1c40f', '#8e44ad',
                '#c0392b', '#2980b9', '#d35400', '#27ae60', '#7f8c8d',
                '#16a085', '#2c3e50', '#f39800', '#8b5a2b', '#ff6b9d'
            ];
            
            console.log('Categories found:', Object.keys(distributionData));
            
            // Assign colors sequentially - each category gets the next color in line
            let colorIndex = 0;
            Object.entries(distributionData).forEach(([category, count]) => {
                labels.push(category);
                values.push(count);
                
                const color = uniqueColors[colorIndex % uniqueColors.length];
                colors.push(color);
                
                console.log(`Category "${category}": ${count} logs, color: ${color}`);
                colorIndex++;
            });
        }
        
        // Fallback to sample data if no classification results
        if (labels.length === 0) {
            labels = ['No Data Available'];
            values = [1];
            colors = ['#e5e7eb'];
        }
        
        this.charts.distribution = new Chart(distCtx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: colors
                }]
            },
            plugins: [{
                id: 'datalabels',
                afterDatasetsDraw: function(chart) {
                    const ctx = chart.ctx;
                    chart.data.datasets.forEach((dataset, datasetIndex) => {
                        const meta = chart.getDatasetMeta(datasetIndex);
                        const total = dataset.data.reduce((sum, value) => sum + value, 0);
                        
                        meta.data.forEach((element, index) => {
                            const value = dataset.data[index];
                            const percentage = (value / total) * 100;
                            
                            // Only show numbers on slices that are at least 5% of the pie
                            // and have a value > 0
                            if (value > 0 && percentage >= 5) {
                                ctx.fillStyle = '#ffffff';
                                ctx.font = 'bold 14px Arial';
                                ctx.textAlign = 'center';
                                ctx.textBaseline = 'middle';
                                
                                const position = element.tooltipPosition();
                                ctx.fillText(value, position.x, position.y);
                            }
                        });
                    });
                }
            }],
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom'
                    }
                }
            }
        });
    }

    // API Testing
    async testApiEndpoint(endpoint) {
        const responseArea = document.getElementById(`response-${endpoint}`);
        responseArea.innerHTML = '<div class="loading">Testing...</div>';

        try {
            let response;
            
            switch (endpoint) {
                case 'health':
                    response = await fetch(`${this.apiV1BaseUrl}/health/`);
                    break;
                case 'classify':
                    const file1 = document.getElementById('apiTestFile1').files[0];
                    if (!file1) {
                        responseArea.innerHTML = '<div class="error">Please select a file first</div>';
                        return;
                    }
                    const formData1 = new FormData();
                    formData1.append('file', file1);
                    response = await fetch(`${this.apiV1BaseUrl}/classify/`, {
                        method: 'POST',
                        body: formData1
                    });
                    break;
                case 'validate':
                    const file2 = document.getElementById('apiTestFile2').files[0];
                    if (!file2) {
                        responseArea.innerHTML = '<div class="error">Please select a file first</div>';
                        return;
                    }
                    const formData2 = new FormData();
                    formData2.append('file', file2);
                    response = await fetch(`${this.apiV1BaseUrl}/validate/`, {
                        method: 'POST',
                        body: formData2
                    });
                    break;
            }
            
            const data = await response.json();
            responseArea.innerHTML = `
                <div class="response-status ${response.ok ? 'success' : 'error'}">
                    Status: ${response.status} ${response.statusText}
                </div>
                <pre>${JSON.stringify(data, null, 2)}</pre>
            `;
        } catch (error) {
            responseArea.innerHTML = `<div class="error">Error: ${error.message}</div>`;
        }
    }

    // Toast Notifications
    showToast(type, title, message) {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        
        const iconMap = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle'
        };
        
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div class="toast-icon">
                <i class="fas ${iconMap[type]}"></i>
            </div>
            <div class="toast-content">
                <div class="toast-title">${title}</div>
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // Add close functionality
        toast.querySelector('.toast-close').addEventListener('click', () => {
            toast.remove();
        });
        
        container.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.logClassifierApp = new LogClassifierApp();
});

// Add some utility functions
window.downloadSampleCSV = function() {
    const sampleData = `source,log_message
WebServer,"ERROR: Database connection failed"
Application,"INFO: User login successful for user@example.com"
System,"WARNING: High memory usage detected: 85%"
Security,"ALERT: Failed login attempt from IP 192.168.1.100"
Database,"ERROR: Query timeout after 30 seconds"
API,"INFO: Request processed successfully in 120ms"`;
    
    const blob = new Blob([sampleData], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sample_logs.csv';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
};
