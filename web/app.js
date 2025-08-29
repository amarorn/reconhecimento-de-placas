// Sistema MBST - Interface Web Avançada
// ======================================

class MBSTSystem {
    constructor() {
        this.apiBase = 'http://localhost:8000';
        this.currentImages = [];
        this.analysisResults = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadStats();
        this.checkAPIStatus();
    }

    setupEventListeners() {
        // Upload area
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');

        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
        uploadArea.addEventListener('drop', this.handleDrop.bind(this));
        fileInput.addEventListener('change', this.handleFileSelect.bind(this));

        // Advanced analysis buttons
        document.getElementById('yoloBtn').addEventListener('click', this.runYOLODetection.bind(this));
        document.getElementById('ocrBtn').addEventListener('click', this.runOCRAnalysis.bind(this));

        // Feedback system
        document.getElementById('feedbackBtn').addEventListener('click', this.showFeedbackModal.bind(this));
        document.getElementById('closeFeedbackModal').addEventListener('click', this.hideFeedbackModal.bind(this));
        document.getElementById('feedbackForm').addEventListener('submit', this.submitFeedback.bind(this));
        document.getElementById('suggestionBtn').addEventListener('click', this.showSuggestionModal.bind(this));
    }

    async checkAPIStatus() {
        try {
            const response = await fetch(`${this.apiBase}/health`);
            const data = await response.json();
            
            const statusBtn = document.getElementById('statusBtn');
            if (data.status === 'healthy') {
                statusBtn.className = 'bg-green-500 hover:bg-green-600 px-4 py-2 rounded-lg transition-colors';
                statusBtn.innerHTML = '<i class="fas fa-circle text-xs mr-2"></i>Online';
            } else {
                statusBtn.className = 'bg-red-500 hover:bg-red-600 px-4 py-2 rounded-lg transition-colors';
                statusBtn.innerHTML = '<i class="fas fa-circle text-xs mr-2"></i>Offline';
            }
        } catch (error) {
            console.error('Erro ao verificar status da API:', error);
            const statusBtn = document.getElementById('statusBtn');
            statusBtn.className = 'bg-red-500 hover:bg-red-600 px-4 py-2 rounded-lg transition-colors';
            statusBtn.innerHTML = '<i class="fas fa-circle text-xs mr-2"></i>Erro';
        }
    }

    async loadStats() {
        try {
            const response = await fetch(`${this.apiBase}/stats`);
            const stats = await response.json();
            
            document.getElementById('totalPlacas').textContent = stats.total_placas;
            document.getElementById('regulamentacao').textContent = stats.por_tipo.regulamentacao || 0;
            document.getElementById('advertencia').textContent = stats.por_tipo.advertencia || 0;
        } catch (error) {
            console.error('Erro ao carregar estatísticas:', error);
        }
    }

    handleDragOver(e) {
        e.preventDefault();
        e.currentTarget.classList.add('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('dragover');
        
        const files = Array.from(e.dataTransfer.files);
        this.processFiles(files);
    }

    handleFileSelect(e) {
        const files = Array.from(e.target.files);
        this.processFiles(files);
    }

    processFiles(files) {
        const imageFiles = files.filter(file => file.type.startsWith('image/'));
        
        if (imageFiles.length === 0) {
            this.showNotification('Por favor, selecione apenas arquivos de imagem.', 'error');
            return;
        }

        this.currentImages = imageFiles;
        this.showUploadProgress();
        this.analyzeImages(imageFiles);
    }

    showUploadProgress() {
        const progressSection = document.getElementById('uploadProgress');
        progressSection.classList.remove('hidden');
        
        // Simular progresso
        let progress = 0;
        const progressBar = document.getElementById('progressBar');
        const progressPercent = document.getElementById('progressPercent');
        
        const interval = setInterval(() => {
            progress += 10;
            progressBar.style.width = `${progress}%`;
            progressPercent.textContent = `${progress}%`;
            
            if (progress >= 100) {
                clearInterval(interval);
                setTimeout(() => {
                    progressSection.classList.add('hidden');
                }, 1000);
            }
        }, 200);
    }

    async analyzeImages(images) {
        this.analysisResults = [];
        
        for (let i = 0; i < images.length; i++) {
            const image = images[i];
            const result = await this.analyzeSingleImage(image);
            this.analysisResults.push(result);
        }

        this.displayResults();
        this.updateProcessedCount();
    }

    async analyzeSingleImage(image) {
        // Simular análise da imagem
        const result = {
            filename: image.name,
            size: this.formatFileSize(image.size),
            type: image.type,
            analysis: {
                detection: this.simulateDetection(),
                classification: this.simulateClassification(),
                ocr: this.simulateOCR(),
                confidence: Math.random() * 0.3 + 0.7 // 70-100%
            }
        };

        return result;
    }

    simulateDetection() {
        const detections = [
            { type: 'placa', confidence: 0.95, bbox: [100, 150, 300, 200] },
            { type: 'texto', confidence: 0.87, bbox: [120, 170, 280, 190] }
        ];
        return detections;
    }

    simulateClassification() {
        const types = ['regulamentacao', 'advertencia', 'informacao'];
        const randomType = types[Math.floor(Math.random() * types.length)];
        
        return {
            type: randomType,
            code: randomType === 'regulamentacao' ? 'R-' + Math.floor(Math.random() * 50) : 'A-' + Math.floor(Math.random() * 50),
            confidence: Math.random() * 0.3 + 0.7
        };
    }

    simulateOCR() {
        const texts = ['PARE', 'DÊ A PREFERÊNCIA', 'VELOCIDADE MÁXIMA', 'PROIBIDO ESTACIONAR'];
        const randomText = texts[Math.floor(Math.random() * texts.length)];
        
        return {
            text: randomText,
            confidence: Math.random() * 0.3 + 0.7
        };
    }

    displayResults() {
        const resultsSection = document.getElementById('resultsSection');
        const resultsContainer = document.getElementById('resultsContainer');
        
        resultsSection.classList.remove('hidden');
        resultsContainer.innerHTML = '';

        this.analysisResults.forEach((result, index) => {
            const resultCard = this.createResultCard(result, index);
            resultsContainer.appendChild(resultCard);
        });
    }

    createResultCard(result, index) {
        const card = document.createElement('div');
        card.className = 'bg-gray-50 rounded-lg p-6 border border-gray-200';
        
        card.innerHTML = `
            <div class="flex items-start justify-between mb-4">
                <div>
                    <h4 class="text-lg font-semibold text-gray-900">${result.filename}</h4>
                    <p class="text-sm text-gray-600">${result.size} • ${result.type}</p>
                </div>
                <div class="flex space-x-2">
                    <span class="px-2 py-1 text-xs font-medium rounded-full ${
                        result.analysis.confidence > 0.9 ? 'bg-green-100 text-green-800' :
                        result.analysis.confidence > 0.7 ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                    }">
                        ${Math.round(result.analysis.confidence * 100)}% Confiança
                    </span>
                </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="bg-white p-4 rounded-lg border">
                    <h5 class="font-medium text-gray-900 mb-2">
                        <i class="fas fa-eye text-blue-600 mr-2"></i>Detecção
                    </h5>
                    <div class="space-y-2">
                        ${result.analysis.detection.map(d => `
                            <div class="text-sm">
                                <span class="font-medium">${d.type}:</span>
                                <span class="text-gray-600">${Math.round(d.confidence * 100)}%</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                <div class="bg-white p-4 rounded-lg border">
                    <h5 class="font-medium text-gray-900 mb-2">
                        <i class="fas fa-tag text-green-600 mr-2"></i>Classificação
                    </h5>
                    <div class="text-sm">
                        <div><span class="font-medium">Tipo:</span> <span class="text-gray-600">${result.analysis.classification.type}</span></div>
                        <div><span class="font-medium">Código:</span> <span class="text-gray-600">${result.analysis.classification.code}</span></div>
                        <div><span class="font-medium">Confiança:</span> <span class="text-gray-600">${Math.round(result.analysis.classification.confidence * 100)}%</span></div>
                    </div>
                </div>
                
                <div class="bg-white p-4 rounded-lg border">
                    <h5 class="font-medium text-gray-900 mb-2">
                        <i class="fas fa-font text-purple-600 mr-2"></i>OCR
                    </h5>
                    <div class="text-sm">
                        <div><span class="font-medium">Texto:</span> <span class="text-gray-600">${result.analysis.ocr.text}</span></div>
                        <div><span class="font-medium">Confiança:</span> <span class="text-gray-600">${Math.round(result.analysis.ocr.confidence * 100)}%</span></div>
                    </div>
                </div>
            </div>
            
            <div class="mt-4 flex space-x-3">
                <button onclick="mbstSystem.correctClassification(${index})" class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm">
                    <i class="fas fa-edit mr-1"></i>Corrigir
                </button>
                <button onclick="mbstSystem.downloadResult(${index})" class="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm">
                    <i class="fas fa-download mr-1"></i>Download
                </button>
                <button onclick="mbstSystem.shareResult(${index})" class="bg-purple-600 hover:bg-purple-700 text-white px-3 py-1 rounded text-sm">
                    <i class="fas fa-share mr-1"></i>Compartilhar
                </button>
            </div>
        `;
        
        return card;
    }

    updateProcessedCount() {
        const currentCount = parseInt(document.getElementById('processadas').textContent);
        document.getElementById('processadas').textContent = currentCount + this.currentImages.length;
    }

    async runYOLODetection() {
        if (this.currentImages.length === 0) {
            this.showNotification('Por favor, faça upload de imagens primeiro.', 'warning');
            return;
        }

        this.showNotification('Executando detecção YOLO...', 'info');
        
        // Simular processamento YOLO
        setTimeout(() => {
            this.showNotification('Detecção YOLO concluída!', 'success');
            this.refreshResults();
        }, 3000);
    }

    async runOCRAnalysis() {
        if (this.currentImages.length === 0) {
            this.showNotification('Por favor, faça upload de imagens primeiro.', 'warning');
            return;
        }

        this.showNotification('Executando análise OCR...', 'info');
        
        // Simular processamento OCR
        setTimeout(() => {
            this.showNotification('Análise OCR concluída!', 'success');
            this.refreshResults();
        }, 2000);
    }

    refreshResults() {
        this.displayResults();
    }

    correctClassification(index) {
        this.showNotification(`Corrigindo classificação da imagem ${index + 1}...`, 'info');
        // Implementar correção de classificação
    }

    downloadResult(index) {
        const result = this.analysisResults[index];
        const dataStr = JSON.stringify(result, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `${result.filename}_analysis.json`;
        link.click();
        
        this.showNotification('Resultado baixado com sucesso!', 'success');
    }

    shareResult(index) {
        const result = this.analysisResults[index];
        const shareText = `Análise da placa ${result.filename}: ${result.analysis.classification.type} - ${result.analysis.ocr.text}`;
        
        if (navigator.share) {
            navigator.share({
                title: 'Análise MBST',
                text: shareText
            });
        } else {
            navigator.clipboard.writeText(shareText);
            this.showNotification('Resultado copiado para a área de transferência!', 'success');
        }
    }

    showFeedbackModal() {
        document.getElementById('feedbackModal').classList.remove('hidden');
    }

    hideFeedbackModal() {
        document.getElementById('feedbackModal').classList.add('hidden');
    }

    async submitFeedback(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const feedback = {
            type: formData.get('type') || 'Classificação Incorreta',
            description: formData.get('description') || '',
            timestamp: new Date().toISOString(),
            imageCount: this.currentImages.length
        };

        // Simular envio de feedback
        this.showNotification('Feedback enviado com sucesso!', 'success');
        this.hideFeedbackModal();
        
        // Limpar formulário
        e.target.reset();
    }

    showSuggestionModal() {
        this.showNotification('Funcionalidade de sugestões em desenvolvimento!', 'info');
    }

    showNotification(message, type = 'info') {
        // Criar notificação
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 transform transition-all duration-300 translate-x-full`;
        
        const colors = {
            success: 'bg-green-500 text-white',
            error: 'bg-red-500 text-white',
            warning: 'bg-yellow-500 text-white',
            info: 'bg-blue-500 text-white'
        };
        
        notification.className += ` ${colors[type]}`;
        notification.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-${type === 'success' ? 'check' : type === 'error' ? 'times' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'} mr-2"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Animar entrada
        setTimeout(() => {
            notification.classList.remove('translate-x-full');
        }, 100);
        
        // Remover após 5 segundos
        setTimeout(() => {
            notification.classList.add('translate-x-full');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 5000);
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Inicializar sistema quando a página carregar
document.addEventListener('DOMContentLoaded', () => {
    window.mbstSystem = new MBSTSystem();
});

// Atualizar estatísticas a cada 30 segundos
setInterval(() => {
    if (window.mbstSystem) {
        window.mbstSystem.loadStats();
        window.mbstSystem.checkAPIStatus();
    }
}, 30000);
